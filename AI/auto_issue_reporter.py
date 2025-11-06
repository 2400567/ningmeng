#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动问题上报模块 (本地 + 占位符外部AI: 通义 API)

功能:
1. 捕获运行期异常（函数包装 / 手动调用）
2. 结构化标准化错误信息 (时间戳、类型、消息、trace、上下文)
3. 写入本地 JSON Lines 文件: error_reports/error_log.jsonl 方便审计
4. 可选: 若设置环境变量 AUTO_AI_REPORT=1 则尝试调用 send_to_ai() 函数
5. send_to_ai() 目前为占位符：检测 TONGYI_API_KEY 是否存在，若不存在仅本地记录
6. 去重: 相同 (错误类型 + 位置 + 第一行trace) 15分钟内重复不重复发送

后续扩展建议:
- 增加异步队列 & 批量发送
- 增加敏感字段脱敏策略（如手机号/邮箱）
- 增加“建议修复”缓存避免重复调用外部模型
"""
from __future__ import annotations
import os
import json
import traceback
import datetime as _dt
from pathlib import Path
from typing import Any, Callable, Dict, Optional, List
import threading
import hashlib
import time

try:
    import requests  # 轻量 HTTP 客户端
except Exception:  # 若环境未装 requests，后续调用将自动降级
    requests = None  # type: ignore

REPORT_DIR = Path(__file__).parent / "error_reports"
REPORT_DIR.mkdir(exist_ok=True)
REPORT_FILE = REPORT_DIR / "error_log.jsonl"
STATE_CACHE_FILE = REPORT_DIR / "sent_cache.json"

_LOCK = threading.Lock()

class AutoIssueReporter:
    """自动错误捕获与上报 (带通义AI诊断集成)"""
    dedup_window_minutes = 15

    # ---- 外部AI调用配置 (可通过环境变量覆盖) ----
    ai_timeout = int(os.getenv('TONGYI_API_TIMEOUT', '15'))
    ai_retries = int(os.getenv('TONGYI_API_RETRIES', '2'))
    ai_model = os.getenv('TONGYI_MODEL', 'qwen-turbo')
    # 兼容 OpenAI 接口模式（DashScope 提供兼容端点）或官方老端点
    ai_endpoint = os.getenv(
        'TONGYI_API_URL',
        # 优先尝试兼容模式（OpenAI 风格）
        'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
    )
    # 最大 trace 发送行数，避免上传过长内容
    max_trace_lines = int(os.getenv('TONGYI_TRACE_LINES', '25'))
    # 是否只发送摘要而非完整 trace
    partial_trace = os.getenv('TONGYI_PARTIAL_TRACE', '1') == '1'

    @classmethod
    def _load_sent_cache(cls) -> Dict[str, str]:
        if STATE_CACHE_FILE.exists():
            try:
                return json.loads(STATE_CACHE_FILE.read_text(encoding='utf-8'))
            except Exception:
                return {}
        return {}

    @classmethod
    def _save_sent_cache(cls, cache: Dict[str, str]):
        try:
            STATE_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception:
            pass

    @classmethod
    def _hash_signature(cls, err_type: str, location: str, first_tb_line: str) -> str:
        raw = f"{err_type}|{location}|{first_tb_line}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    @classmethod
    def _dedup_ok(cls, signature: str) -> bool:
        cache = cls._load_sent_cache()
        now = _dt.datetime.utcnow()
        if signature in cache:
            try:
                ts = _dt.datetime.fromisoformat(cache[signature])
                if (now - ts) < _dt.timedelta(minutes=cls.dedup_window_minutes):
                    return False
            except Exception:
                pass
        cache[signature] = now.isoformat()
        cls._save_sent_cache(cache)
        return True

    @classmethod
    def capture_exception(cls, section: str, e: Exception, extra_context: Optional[Dict[str, Any]] = None):
        tb = traceback.format_exc()
        tb_lines = tb.splitlines()
        first_line = tb_lines[-1] if tb_lines else ''
        location = ''
        for line in tb_lines:
            if 'enhanced_app.py' in line or 'auto_issue_reporter' in line:
                location = line.strip()
        err_record = {
            'timestamp_utc': _dt.datetime.utcnow().isoformat(),
            'section': section,
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': tb,
            'location_hint': location,
            'context': cls._sanitize_context(extra_context or {}),
        }
        signature = cls._hash_signature(err_record['error_type'], err_record['location_hint'], first_line)
        with _LOCK:
            with REPORT_FILE.open('a', encoding='utf-8') as f:
                f.write(json.dumps(err_record, ensure_ascii=False) + '\n')
        # 条件外部上报
        if os.environ.get('AUTO_AI_REPORT', '0') == '1' and cls._dedup_ok(signature):
            cls._attempt_external_ai(err_record)
        return err_record

    @classmethod
    def _sanitize_context(cls, ctx: Dict[str, Any]) -> Dict[str, Any]:
        redacted_keys = {'password','token','secret','api_key'}
        safe = {}
        for k, v in ctx.items():
            if any(word in k.lower() for word in redacted_keys):
                safe[k] = '***REDACTED***'
            else:
                try:
                    json.dumps(v)  # test serializable
                    safe[k] = v
                except Exception:
                    safe[k] = str(v)
        return safe

    @classmethod
    def _attempt_external_ai(cls, record: Dict[str, Any]):
        """调用通义(或兼容)模型获取诊断建议.

        调用条件:
        - 环境变量 TONGYI_API_KEY 存在
        - requests 可用
        - 失败自动重试 (ai_retries)

        失败降级: 写入 placeholder 建议，不抛异常。
        """
        api_key = os.environ.get('TONGYI_API_KEY')
        if not api_key or requests is None:
            return  # 无密钥或无requests直接跳过

        # 构造压缩 trace
        tb = record.get('traceback', '') or ''
        trace_lines = tb.splitlines()
        if cls.partial_trace and len(trace_lines) > cls.max_trace_lines:
            head = trace_lines[: cls.max_trace_lines]
            tb_compact = '\n'.join(head) + f"\n... (truncated {len(trace_lines)-cls.max_trace_lines} lines)"
        else:
            tb_compact = tb

        prompt = cls._build_prompt(record, tb_compact)
        payload = {
            'model': cls.ai_model,
            'messages': [
                {'role': 'system', 'content': '你是资深Python错误诊断助手，请输出简明可执行的修复建议，必要时给出代码片段。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'top_p': 0.9,
        }
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        suggestion_text = None
        last_error = None
        for attempt in range(1, cls.ai_retries + 2):  # 初次 + 重试次数
            try:
                resp = requests.post(
                    cls.ai_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=cls.ai_timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    # 兼容 OpenAI-style 返回
                    suggestion_text = cls._extract_message(data)
                    if suggestion_text:
                        break
                    else:
                        last_error = 'empty_content'
                else:
                    last_error = f"status_{resp.status_code}"
            except Exception as e:  # 网络/超时
                last_error = f"exception:{type(e).__name__}:{e}"
            # 退避等待
            time.sleep(min(2 ** (attempt - 1), 5))

        if not suggestion_text:
            suggestion_text = f"(调用失败: {last_error or 'unknown'}) 占位: 建议查看错误类型 {record.get('error_type')} 与上下文。"  # 回退

        # 写入建议文件
        suggestion_file = REPORT_DIR / 'ai_suggestions.jsonl'
        ai_entry = {
            'timestamp_utc': _dt.datetime.utcnow().isoformat(),
            'error_type': record.get('error_type'),
            'section': record.get('section'),
            'model': cls.ai_model,
            'endpoint': cls.ai_endpoint,
            'suggestion': suggestion_text,
        }
        with _LOCK:
            with suggestion_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(ai_entry, ensure_ascii=False) + '\n')

    @classmethod
    def _build_prompt(cls, record: Dict[str, Any], tb_compact: str) -> str:
        return (
            "请分析以下后端运行错误并给出: (1) 问题根因推断 (2) 立即可尝试的修复步骤 (3) 如果涉及数据/状态, 给出验证建议。\n"
            f"Section: {record.get('section')}\n"
            f"ErrorType: {record.get('error_type')}\n"
            f"Message: {record.get('error_message')}\n"
            f"LocationHint: {record.get('location_hint')}\n"
            f"Context: {json.dumps(record.get('context') or {}, ensure_ascii=False)[:800]}\n"
            "Traceback (可能被截断):\n" + tb_compact
        )

    @classmethod
    def _extract_message(cls, data: Dict[str, Any]) -> Optional[str]:
        # OpenAI style: choices[0].message.content
        try:
            choices = data.get('choices')
            if isinstance(choices, list) and choices:
                msg = choices[0].get('message')
                if isinstance(msg, dict):
                    content = msg.get('content')
                    if isinstance(content, str) and content.strip():
                        return content.strip()
        except Exception:
            return None
        # 兼容其他格式: data['output']['text'] 或 data['text']
        for key in ('output', 'text', 'result'):
            if key in data:
                val = data[key]
                if isinstance(val, dict) and 'text' in val:
                    return str(val['text']).strip()
                if isinstance(val, str):
                    return val.strip()
        return None

    @classmethod
    def run_with_capture(cls, func: Callable[[], Any], section: str, context_provider: Optional[Callable[[], Dict[str, Any]]] = None):
        try:
            return func()
        except Exception as e:  # noqa: BLE001
            ctx = {}
            if context_provider:
                try:
                    ctx = context_provider() or {}
                except Exception:
                    ctx = {'context_error': 'failed to collect'}
            cls.capture_exception(section, e, ctx)
            # 重新抛出以便前端仍然显示错误
            raise

# 便捷装饰器
def ai_error_guard(section: str):
    def deco(fn: Callable):
        def wrapper(*a, **kw):
            return AutoIssueReporter.run_with_capture(lambda: fn(*a, **kw), section,
                                                      context_provider=lambda: {'args': a, 'kwargs': kw})
        return wrapper
    return deco

__all__ = [
    'AutoIssueReporter',
    'ai_error_guard'
]

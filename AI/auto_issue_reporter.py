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
from typing import Any, Callable, Dict, Optional
import threading
import hashlib

REPORT_DIR = Path(__file__).parent / "error_reports"
REPORT_DIR.mkdir(exist_ok=True)
REPORT_FILE = REPORT_DIR / "error_log.jsonl"
STATE_CACHE_FILE = REPORT_DIR / "sent_cache.json"

_LOCK = threading.Lock()

class AutoIssueReporter:
    """自动错误捕获与上报"""
    dedup_window_minutes = 15

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
        # 占位: 通义 API 调用逻辑
        api_key = os.environ.get('TONGYI_API_KEY')
        if not api_key:
            # 没有密钥，跳过外部发送
            return
        # 这里保留可扩展结构；实际调用需接入正式SDK或HTTP.
        # 示例(伪代码):
        # response = requests.post(url, headers={'Authorization': f'Bearer {api_key}'}, json={'error': record})
        # 保存AI建议
        suggestion_file = REPORT_DIR / 'ai_suggestions.jsonl'
        ai_placeholder = {
            'error_type': record['error_type'],
            'section': record['section'],
            'suggestion': '占位: 此处应返回通义大模型的诊断与修复建议。',
        }
        with _LOCK:
            with suggestion_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(ai_placeholder, ensure_ascii=False) + '\n')

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

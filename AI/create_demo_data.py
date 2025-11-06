#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建UTAUT2问卷演示数据
包含标准的题项结构，用于测试题项变量映射功能
"""

import pandas as pd
import numpy as np

# 设置随机种子
np.random.seed(42)

# 定义问卷题项
questions = {
    # 绩效期望 (Performance Expectancy)
    'Q1_我认为AI虚拟主播能提高购物效率': '绩效期望',
    'Q2_AI虚拟主播让我更快找到想要的商品': '绩效期望', 
    'Q3_使用AI虚拟主播购物对我很有用': '绩效期望',
    'Q4_AI虚拟主播提高了我的购物体验质量': '绩效期望',
    
    # 努力期望 (Effort Expectancy)
    'Q5_学习使用AI虚拟主播对我来说很容易': '努力期望',
    'Q6_我的操作技能足以使用AI虚拟主播': '努力期望',
    'Q7_学习使用AI虚拟主播很简单': '努力期望',
    'Q8_我能够快速掌握AI虚拟主播的使用方法': '努力期望',
    
    # 社会影响 (Social Influence)  
    'Q9_我周围的人认为我应该使用AI虚拟主播': '社会影响',
    'Q10_对我重要的人认为我应该使用AI虚拟主播': '社会影响',
    'Q11_我的朋友们鼓励我使用AI虚拟主播': '社会影响',
    'Q12_使用AI虚拟主播符合当前的流行趋势': '社会影响',
    
    # 促进条件 (Facilitating Conditions)
    'Q13_我有必要的资源使用AI虚拟主播': '促进条件',
    'Q14_我有必要的知识使用AI虚拟主播': '促进条件', 
    'Q15_AI虚拟主播与我使用的其他技术兼容': '促进条件',
    'Q16_当我遇到困难时，能够得到他人帮助': '促进条件',
    
    # 享乐动机 (Hedonic Motivation)
    'Q17_使用AI虚拟主播很有趣': '享乐动机',
    'Q18_使用AI虚拟主播很愉快': '享乐动机',
    'Q19_使用AI虚拟主播很有娱乐性': '享乐动机',
    
    # 价值认知 (Price Value)
    'Q20_AI虚拟主播购物的价格是合理的': '价值认知',
    'Q21_AI虚拟主播提供了良好的性价比': '价值认知',
    'Q22_使用AI虚拟主播购物是值得的': '价值认知',
    
    # 技术信任 (Technology Trust)
    'Q23_我信任AI虚拟主播提供的商品信息': '技术信任',
    'Q24_我相信AI虚拟主播的推荐是可靠的': '技术信任',
    'Q25_AI虚拟主播的建议值得信赖': '技术信任',
    
    # 感知风险 (Perceived Risk)
    'Q26_使用AI虚拟主播购物存在一定风险': '感知风险',
    'Q27_我担心AI虚拟主播可能提供错误信息': '感知风险',
    
    # 个体创新 (Personal Innovation)
    'Q28_我喜欢尝试新的购物方式': '个体创新',
    'Q29_我通常是最早尝试新技术的人之一': '个体创新',
    'Q30_我对新技术有强烈的好奇心': '个体创新',
    
    # 消费意愿 (Purchase Intention)
    'Q31_我打算继续使用AI虚拟主播购物': '消费意愿',
    'Q32_我会向他人推荐AI虚拟主播购物': '消费意愿',
    'Q33_我有强烈的意愿使用AI虚拟主播': '消费意愿',
    'Q34_我计划在未来增加使用AI虚拟主播的频率': '消费意愿',
    
    # 消费行为 (Purchase Behavior)
    'Q35_我经常通过AI虚拟主播购买商品': '消费行为',
    'Q36_我会根据AI虚拟主播的推荐做购买决定': '消费行为',
    'Q37_AI虚拟主播已成为我购物的重要渠道': '消费行为'
}

# 生成演示数据
n_samples = 300  # 样本数量

# 创建基础数据框
data = {}

# 添加基本信息
data['答题序号'] = range(1, n_samples + 1)
data['来源'] = np.random.choice(['微信', '问卷星', '腾讯问卷'], n_samples)

# 添加人口统计学变量
data['性别'] = np.random.choice(['男', '女'], n_samples, p=[0.45, 0.55])
data['年龄'] = np.random.choice(['18-25岁', '26-35岁', '36-45岁', '46-55岁', '55岁以上'], 
                              n_samples, p=[0.3, 0.35, 0.2, 0.1, 0.05])
data['学历'] = np.random.choice(['高中及以下', '专科', '本科', '硕士', '博士'], 
                             n_samples, p=[0.1, 0.15, 0.6, 0.13, 0.02])
data['职业'] = np.random.choice(['学生', '上班族', '自由职业', '退休', '其他'], 
                             n_samples, p=[0.25, 0.5, 0.15, 0.05, 0.05])

# 为每个问卷题项生成数据
for question, construct in questions.items():
    # 基于构念生成不同的分布
    if construct in ['绩效期望', '努力期望', '消费意愿']:
        # 这些构念通常得分较高
        scores = np.random.choice([3, 4, 5], n_samples, p=[0.2, 0.4, 0.4])
    elif construct in ['感知风险']:
        # 感知风险得分通常较低
        scores = np.random.choice([1, 2, 3], n_samples, p=[0.3, 0.4, 0.3])
    else:
        # 其他构念正态分布
        scores = np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1])
    
    data[question] = scores

# 创建数据框
df = pd.DataFrame(data)

# 保存为CSV文件
output_file = 'utaut2_demo_data.csv'
df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ 演示数据已生成: {output_file}")
print(f"📊 数据规模: {len(df)} 行 × {len(df.columns)} 列")
print(f"🎯 包含构念: {len(set(questions.values()))} 个")
print(f"📝 包含题项: {len([q for q in questions.keys()])} 个")

# 显示数据预览
print("\n📋 数据预览:")
print(df.head())

# 显示构念分布
print("\n🏗️ 构念题项分布:")
construct_counts = {}
for question, construct in questions.items():
    if construct not in construct_counts:
        construct_counts[construct] = 0
    construct_counts[construct] += 1

for construct, count in construct_counts.items():
    print(f"  {construct}: {count} 个题项")

print(f"\n🎉 演示数据生成完成！可以用于测试题项变量映射功能。")
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 设置随机种子确保结果可重现
np.random.seed(42)

# 创建测试数据集
n_samples = 500

# 生成基础数据
data = {
    # 人口统计学变量
    'ID': range(1, n_samples + 1),
    '性别': np.random.choice(['男', '女'], n_samples, p=[0.45, 0.55]),
    '年龄': np.random.normal(35, 12, n_samples).astype(int),
    '教育水平': np.random.choice(['高中以下', '高中', '大专', '本科', '研究生'], 
                                n_samples, p=[0.15, 0.25, 0.25, 0.25, 0.1]),
    '收入水平': np.random.choice(['低', '中', '高'], n_samples, p=[0.3, 0.5, 0.2]),
    
    # 心理量表数据 (Likert 1-5)
    '生活满意度1': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.05, 0.15, 0.35, 0.35, 0.1]),
    '生活满意度2': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.05, 0.15, 0.35, 0.35, 0.1]),
    '生活满意度3': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.05, 0.15, 0.35, 0.35, 0.1]),
    '工作满意度1': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
    '工作满意度2': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
    '工作满意度3': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.3, 0.3, 0.1]),
    
    # 反向题（故意设计与其他题目负相关）
    '压力水平1': 6 - np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1]),
    '焦虑水平1': 6 - np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.2, 0.4, 0.2, 0.1]),
    
    # 多选题数据 (0/1编码)
    '兴趣爱好_运动': np.random.choice([0, 1], n_samples, p=[0.4, 0.6]),
    '兴趣爱好_阅读': np.random.choice([0, 1], n_samples, p=[0.5, 0.5]),
    '兴趣爱好_音乐': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
    '兴趣爱好_旅游': np.random.choice([0, 1], n_samples, p=[0.6, 0.4]),
    '兴趣爱好_美食': np.random.choice([0, 1], n_samples, p=[0.2, 0.8]),
    
    # 连续变量
    '身高': np.random.normal(165, 10, n_samples),
    '体重': np.random.normal(65, 15, n_samples),
    '月收入': np.random.exponential(5000, n_samples) + 3000,
    
    # 时间序列数据
    '测量时间': [datetime(2023, 1, 1) + timedelta(days=i) for i in range(n_samples)],
    
    # 分组变量（用于t检验和方差分析）
    '实验组': np.random.choice(['对照组', '实验组'], n_samples, p=[0.5, 0.5]),
    '地区': np.random.choice(['北方', '南方', '东部', '西部'], n_samples, p=[0.25, 0.25, 0.25, 0.25]),
    
    # 二分类结果变量（用于逻辑回归）
    '是否满意': np.random.choice(['是', '否'], n_samples, p=[0.7, 0.3]),
}

# 创建DataFrame
df = pd.DataFrame(data)

# 添加一些相关性
# 让生活满意度各题目相关
life_base = np.random.normal(3, 1, n_samples)
df['生活满意度1'] = np.clip(life_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)
df['生活满意度2'] = np.clip(life_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)
df['生活满意度3'] = np.clip(life_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)

# 让工作满意度相关
work_base = np.random.normal(3, 1, n_samples)
df['工作满意度1'] = np.clip(work_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)
df['工作满意度2'] = np.clip(work_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)
df['工作满意度3'] = np.clip(work_base + np.random.normal(0, 0.3, n_samples), 1, 5).astype(int)

# BMI计算
df['BMI'] = df['体重'] / (df['身高'] / 100) ** 2

# 添加一些缺失值
missing_indices = np.random.choice(df.index, size=int(0.05 * len(df)), replace=False)
df.loc[missing_indices, '月收入'] = np.nan

missing_indices = np.random.choice(df.index, size=int(0.03 * len(df)), replace=False)
df.loc[missing_indices, '生活满意度3'] = np.nan

# 添加异常值
outlier_indices = np.random.choice(df.index, size=int(0.02 * len(df)), replace=False)
df.loc[outlier_indices, '月收入'] = df.loc[outlier_indices, '月收入'] * 10

# 保存数据
df.to_csv('/workspaces/ningmeng/AI/comprehensive_test_data.csv', index=False, encoding='utf-8')

print("✅ 综合测试数据集已创建")
print(f"📊 数据形状: {df.shape}")
print(f"📋 变量类型:")
print(f"   - 分类变量: {len(df.select_dtypes(include=['object']).columns)} 个")
print(f"   - 数值变量: {len(df.select_dtypes(include=['number']).columns)} 个")
print(f"   - 时间变量: {len(df.select_dtypes(include=['datetime']).columns)} 个")
print(f"🔍 数据质量:")
print(f"   - 缺失值: {df.isnull().sum().sum()} 个")
print(f"   - 重复行: {df.duplicated().sum()} 个")
print("\n📝 数据说明:")
print("- 包含心理量表题目（用于信度效度分析）")
print("- 包含多选题数据（用于多选题分析）")
print("- 包含分组变量（用于t检验和方差分析）")
print("- 包含连续变量（用于相关分析和回归）")
print("- 包含时间序列数据（用于趋势分析）")
print("- 包含缺失值和异常值（用于数据质量评估）")
"""
智能变量匹配和映射系统
用于解决模板变量与实际数据列名不匹配的问题
"""

def create_variable_mapping_suggestions(template_variables, data_columns):
    """
    创建变量映射建议
    
    Args:
        template_variables: 模板中的变量列表 
        data_columns: 数据中的列名列表
    
    Returns:
        dict: 映射建议 {template_var: [suggested_columns]}
    """
    import re
    from difflib import get_close_matches
    
    mapping_suggestions = {}
    
    for template_var in template_variables:
        suggestions = []
        template_var_lower = template_var.lower()
        
        # 1. 精确匹配（忽略大小写）
        for col in data_columns:
            if template_var_lower == col.lower():
                suggestions.append(col)
        
        # 2. 包含匹配
        if not suggestions:
            for col in data_columns:
                col_lower = col.lower()
                # 检查模板变量是否包含在列名中
                if template_var_lower in col_lower or col_lower in template_var_lower:
                    suggestions.append(col)
        
        # 3. Q1-Q50 特殊匹配
        if not suggestions and re.match(r'^[Qq]\d+$', template_var):
            q_num = re.findall(r'\d+', template_var)[0]
            for col in data_columns:
                if f"Q{q_num}_" in col or f"q{q_num}_" in col.lower():
                    suggestions.append(col)
        
        # 4. 模糊匹配
        if not suggestions:
            close_matches = get_close_matches(
                template_var_lower, 
                [col.lower() for col in data_columns], 
                n=3, 
                cutoff=0.6
            )
            for match in close_matches:
                # 找到原始列名
                original_col = next(col for col in data_columns if col.lower() == match)
                suggestions.append(original_col)
        
        mapping_suggestions[template_var] = suggestions[:5]  # 最多5个建议
    
    return mapping_suggestions

def analyze_variable_mismatch(template_variables, data_columns):
    """
    分析变量不匹配的情况并提供解决方案
    """
    missing_vars = []
    available_mappings = {}
    
    for var in template_variables:
        if var not in data_columns:
            missing_vars.append(var)
    
    if missing_vars:
        mapping_suggestions = create_variable_mapping_suggestions(missing_vars, data_columns)
        return {
            'has_mismatch': True,
            'missing_variables': missing_vars,
            'total_missing': len(missing_vars),
            'total_template': len(template_variables),
            'mapping_suggestions': mapping_suggestions,
            'data_columns': data_columns
        }
    else:
        return {
            'has_mismatch': False,
            'message': '所有变量都找到了匹配'
        }

def create_utaut2_standard_mapping():
    """
    创建UTAUT2模型的标准变量映射
    """
    return {
        # 基础UTAUT2构念
        'PE': ['感知有用性', '绩效期望', 'Performance_Expectancy'],
        'EE': ['感知易用性', '努力期望', 'Effort_Expectancy'], 
        'SI': ['社会影响', 'Social_Influence'],
        'FC': ['便利条件', 'Facilitating_Conditions'],
        'HM': ['享乐动机', 'Hedonic_Motivation'],
        'PV': ['价格价值', 'Price_Value'],
        'HB': ['习惯', 'Habit'],
        'BI': ['行为意图', 'Behavioral_Intention'],
        'UB': ['使用行为', 'Use_Behavior'],
        
        # 问卷编号映射
        'Q1': ['Q1_', 'Q01_'],
        'Q2': ['Q2_', 'Q02_'], 
        'Q3': ['Q3_', 'Q03_'],
        'Q4': ['Q4_', 'Q04_'],
        'Q5': ['Q5_', 'Q05_'],
        
        # 其他常见变量
        'VI2': ['虚拟交互', '虚拟互动', 'Virtual_Interaction'],
        'UTAUT2': ['UTAUT2模型', 'UTAUT2_Model']
    }

if __name__ == "__main__":
    # 测试函数
    template_vars = ['BI', 'Q1', 'Q2', 'PE', 'EE']
    data_cols = ['Q1_性别', 'Q2_年龄', 'Q3_学历', 'BI_行为意图', 'PE_感知有用性']
    
    result = analyze_variable_mismatch(template_vars, data_cols)
    print("变量匹配分析结果:")
    print(result)
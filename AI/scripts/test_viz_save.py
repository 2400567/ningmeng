import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.visualization.visualizer import DataVisualizer
import pandas as pd
import numpy as np
import os

def main():
    viz = DataVisualizer()
    # Create sample data
    x = np.arange(0, 10)
    y = x * 2 + np.random.randn(10)
    df = pd.DataFrame({'x': x, 'y': y})

    temp_dir = Path('temp/figures')
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Line chart
    fig_line = viz.create_line_chart(df, 'x', 'y', title='测试折线图')
    p_line = temp_dir / 'test_line.png'
    fig_line.savefig(p_line, dpi=150, bbox_inches='tight')
    print('Saved line to', p_line)

    # Scatter
    fig_scatter = viz.create_scatter_plot(df, 'x', 'y', title='测试散点图', trendline=True)
    p_sc = temp_dir / 'test_scatter.png'
    fig_scatter.savefig(p_sc, dpi=150, bbox_inches='tight')
    print('Saved scatter to', p_sc)

    # Heatmap using numeric columns
    df2 = pd.DataFrame(np.random.randn(10,4), columns=['a','b','c','d'])
    fig_heat = viz.create_heatmap(df2, title='测试热力图')
    p_heat = temp_dir / 'test_heat.png'
    fig_heat.savefig(p_heat, dpi=150, bbox_inches='tight')
    print('Saved heatmap to', p_heat)

if __name__ == '__main__':
    main()

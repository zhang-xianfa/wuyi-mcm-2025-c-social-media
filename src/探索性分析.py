# -*- coding: utf-8 -*-
"""
社交媒体互动数据时段分析系统
功能：分析用户在不同时段的互动行为模式
作者：Monica
日期：2025-05-02
"""

# 导入库
import pandas as pd  # 数据处理
import seaborn as sns  # 高级可视化
import matplotlib.pyplot as plt  # 基础绘图
from matplotlib.pylab import rcParams  # 图形参数配置
import os  # 文件路径操作

# 可视化全局参数设置
rcParams['figure.figsize'] = (16, 9)  # 设置默认图表尺寸
sns.set_style("darkgrid")  # 使用深色网格风格
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文显示问题

import pandas as pd

# -*- coding: utf-8 -*-
import pandas as pd
import re
from config import ATTACHMENT_1


def load_special_format(file_path):
    """
    特殊格式CSV文件加载器
    处理特征：
    1. 中文列名含特殊符号
    2. 时间字段含异常字符
    3. 逗号分隔符
    """
    try:
        # 处理带括号的时间格式
        date_parser = lambda x: pd.to_datetime(
            re.sub(r'[()]', '', x).strip(),  # 去除括号和空格
            format='%Y-%m-%d %H:%M:%S',
            errors='coerce'
        )

        df = pd.read_csv(
            file_path,
            sep=',',  # 明确指定逗号分隔
            header=0,
            parse_dates=['鏃堕棿 (Time)'],  # 保持原始列名
            date_parser=date_parser,
            encoding='gbk',
            engine='python'
        )

        # 列名标准化
        df.columns = ['用户ID', '用户行为', '博主ID', '时间']

        # 数据验证
        print("成功加载列：", df.columns.tolist())
        print("首行时间示例：", df['时间'].iloc[0])

        return df.dropna(subset=['时间'])

    except Exception as e:
        print(f"加载失败：{str(e)}")
        # 文件内容诊断
        with open(file_path, 'r', encoding='gbk') as f:
            print("\n文件前两行实际内容：")
            print(f.readline())  # 列标题
            print(f.readline())  # 数据首行
        exit(1)



def load_and_preprocess(file_path):
    """
    数据加载与预处理模块
    参数：
        file_path : str 数据文件绝对路径
    返回：
        df_clean : DataFrame 清洗后的数据
    功能：
        1. 验证文件存在性
        2. 读取制表符分隔的CSV文件
        3. 处理时间字段和异常值
        4. 生成日期特征
    """
    try:
        # 检查文件存在性
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件路径错误: {file_path}")

        # 读取CSV文件（处理混合分隔符）
        df = pd.read_csv(
            file_path,
            sep='\t+',  # 正则表达式匹配不定长制表符
            engine='python',  # 启用正则解析引擎
            header=0,  # 使用首行为列名
            names=['用户ID', '用户行为', '博主ID', '时间'],  # 统一列名
            parse_dates=['时间'],  # 指定时间解析列
            date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M', errors='coerce'),  # 严格时间格式
            encoding='gbk'  # 处理中文编码
        )

        # ===== 数据质量检查 =====
        print(f"数据加载成功，共加载{len(df)}条记录")
        na_count = df[df['时间'].isna()].shape[0]
        print(f"发现时间异常记录：{na_count}条")

        # ===== 数据清洗 =====
        df_clean = df.dropna(subset=['时间']).reset_index(drop=True)  # 剔除无效时间记录

        # ===== 时间特征工程 =====
        # 提取日期部分（YYYY-MM-DD）
        df_clean['日期'] = df_clean['时间'].dt.date
        # 提取小时数值（0-23）
        df_clean['小时'] = df_clean['时间'].dt.hour
        # 生成中文星期名称（星期一~日）
        df_clean['星期'] = df_clean['时间'].dt.day_name(locale='zh_CN.UTF-8')

        return df_clean

    except Exception as e:
        print(f"数据加载失败: {str(e)}")
        exit(1)


def analyze_hourly_pattern(df):
    """
    时段分析引擎
    参数：
        df : DataFrame 预处理后的数据
    返回：
        pivot : DataFrame 日期×小时的互动量矩阵
        stats : dict 关键统计指标
    功能：
        1. 构建时间透视表
        2. 补全缺失日期
        3. 计算互动量指标
    """
    # ===== 生成时间透视表 =====
    pivot = df.pivot_table(
        index='日期',  # 行索引为日期
        columns='小时',  # 列索引为小时
        values='用户ID',  # 使用任意非空列计数
        aggfunc='count',  # 计数统计
        fill_value=0  # 缺失值补零
    )

    # ===== 日期连续性处理 =====
    # 生成完整日期序列（防止数据缺失日期）
    full_dates = pd.date_range(start=df['日期'].min(), end=df['日期'].max())
    # 重建索引保证日期连续
    pivot = pivot.reindex([d.date() for d in full_dates], fill_value=0)

    # ===== 统计指标计算 =====
    stats = {
        '总互动量': pivot.sum().sum(),  # 总互动次数
        '时段排名': pivot.sum().sort_values(ascending=False).index.tolist(),  # 时段热度排序
        '最高时段': pivot.sum().idxmax(),  # 最活跃小时
        '每日趋势': pivot.sum(axis=1).to_dict()  # 每日总互动量
    }
    return pivot, stats


def visualize_results(pivot, stats):
    """
    可视化模块
    参数：
        pivot : DataFrame 时间透视表
        stats : dict 统计指标
    功能：
        1. 生成热力图展示时空分布
        2. 保存高清图表
    """
    # ===== 时间标签生成 =====
    time_labels = [f"{h:02d}:00" for h in range(24)]  # 生成24小时制标签

    # ===== 热力图配置 =====
    plt.figure(figsize=(18, 10))  # 设置画布尺寸
    ax = sns.heatmap(
        pivot,  # 输入数据矩阵
        annot=True,  # 显示数值
        fmt="d",  # 整数格式
        cmap="YlGnBu",  # 颜色映射方案（黄-绿-蓝渐变）
        linewidths=0.5,  # 单元格边框粗细
        annot_kws={'size': 9},  # 标注字体大小
        cbar_kws={'label': '互动量'}  # 颜色条标签
    )

    # ===== 坐标轴优化 =====
    ax.set_xticks(range(24))  # 设置24个刻度
    ax.set_xticklabels(time_labels, rotation=45)  # 倾斜45度显示小时标签
    # 生成带星期的日期标签（MM-DD (周X)）
    date_labels = [d.strftime("%m-%d (%a)") for d in pivot.index]
    ax.set_yticklabels(date_labels, rotation=0)  # 垂直显示日期

    # ===== 标题与保存 =====
    plt.title(f'24小时互动热力图 | 总互动量: {stats["总互动量"]:,} | 峰值时段: {stats["最高时段"]}:00',
              pad=20, fontsize=14)  # 动态生成标题
    plt.xlabel('时段', labelpad=15)  # X轴标签
    plt.ylabel('日期', labelpad=15)  # Y轴标签
    plt.tight_layout()  # 自动调整布局
    plt.savefig('hourly_analysis.png', dpi=300, bbox_inches='tight')  # 保存高清图
    plt.show()


if __name__ == "__main__":
    """
    主程序执行流程
    步骤：
        1. 配置数据路径
        2. 加载清洗数据
        3. 执行时段分析
        4. 输出统计结果
        5. 生成可视化图表
    """
    # ===== 文件路径配置 =====
    data_path = ATTACHMENT_1  # 需修改为实际路径

    # ===== 执行分析流程 =====
    df = load_special_format(data_path)  # 加载数据
    pivot_table, stats = analyze_hourly_pattern(df)  # 时段分析

    # ===== 输出关键发现 =====
    print("\n【分析结论】")
    print(f"1. 峰值时段分布：{stats['最高时段']}时（互动量 {pivot_table[stats['最高时段']].sum()} 次）")
    print(f"2. Top3活跃时段：")
    for i, hour in enumerate(stats['时段排名'][:3]):
        print(f"   {i + 1}. {hour:02d}:00 时段，互动量 {pivot_table[hour].sum():,} 次")

    print("\n3. 每日活跃趋势：")
    for date, total in stats['每日趋势'].items():
        print(f"   {date.strftime('%m-%d')}: {total} 次")

    # ===== 生成可视化 =====
    visualize_results(pivot_table, stats)

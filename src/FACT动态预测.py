import pandas as pd
import numpy as np
from config import CREATOR_STATS

# 1. 数据加载
df = pd.read_csv(CREATOR_STATS, index_col=0, parse_dates=True, dayfirst=False)

# 2. 时间差计算（修复错误）
date_diff = pd.to_datetime(df.columns) - pd.to_datetime("2021-07-11")
days = date_diff.astype('timedelta64[D]').astype(int).values  # 正确获取天数

# 3. 时间衰减因子（修正逻辑）
decay = 0.85 ** (days.max() - days)  # 时间越近权重越高

# 4. 加权预测模型
def predict(row):
    valid_data = row[row > 0][-5:]  # 取最近5天非零数据
    weights = decay[-len(valid_data):]  # 动态权重匹配
    return np.dot(valid_data, weights/weights.sum())

# 5. 执行预测并输出
pred = df.apply(predict, axis=1).sort_values(ascending=False).head(5)
print("2024年7月21日预测Top5：")
print(pd.DataFrame({'博主ID': pred.index, '预测值': pred.round().astype(int)}).to_markdown(index=False))

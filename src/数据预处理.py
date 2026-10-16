import pandas as pd
from config import ATTACHMENT_1, CREATOR_STATS

# 数据加载与处理
df = (
    pd.read_csv(ATTACHMENT_1, usecols=[0,1,2,3])
    .rename(columns=lambda x: x.split(' ')[0])  # 简化列名
    .assign(
        时间=lambda x: pd.to_datetime(x['时间'].str.replace('：',':')),
        日期=lambda x: x['时间'].dt.date,
        观看=1,
        点赞=lambda x: x['用户行为']==2,
        评论=lambda x: x['用户行为']==3,
        关注=lambda x: x['用户行为']==4
    )
)

# 构建统计表
(
    df.groupby(['博主ID', '日期'])
    [['观看','点赞','评论','关注']].sum()
    .unstack(fill_value=0)
    .to_csv(CREATOR_STATS)
)

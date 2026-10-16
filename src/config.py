"""数据路径配置。

附件 1 / 附件 2 是竞赛官方提供的数据集，体积很大（附件 1 约 70 MB），
因此没有放进本仓库。请把两个 CSV 放到仓库根目录的 `data/` 下，
或者用环境变量 `MCM_DATA_DIR` 指向它们所在的目录。
"""

import os

# src/ 的上一级 = 仓库根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("MCM_DATA_DIR") or os.path.join(BASE_DIR, "data")

# 竞赛附件（需自行下载，见 README「数据」一节）
ATTACHMENT_1 = os.path.join(DATA_DIR, "附件1 (Attachment 1).csv")
ATTACHMENT_2 = os.path.join(DATA_DIR, "附件2 (Attachment 2).csv")

# 数据预处理脚本产出的中间文件
CREATOR_STATS = os.path.join(DATA_DIR, "博主行为统计.csv")

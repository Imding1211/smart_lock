
from datetime import datetime
from textwrap import dedent

import pandas as pd

#=============================================================================#

QA_file_path = "QandA.csv"

#=============================================================================#

def get_qa_info():

    df_qa = pd.read_csv(QA_file_path, encoding="utf-8")

    models = (
        df_qa["適用型號"]
        .dropna()
        .str.split(r"\s*,\s*")
        .explode()
        .unique()
        .tolist()
    )

    issues = (
    	df_qa['問題大類']
    	.dropna()
    	.unique()
    	.tolist()
    )

    return df_qa, models, issues

#-----------------------------------------------------------------------------#

def build_docs_from_df(df_input):

    docs = []

    for idx, row in df_input.iterrows():
        doc = dedent(f"""
適用型號：{row['適用型號']}
問題大類：{row['問題大類']}
客戶問題/意圖：{row['客戶問題/意圖']}
視覺或聲音特徵：{row['視覺或聲音特徵']}
前置條件：{row['前置條件']}
標準操作步驟：{row['標準操作步驟']}
師傅小撇步：{row['師傅小撇步']}
        """).lstrip()
    
        docs.append(doc)

    return docs

#-----------------------------------------------------------------------------#

def merge_last_field_unique(data):

    time   = set()
    seen   = set()
    result_time = []
    result      = []

    for item in reversed(data):
        timestamp = item[1]
        msg       = item[5]

        if msg not in seen and timestamp not in time:
            time.add(timestamp)
            seen.add(msg)
            result_time.append(f"{time_ago(int(timestamp))}:{msg}")
            result.append(msg)

    return result_time, result

#-----------------------------------------------------------------------------#

def time_ago(timestamp, unit="ms"):

    if unit == "ms":
        timestamp /= 1000

    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()

    seconds = int((now - dt).total_seconds())

    if seconds < 60:
        return f"{seconds}秒前"

    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}分{seconds}秒前"

    hours, minutes = divmod(minutes, 60)
    return f"{hours}小時{minutes}分前"

#=============================================================================#

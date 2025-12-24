
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

#=============================================================================#

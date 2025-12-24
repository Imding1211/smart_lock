
from tool import get_qa_info, build_docs_from_df

#=============================================================================#

def quer_qa(model, issue_category):

	df_qa, _, _ = get_qa_info()

	df_result = df_qa[
	    df_qa["適用型號"].str.contains(model, na=False) &
	    (df_qa["問題大類"] == issue_category)
	]

	info = build_docs_from_df(df_result)

	return info

#=============================================================================#

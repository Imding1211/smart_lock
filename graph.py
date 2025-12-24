
from llm import reply_user, evaluate_info_sufficiency
from doc_db import search_doc_db
from query import quer_qa

from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict, Literal

import operator

#=============================================================================#

class GraphState(TypedDict):
    fields   : dict
    question : list[str]
    context  : list[str]
    answer   : str
    history  : Annotated[list, operator.add]

#=============================================================================#

def retrieve_qa(state: GraphState):
    print("  [檢索雲端硬碟中...]")

    result = quer_qa(state['fields']['適用型號'], state['fields']['問題大類'])

    return {"context": result, "history": ["檢索雲端硬碟"]}

#-----------------------------------------------------------------------------#

def retrieve_doc(state: GraphState):
    print("  [檢索說明書中...]")

    result = search_doc_db(','.join(state['question']), state['fields']['適用型號'], 5)

    page_contents = [doc.page_content for doc in result]

    return {"context": page_contents, "history": ["檢索說明書"]}

#-----------------------------------------------------------------------------#

def generate_answer(state: GraphState):
    print("  [生成回覆中...]")

    resp = reply_user(state['question'], state['context'])

    return {"answer": resp, "history": ["生成回覆"]}

#-----------------------------------------------------------------------------#

def transfer_to_human(state: GraphState):
    print("  [無法回覆，轉交真人客服...]")

    resp = "您好\n麻煩您留下以下資訊\n聯絡地址：\n電話：\n安裝日期：\n另外再麻煩您錄影整個狀況的影片將其上傳，謝謝您"

    return {"answer": resp, "history": ["真人客服"]}

#-----------------------------------------------------------------------------#

def decide_sufficiency(state: GraphState) -> Literal["sufficient", "insufficient"]:
    print("  [判斷資訊是否足夠...]", end=" ")

    context  = state.get("context")
    question = state.get("question")

    if not context or not any(c.strip() for c in context):
        print("No (context empty)")
        return "insufficient"

    response = evaluate_info_sufficiency(question, context)

    normalized = response.strip().lower()

    if normalized.startswith("yes"):
        print("Yes")
        return "sufficient"

    print("No")
    return "insufficient"

#=============================================================================#

workflow = StateGraph(GraphState)

workflow.add_node("db_qa", retrieve_qa)
workflow.add_node("db_doc", retrieve_doc)
workflow.add_node("generate", generate_answer)
workflow.add_node("human", transfer_to_human)

#-----------------------------------------------------------------------------#

workflow.add_edge(START, "db_qa")
workflow.add_conditional_edges(
    "db_qa",
    decide_sufficiency,
    {"sufficient": "generate", "insufficient": "db_doc"}
)
workflow.add_conditional_edges(
    "db_doc",
    decide_sufficiency,
    {"sufficient": "generate", "insufficient": "human"}
)
workflow.add_edge("generate", END)
workflow.add_edge("human", END)

lock_ai = workflow.compile()

# print(lock_ai.get_graph().draw_ascii())

#=============================================================================#

def run_test():
    
    # 檢索雲端硬碟(O) -> 生成回覆
    # user_input = ['請問註冊鍵在哪？', '我的型號是AS850']
    # fields     = {'適用型號': 'AS850', '問題大類': '基本設定'}

    # 無法回答
    # user_input = ['今天吃什麼？']
    # fields     = {'適用型號': '無', '問題大類': '無'}

    # 檢索雲端硬碟(X) -> 檢索說明書(O) -> 生成回覆
    user_input = ['請問註冊鍵在哪？', '我的型號是AS901']
    fields     = {'適用型號': 'AS901', '問題大類': '基本設定'}

    # 檢索雲端硬碟(X) -> 檢索說明書(X) -> 真人客服
    # user_input = ['請問註冊鍵在哪？', 'A12345']
    # fields     = {'適用型號': 'A12345', '問題大類': '基本設定'}

    print(f"\n>>> 測試問題: {','.join(user_input)}")

    inputs = {
        "fields"   : fields,
        "question" : user_input,
        "context"  : "",
        "answer"   : "",
        "history"  : []
    }
    
    result = lock_ai.invoke(inputs)
    print(f"*** 最終結果 ***\n{result['answer']}\n路徑追蹤: {' -> '.join(result['history'])}")

    """
    for output in lock_ai.stream(inputs):
        for node_name, value in output.items():
            print(f"  └─ 節點【{node_name}】執行完畢")
    print(f"*** 最終結果 ***\n{value['answer']}")
    """
    
#=============================================================================#

if __name__ == '__main__':
    run_test()

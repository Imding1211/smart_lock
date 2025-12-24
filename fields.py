
from llm import extract_fields, ask_fields
from tool import get_qa_info

from pydantic import BaseModel, Field

#=============================================================================#

class Ticket(BaseModel):
    model: str          = Field(description="裝置型號")
    issue_category: str = Field(description="問題分類")

#=============================================================================#

def update_fields(item):

    fields = {
        "適用型號": item.model,
        "問題大類": item.issue_category
    }

    missing_fields = [k for k, v in fields.items() if v == "未提供"]

    if missing_fields:
        return fields, missing_fields, True

    else:
        return fields, missing_fields, False

#-----------------------------------------------------------------------------#

def get_fields(user_input, issues):

    resp = extract_fields(Ticket, user_input, issues)

    fields, missing_fields, is_missing = update_fields(resp)

    print(f"問題資訊:{fields}")
    print(f"缺失資訊:{missing_fields}")
    print(f"資訊完整:{is_missing}")

    return fields, missing_fields, is_missing

#-----------------------------------------------------------------------------#

def get_fields_process():

    _, _, issues = get_qa_info()

    user_input = []

    print('忘記管理者密碼了，請問怎麼更改？')

    user_input.append('忘記管理者密碼了，請問怎麼更改？')

    fields, missing_fields, is_missing = get_fields(user_input, issues)

    while is_missing:
        resp = ask_fields(user_input, missing_fields)

        print(resp)

        print('我的型號是AS850')

        user_input.append('我的型號是AS850')

        fields, missing_fields, is_missing = get_fields(user_input, issues)

#=============================================================================#

# if __name__ == '__main__':
    # get_fields_process()

    # _, _, issues = get_qa_info()

    # user_input = [
    #     HumanMessage(content='請問註冊鍵在哪？', additional_kwargs={}, response_metadata={}, id='5f347a44-2305-4fd0-a871-e6f1913a5867'), 
    #     AIMessage(content='您好！請問您使用的是哪一款智慧鎖呢？ 這樣我才能更精準地告訴您註冊鍵的位置喔！', additional_kwargs={}, response_metadata={'model': 'gemma3:4b', 'created_at': '2025-12-24T10:32:33.287521419Z', 'done': True, 'done_reason': 'stop', 'total_duration': 5792588306, 'load_duration': 4868938785, 'prompt_eval_count': 16, 'prompt_eval_duration': 81862297, 'eval_count': 79, 'eval_duration': 656617925, 'logprobs': None, 'model_name': 'gemma3:4b', 'model_provider': 'ollama'}, id='lc_run--019b4e3f-542c-72f1-a651-d4b91e6f422b-0', usage_metadata={'input_tokens': 16, 'output_tokens': 79, 'total_tokens': 95}), 
    #     HumanMessage(content='我的型號是AS901', additional_kwargs={}, response_metadata={}, id='02fad958-36b0-4d4c-b9ea-bdd95497464c')
    # ]

    # fields, missing_fields, is_missing = get_fields(user_input, issues)
    # print(fields, missing_fields, is_missingf)


from tool import build_docs_from_df
from query import quer_qa
from prompt import *

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

import instructor
import os

load_dotenv()

#=============================================================================#

instructor_model_name = "ollama/qwen3-vl:4b"
llm_model_name        = "gemma3:4b"

#=============================================================================#

instructor_model = instructor.from_provider(instructor_model_name)
# instructor_model = instructor.from_provider("google/gemini-2.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))

llm_model = ChatOllama(model=llm_model_name, temperature=0)
# llm_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

#=============================================================================#

def extract_fields(response_model, user_input, issues):

    prompt = struct_prompt_template.format(
        user_input = '\n'.join(user_input),
        issues     = ','.join(issues),
    )

    print(prompt)

    resp = instructor_model.create(
        response_model = response_model,
        messages       = [{"role": "user", "content": prompt}],
    )

    return resp

#-----------------------------------------------------------------------------#

def ask_fields(user_input, missing_fields):

    prompt = ask_prompt_template.format(
        user_input     = '\n'.join(user_input),
        missing_fields = ','.join(missing_fields),
    )

    # print(prompt)

    resp = llm_model.invoke([("user", prompt)])

    return resp.content

#-----------------------------------------------------------------------------#

def reply_user(user_input, context):

	prompt = reply_prompt_template.format(
	    info       = '\n'.join(context),
	    user_input = ','.join(user_input),
	)

	# print(prompt)

	resp = llm_model.invoke([("user", prompt)])

	return resp.content

#-----------------------------------------------------------------------------#

def evaluate_info_sufficiency(user_input, context):

	prompt = decide_prompt_template.format(
	    context  = '\n'.join(context),
	    question = ','.join(user_input),
	)

	# print(prompt)

	resp = llm_model.invoke([("user", prompt)])

	return resp.content.strip().upper()

#=============================================================================#

if __name__ == '__main__':
	
    user_input = ['請問註冊鍵在哪？', '我的型號是AS850']
    fields = {'適用型號': 'AS850', '問題大類': '基本設定'}
    resp = reply_user(user_input, fields)
    print(resp)

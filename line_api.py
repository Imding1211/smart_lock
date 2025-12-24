
from fields import get_fields
from drive import get_doc_url
from tool import get_qa_info
from llm import ask_fields
from graph import lock_ai
from message_db import *

from linebot.exceptions import InvalidSignatureError
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from dotenv import load_dotenv
from linebot.models import (
    TemplateSendMessage,
    TextSendMessage,
    ButtonsTemplate,
    MessageEvent,
    TextMessage,
    SourceGroup,
    SourceRoom,
    SourceUser,
    URIAction
)

import logging
import os

#=============================================================================#

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET       = os.environ.get("LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise ValueError("LINE_CHANNEL_ACCESS_TOKEN 和 LINE_CHANNEL_SECRET 必須在 .env 檔案中設定！")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler      = WebhookHandler(CHANNEL_SECRET)

df_qa, models, issues = get_qa_info()

app = FastAPI()

#=============================================================================#

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#=============================================================================#

def merge_last_field_unique(data):

    seen   = set()
    result = []

    for item in reversed(data):
        msg = item[-1]
        if msg not in seen:
            seen.add(msg)
            result.append(msg)

    return result

#-----------------------------------------------------------------------------#

def reply_line(event, messages):

    try:
        if not isinstance(messages, list):
            messages = [messages]

        line_bot_api.reply_message(event.reply_token, messages)

    except Exception as e:
        logger.error(f"回覆訊息失敗: {e}")

#-----------------------------------------------------------------------------#

@app.post("/callback")
async def callback(request: Request):
    
    signature = request.headers.get("X-Line-Signature", "")
    body      = await request.body()
    body_str  = body.decode("utf-8")

    try:
        handler.handle(body_str, signature)

    except InvalidSignatureError:
        logger.error("Invalid signature. Please check your channel access token/secret.")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    return "OK"

#-----------------------------------------------------------------------------#

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):

    received_text = event.message.text
    message_id    = event.message.id
    timestamp     = event.timestamp
    source        = event.source
    source_type   = source.type
    user_id       = None
    group_room_id = None
    
    if isinstance(source, SourceUser):
        user_id = source.user_id

    elif isinstance(source, SourceGroup):
        user_id = source.user_id
        group_room_id = source.group_id

    elif isinstance(source, SourceRoom):
        user_id = source.user_id
        group_room_id = source.room_id

    db_record = {
        "timestamp": timestamp,
        "message_id": message_id,
        "source_type": source_type,
        "user_id": user_id,
        "group_room_id": group_room_id,
        "message_content": received_text
    }
    
    insert_message_record(db_record)

    records = fetch_recent_records(user_id)

    user_input = merge_last_field_unique(records)

    fields, missing_fields, is_missing = get_fields(user_input, issues)

    if is_missing:
        reply_message = ask_fields(user_input, missing_fields)
        reply_line(event, TextSendMessage(text=reply_message))
        return

    lock_ai_inputs = {
        "fields": fields,
        "question": user_input,
        "context": "",
        "answer": "",
        "history": []
    }

    lock_ai_result = lock_ai.invoke(lock_ai_inputs)
    reply_message = lock_ai_result.get("answer", "")

    messages = [TextSendMessage(text=reply_message)]

    doc_info = get_doc_url(fields.get("適用型號"))

    if doc_info:
        info = doc_info[0]

        template_message = TemplateSendMessage(
            alt_text="產品使用說明書",
            template=ButtonsTemplate(
                title=f'{fields["適用型號"]} 使用說明書',
                text="請點擊下方按鈕查看完整操作說明",
                actions=[
                    URIAction(
                        label="點我開啟說明書",
                        uri=info["webViewLink"]
                    )
                ]
            )
        )

        messages.append(template_message)

    reply_line(event, messages)

    delete_records_by_user_id(user_id)

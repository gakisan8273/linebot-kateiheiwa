from curses.ascii import alt
import json
import os
import uuid

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (TemplateSendMessage, ButtonsTemplate, PostbackAction)
from linebot.exceptions import (LineBotApiError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# ステータス定義
STATUS_DICT = {
    'genki': {
        'score': 5,
        'label': '元気！',
    },
    'a_little_sindoi': {
        'score': 10,
        'label': 'なんとか',
    },
    'sindoi': {
        'score': 20,
        'label': 'しんどい',
    },
    'muri': {
        'score': 40,
        'label': 'もう無理',
    },
}

# LINE API最大試行数
MAX_ATTEMPTS = 3

def handler(event, context):
    postback_actions = []
    for status, item in STATUS_DICT.items():
        postback_actions.append(PostbackAction(data=item['score'], label=item['label'], text='> ' + item['label']))

    title = '今日もお仕事お疲れ様！'
    text = '体調はどうかな？'
    buttuns_template = ButtonsTemplate(text=text, title=title, actions=postback_actions)
    try:
        push_postback_message(os.environ['MY_LINE_USER_ID'], title, buttuns_template)
    except Exception as e:
        print('error', e)
        # TODO: レスポンスを変更する
        return

    body = {
        "message": "お疲れ様メッセージを送信しました。",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

# LINEメッセージを送信する
def push_postback_message(id: str, alt_text: str, buttuns_template: list[ButtonsTemplate]) -> bool:
    # 16進表記のUUID
    retry_key = str(uuid.uuid1())
    attempt_count = 1
    messages = TemplateSendMessage(alt_text=alt_text, template=buttuns_template)
    while attempt_count <= MAX_ATTEMPTS:
        try:
            line_bot_api.push_message(to=os.environ['MY_LINE_USER_ID'], messages=messages, retry_key=retry_key)
            return True
        except LineBotApiError as e:
            attempt_count = attempt_count + 1

    raise LineBotApiError

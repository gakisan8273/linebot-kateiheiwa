import json
import os

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (TemplateSendMessage, ButtonsTemplate, PostbackAction)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    status_dict = {
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
    postback_actions = []
    for status, item in status_dict.items():
        postback_actions.append(PostbackAction(data=item['score'], label=item['label'], text='> ' + item['label']))

    title = '今日もお仕事お疲れ様！'
    text = '体調はどうかな？'
    buttuns_template = ButtonsTemplate(text=text, title=title, actions=postback_actions)
    # TODO: 例外処理
    line_bot_api.push_message(os.environ['MY_LINE_USER_ID'], TemplateSendMessage(alt_text=title, template=buttuns_template))

    body = {
        "message": "お疲れ様メッセージを送信しました。",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

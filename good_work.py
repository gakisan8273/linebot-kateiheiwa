import json
import os
from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction, PostbackAction)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    status_map = {
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
    postback_actions = [
        PostbackAction(data=status_map['genki']['score'], label=status_map['genki']['label'], text='> ' + status_map['genki']['label']),
        PostbackAction(data=status_map['a_little_sindoi']['score'], label=status_map['a_little_sindoi']['label'], text='> ' + status_map['a_little_sindoi']['label']),
        PostbackAction(data=status_map['sindoi']['score'], label=status_map['sindoi']['label'], text='> ' + status_map['sindoi']['label']),
        PostbackAction(data=status_map['muri']['score'], label=status_map['muri']['label'], text='> ' + status_map['muri']['label']),
    ]
    title = '今日もお仕事お疲れ様！'
    text = '体調はどうかな？'
    buttuns_template = ButtonsTemplate(text=text, title=title, actions=postback_actions)
    line_bot_api.push_message(os.environ['MY_LINE_USER_ID'], TemplateSendMessage(alt_text=title, template=buttuns_template))
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

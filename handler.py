import json
import os
from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    # signature = event['headers']['x-line-signature']
    # try:
    #     # handleの引数はJSON文字列（パース前）
    #     webhook_handler.handle(event['body'], signature)
    #     print('authenticated')
    #     # event['body']はJSON文字列なのでパースする
    #     body = json.loads(event['body'])
    #     reply_token = body['events'][0]['replyToken']
    #     line_bot_api.reply_message(reply_token, TextSendMessage('応答メッセージ'))
    # except InvalidSignatureError:
    #     print('not authenticated')
    #     print(InvalidSignatureError)

    # line_bot_api.push_message(os.environ['MY_LINE_USER_ID'], TextSendMessage(text='test'))
    message_actions = [
        MessageAction(label='元気！', text='> 元気！'),
        MessageAction(label='ちょっとしんどい', text='> ちょっとしんどい'),
        MessageAction(label='しんどい', text='> しんどい'),
        MessageAction(label='もう無理', text='> もう無理'),
    ]
    title = '今日もお仕事お疲れ様！'
    text = '体調はどうかな？'
    buttuns_template = ButtonsTemplate(text=text, title=title, actions=message_actions)
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

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

import json
import os
from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage, PostbackEvent, MessageEvent, TextMessage)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
parser = WebhookParser(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    signature = event['headers']['x-line-signature']
    body = event['body']
    try:
        webhook_handler.handle(body, signature)
        events = parser.parse(body, signature)
        print('authenticated')
    except InvalidSignatureError:
        print('not authenticated')
        print(InvalidSignatureError)
        return

    for event in events:
        if isinstance(event, PostbackEvent):
            text_send_message = TextSendMessage(event.postback.data)
        elif isinstance(event, MessageEvent):
            if not isinstance(event.message, TextMessage):
                return
            text_send_message = TextSendMessage(event.message.text)
        else:
            return
        reply_token = event.reply_token
        line_bot_api.reply_message(reply_token, text_send_message)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

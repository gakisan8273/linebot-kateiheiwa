import json
import os

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    line_bot_api.push_message(os.environ['MY_LINE_USER_ID'], TextSendMessage(text='test'))
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

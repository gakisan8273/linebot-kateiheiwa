import json
import os
import boto3

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tired-scores')

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
        line_events = parser.parse(body, signature)
        print('authenticated')
    except InvalidSignatureError:
        print('not authenticated')
        print(InvalidSignatureError)
        return

    for line_event in line_events:
        if isinstance(line_event, PostbackEvent):
            user_id = line_event.source.user_id
            response = table.get_item(Key={'id': user_id})
            if 'Item' in response:
                score = int(response['Item']['score'])
            else:
                score = 0
            add_score = int(line_event.postback.data)
            table.put_item(
                Item = {
                    "id": user_id,
                    "score": score + add_score,
                }
            )
            text_send_message = TextSendMessage(line_event.postback.data)
        elif isinstance(line_event, MessageEvent):
            if not isinstance(line_event.message, TextMessage):
                return
            text_send_message = TextSendMessage(line_event.message.text)
        else:
            return
        reply_token = line_event.reply_token
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

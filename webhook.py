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
        print(line_event)
        if not isinstance(line_event, PostbackEvent):
            continue
        user_id = line_event.source.user_id
        response = table.get_item(Key={'id': user_id})
        if 'Item' in response:
            score_now = int(response['Item']['score'])
        else:
            score_now = 0
        score_add = int(line_event.postback.data)
        score = score_now + score_add
        table.put_item(
            Item = {
                "id": user_id,
                "score": score,
            }
        )
        # スコアが20未満（仮）なら無理しないでね的な言葉をかける
        if score < 20:
            text_send_message = TextSendMessage('無理しないでね！')
        # スコアが20以上~40未満（仮）なら休みを促す
        elif score < 40:
            text_send_message = TextSendMessage('疲れてるみたいだね！そろそろ休もうか？')
        # スコアが40以上（仮）なら休みを強く促す
        else:
            text_send_message = TextSendMessage('そうだね！今日は一人でご飯食べてきた方がいいね！')
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

import json
import os
import boto3

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tired-scores')

from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage, PostbackEvent)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
parser = WebhookParser(os.environ['LINE_CHANNEL_SECRET'])

def handler(event, context):
    signature: str = event['headers']['x-line-signature']
    body: dict = event['body']
    if not authenticate(body, signature):
        return

    line_events: list = parser.parse(body, signature)
    for line_event in line_events:
        # ポストバックイベントのみ処理する
        if not isinstance(line_event, PostbackEvent):
            continue

        id: str = line_event.source.user_id
        # 現在のスコア・イベントから送信されたスコアより更新する値を決定する
        score_now: int = get_score(id)
        score_add: int = int(line_event.postback.data)
        score: int = calculate_score(score_now, score_add)

        # DynamoDBのスコアを更新
        result = put_item(id, score)

        # スコアから応答メッセージを生成して送信
        text_send_message: TextSendMessage = genarate_send_message(score)
        result = reply_message(line_event.reply_token, text_send_message)

    body = {
        "message": "応答メッセージを送信しました。",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

# LINEメッセージ認証処理
def authenticate(body: dict, signature: str) -> bool:
    try:
        webhook_handler.handle(body, signature)
        return True
    except InvalidSignatureError:
        print('not authenticated')
        print(InvalidSignatureError)
        return False

# DynamoDBからスコアを取得
def get_score(id: str) -> int:
    # TODO: 例外処理
    response = table.get_item(Key={'id': id})
    if not 'Item' in response:
        return 0
    return int(response['Item']['score'])

# DynamoDBのスコアを更新
def put_item(id: str, score: int):
    # TODO: 例外処理
    table.put_item(
        Item = {
            "id": id,
            "score": score,
        }
    )

# 更新するスコアを計算する
def calculate_score(now: int, add: int) -> int:
    # 送信スコアが-1なら完全回復する
    if add == -1:
        return 0
    # 送信スコアが0なら10まで回復
    elif add == 0:
        return 10
    else:
        return now + add

# スコアに応じた応答メッセージを生成する
def genarate_send_message(score: int) -> TextSendMessage:
    # スコアが20未満（仮）なら無理しないでね的な言葉をかける
    if score < 20:
        return TextSendMessage('無理しないでね！')
    # スコアが20以上~40未満（仮）なら休みを促す
    elif score < 40:
        return TextSendMessage('疲れてるみたいだね！そろそろ休もうか？')
    # スコアが40以上（仮）なら休みを強く促す
    else:
        return TextSendMessage('そうだね！今日は一人でご飯食べてきた方がいいね！')

# LINEメッセージを応答する
def reply_message(reply_token: str, text_send_message: TextSendMessage):
    # TODO: 例外処理
    return line_bot_api.reply_message(reply_token, text_send_message)

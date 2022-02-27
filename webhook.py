import json
import os
import boto3

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tired-scores__')

from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage, PostbackEvent)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
parser = WebhookParser(os.environ['LINE_CHANNEL_SECRET'])

# LINE API最大試行数
MAX_ATTEMPTS = 3

def handler(event, context):
    # LINEメッセージ認証処理
    signature: str = event['headers']['x-line-signature']
    body: dict = event['body']
    try:
        webhook_handler.handle(body, signature)
    except InvalidSignatureError as e:
        print('not authenticated')
        return

    line_events: list = parser.parse(body, signature)
    for line_event in line_events:
        # ポストバックイベントのみ処理する
        if not isinstance(line_event, PostbackEvent):
            continue

        id: str = line_event.source.user_id
        # 現在のスコア・イベントから送信されたスコアより更新する値を決定する
        try:
            score_now: int = get_score(id)
        except Exception as e:
            print('error', e)
            # TODO: 例外発生時は再度発言を促す応答メッセージを返す
            return
        score_add: int = int(line_event.postback.data)
        score: int = calculate_score(score_now, score_add)

        # DynamoDBのスコアを更新
        try:
            put_item(id, score)
        except Exception as e:
            print('error', e)
            # TODO: 例外発生時は再度発言を促す応答メッセージを返す
            return

        # スコアから応答メッセージを生成して送信
        text_send_message: TextSendMessage = genarate_send_message(score)
        try:
            return line_bot_api.reply_message(line_event.reply_token, text_send_message)
        except Exception as e:
            print('error', e)
            # 応答失敗したら諦める
            # TODO: レスポンスを変更する
            return

    body = {
        "message": "応答メッセージを送信しました。",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

# DynamoDBからスコアを取得
def get_score(id: str) -> int:
    response = table.get_item(Key={'id': id})
    if not 'Item' in response:
        return 0

    return int(response['Item']['score'])

# DynamoDBのスコアを更新
def put_item(id: str, score: int) -> None:
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
    attempt_count = 1
    while attempt_count <= MAX_ATTEMPTS:
        try:
            line_bot_api.reply_message(reply_token, text_send_message)
        except LineBotApiError as e:
            attempt_count = attempt_count + 1

    raise LineBotApiError

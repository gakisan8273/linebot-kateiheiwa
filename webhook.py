import json
import os
import boto3
import random

dynamo_db = boto3.resource('dynamodb')
scores = dynamo_db.Table('tired-scores')
group_talk = dynamo_db.Table('group-talk')

from logging import getLogger
logger = getLogger(__name__)

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage, PostbackEvent, MessageEvent)
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
        # グループトークからの発言があれば登録する
        # それ以外はポストバックイベントのみ処理する
        if isinstance(line_event, MessageEvent):
            group_id: str = getattr(line_event.source, 'group_id', '')
            try:
                register_group_talk(group_id)
            except Exception as e:
                print('error', e)
                line_bot_api.reply_message(line_event.reply_token, TextSendMessage('ごめんなさい、エラーが発生したのでもう一回発言してね'))
                return
        if not isinstance(line_event, PostbackEvent):
            continue

        user_id: str = line_event.source.user_id
        # 現在のスコア・イベントから送信されたスコアより更新する値を決定する
        try:
            score_now: int = get_score(user_id)
        except Exception as e:
            print('error', e)
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage('ごめんなさい、エラーが発生したのでもう一回発言してね'))
            return
        score_add: int = int(line_event.postback.data)
        score: int = calculate_score(score_now, score_add)

        # DynamoDBのスコアを更新
        try:
            update_score(user_id, score)
        except Exception as e:
            print('error', e)
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage('ごめんなさい、エラーが発生したのでもう一回発言してね'))
            return

        # スコアから応答メッセージを生成して送信
        send_message: str = genarate_send_message(score)
        try:
            line_bot_api.reply_message(line_event.reply_token, TextSendMessage(send_message))
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
    response = scores.get_item(Key={'id': id})
    if not 'Item' in response:
        return 0

    return int(response['Item']['score'])

# グループトークを登録する
def register_group_talk(id: str) -> None:
    if not id:
        return
    group_talk.put_item(
        Item = {
            "id": id,
        }
    )

# DynamoDBのスコアを更新
def update_score(id: str, score: int) -> None:
    scores.put_item(
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
def genarate_send_message(score: int) -> str:
    json_open = open('reply.json', 'r')
    reply_messages = json.load(json_open)

    # 〜120→元気
    if score <= 120:
        condition = 'genki'
    # 121〜240 なんとか頑張ってる
    elif score <= 240:
        condition = 'nantoka'
    # 241〜360 そろそろきつい
    elif score <= 360:
        condition = 'sindoi'
    # 361〜480 ストレス溜まっている
    elif score <= 480:
        condition = 'kitsui'
    # 481〜600 休んだほうがいい
    elif score <= 600:
        condition = 'yasume'
    # 601〜    休め
    else:
        condition = 'limit'

    messages = reply_messages[condition]
    length = len(messages)
    if length > 1:
        element = random.randrange(length - 1)
    else:
        element = 0
    return reply_messages[condition][element]

# LINEメッセージを応答する
def reply_message(reply_token: str, text: str):
    attempt_count = 1
    messages = TextSendMessage(text)
    while attempt_count <= MAX_ATTEMPTS:
        try:
            line_bot_api.reply_message(reply_token, messages)
        except LineBotApiError as e:
            attempt_count = attempt_count + 1

    raise LineBotApiError

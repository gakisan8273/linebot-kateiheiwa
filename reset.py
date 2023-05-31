import json
from multiprocessing.dummy import Array
import os
import boto3

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage)
line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])

dynamo_db = boto3.resource('dynamodb')
scores = dynamo_db.Table('tired-scores')
group_talk = dynamo_db.Table('group-talk')

def handler(event, context):
    try:
        reset()
        group_talk_id = get_group_talk_id()
        line_bot_api.push_message(group_talk_id, TextSendMessage('全員の体調をリセットしました'), notification_disabled=True)
    except Exception as e:
        print(e)
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

# 全ユーザのスコアを0にする
def reset() -> None:
    users = get_users()
    for user in users:
        update_score(user, 0)

# ユーザを全て取得する
def get_users() -> Array:
    users = []
    records = scores.scan()
    for record in records['Items']:
        users.append(record['id'])
    return users

# トークグループIDを取得
def get_group_talk_id() -> str:
    records = group_talk.scan()
    if not records['Items']:
        raise Exception
    return records['Items'][0]['id']

# DynamoDBのスコアを更新
def update_score(id: str, score: int) -> None:
    scores.put_item(
        Item = {
            "id": id,
            "score": score,
        }
    )

import json
from multiprocessing.dummy import Array
import os
import boto3

dynamo_db = boto3.resource('dynamodb')
table = dynamo_db.Table('tired-scores')


def handler(event, context):
    try:
        reset()
    except Exception as e:
        print('error', e)
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
        put_item(user, 0)

# ユーザを全て取得する
def get_users() -> Array:
    users = []
    records = table.scan()
    for record in records['Items']:
        users.append(record['id'])
    return users

# DynamoDBのスコアを更新
def put_item(id: str, score: int) -> None:
    table.put_item(
        Item = {
            "id": id,
            "score": score,
        }
    )

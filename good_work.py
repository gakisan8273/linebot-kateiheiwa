import json
import os
import uuid
import boto3

dynamo_db = boto3.resource('dynamodb')
group_talk = dynamo_db.Table('group-talk')

from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (TemplateSendMessage, ButtonsTemplate, PostbackAction)
from linebot.exceptions import (LineBotApiError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# ステータス定義
# 上限600とする
# 元気 → 5日で上限になるように 600/5=120
# なんとか → 3日で上限になるように 600/3=200
# しんどい → 2日で上限になるように 600/2=300
# もう無理 → 一発で上限を超えるように 600<601
# 〜120 元気
# 121〜240 なんとか頑張ってる
# 241〜360 そろそろきつい
# 361〜480 やばい
# 481〜600 休め
# 601〜    強く休め
STATUS_DICT = {
    'genki': {
        'score': 120,
        'label': '元気！',
    },
    'a_little_sindoi': {
        'score': 200,
        'label': 'なんとか',
    },
    'sindoi': {
        'score': 300,
        'label': 'しんどい',
    },
    'muri': {
        'score': 601,
        'label': 'もう無理',
    },
}

# LINE API最大試行数
MAX_ATTEMPTS = 3

def handler(event, context):
    # TODO: ボタンテンプレートの出しわけ
    title = event.get('title', '今日もお仕事お疲れ様！')
    text = event.get('text', '体調はどうかな？')
    reply_token = event.get('reply_token')
    postback_actions = []
    for status, item in STATUS_DICT.items():
        postback_actions.append(PostbackAction(data=item['score'], label=item['label'], text='> ' + item['label']))
    buttuns_template = ButtonsTemplate(text=text, title=title, actions=postback_actions)
    try:
        group_talk_id = get_group_talk_id()
        send_postback_message(group_talk_id, title, buttuns_template, reply_token)
    except Exception as e:
        print('error', e)
        # TODO: レスポンスを変更する
        return

    body = {
        "message": "お疲れ様メッセージを送信しました。",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

# LINEメッセージを送信する
def send_postback_message(id: str, alt_text: str, buttuns_template: ButtonsTemplate, reply_token: str) -> bool:
    # 16進表記のUUID
    retry_key = str(uuid.uuid1())
    attempt_count = 1
    messages = TemplateSendMessage(alt_text=alt_text, template=buttuns_template)
    while attempt_count <= MAX_ATTEMPTS:
        try:
            if reply_token:
                line_bot_api.reply_message(reply_token=reply_token, messages=messages)
            else:
                line_bot_api.push_message(to=id, messages=messages, retry_key=retry_key)
            return True
        except LineBotApiError as e:
            attempt_count = attempt_count + 1

    raise LineBotApiError

# トークグループIDを取得
def get_group_talk_id() -> str:
    records = group_talk.scan()
    if not records['Items']:
        raise Exception
    return records['Items'][0]['id']

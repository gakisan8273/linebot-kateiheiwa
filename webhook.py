import json
import os
from aiohttp import content_disposition_filename
import boto3
import random

reply_messages = json.load(open('reply.json', 'r'))
scores = json.load(open('score.json', 'r'))

dynamo_db = boto3.resource('dynamodb')
step_functions = boto3.client('stepfunctions')
scores_table = dynamo_db.Table('tired-scores')
group_talk_table = dynamo_db.Table('group-talk')

from linebot import (LineBotApi, WebhookHandler, WebhookParser)
from linebot.models import (TextSendMessage, PostbackEvent, MessageEvent, MessageAction, ButtonsTemplate, TemplateSendMessage)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)

line_bot_api = LineBotApi(os.environ['LINE_ACCESS_TOKEN'])
webhook_handler = WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])
parser = WebhookParser(os.environ['LINE_CHANNEL_SECRET'])

# LINE API最大試行数
MAX_ATTEMPTS = 3

# 何かしてから帰宅する時の文言
REST_JSON = {
    'BACK_AFTER_SLEEP': '子供が寝てから帰る',
    'EAT_DINNER': 'ご飯を食べてくる',
}

# 普通に帰宅する時の文言
BACK_HOME_SOON = 'また別の日にする'

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
            try:
                # 特定の発話ならstep functionsを開始して一定時間後に回復メッセージを送信する
                start_stepfunctions(line_event)
                register_group_talk(getattr(line_event.source, 'group_id', ''))
                continue
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

        try:
            # スコアから応答メッセージを生成して送信
            # 送信されたスコアが0以下なら休んだとみなし、メッセージを変える
            if score_add > 0:
                title: str = genarate_send_otukare_message(score)
                message_actions = [
                    MessageAction(label=REST_JSON['BACK_AFTER_SLEEP'], text='> ' + REST_JSON['BACK_AFTER_SLEEP']),
                    MessageAction(label=REST_JSON['EAT_DINNER'], text='> ' + REST_JSON['EAT_DINNER']),
                    MessageAction(label=BACK_HOME_SOON, text='> ' + BACK_HOME_SOON),
                ]
                buttons_template = ButtonsTemplate(text='休む？', title=title, actions=message_actions)
                line_bot_api.reply_message(line_event.reply_token, TemplateSendMessage(alt_text='休む？', template=buttons_template))
            else:
                send_message: str = genarate_send_kaihuku_message()
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

def start_stepfunctions(message_event: MessageEvent) -> None:
    text = getattr(message_event.message, 'text', '')
    if not '> ' in text:
        return

    if REST_JSON['BACK_AFTER_SLEEP'] in text:
        step_functions.start_execution(stateMachineArn=os.environ['HEAL_ARN'])
        line_bot_api.reply_message(message_event.reply_token, TextSendMessage('ゆっくり休んできて！'))
    elif REST_JSON['EAT_DINNER'] in text:
        step_functions.start_execution(stateMachineArn=os.environ['HEAL_ARN'])
        line_bot_api.reply_message(message_event.reply_token, TextSendMessage('そーっと帰ってきてね！'))
    else:
        return


# DynamoDBからスコアを取得
def get_score(id: str) -> int:
    response = scores_table.get_item(Key={'id': id})
    if not 'Item' in response:
        return 0

    return int(response['Item']['score'])

# グループトークを登録する
def register_group_talk(id: str) -> None:
    if not id:
        return
    group_talk_table.put_item(
        Item = {
            "id": id,
        }
    )

# DynamoDBのスコアを更新
def update_score(id: str, score: int) -> None:
    scores_table.put_item(
        Item = {
            "id": id,
            "score": score,
        }
    )

# 更新するスコアを計算する
def calculate_score(now: int, add: int) -> int:
    if add == -1:
        return 0
    elif add == 0:
        return scores['genki']
    else:
        return now + add

# スコアに応じた応答メッセージを生成する
def genarate_send_otukare_message(score: int) -> str:
    # 〜120→元気
    if score <= scores['genki']:
        condition = 'genki'
    # 121〜240 なんとか頑張ってる
    elif score <= scores['nantoka']:
        condition = 'nantoka'
    # 241〜360 しんどい
    elif score <= scores['sindoi']:
        condition = 'sindoi'
    # 361〜480 きつい
    elif score <= scores['kitsui']:
        condition = 'kitsui'
    # 481〜600 休め
    elif score <= scores['yasume']:
        condition = 'yasume'
    # 601〜    限界
    else:
        condition = 'limit'

    messages = reply_messages[condition]
    length = len(messages)
    if length > 1:
        element = random.randrange(length)
    else:
        element = 0
    return reply_messages[condition][element]

# 回復したときのメッセージを生成する
def genarate_send_kaihuku_message() -> str:
    messages = reply_messages['kaihuku']
    length = len(messages)
    if length > 1:
        element = random.randrange(length)
    else:
        element = 0
    return reply_messages['kaihuku'][element]

# LINEメッセージを応答する
def reply_message(reply_token: str, text: str) -> None:
    attempt_count = 1
    messages = TextSendMessage(text)
    while attempt_count <= MAX_ATTEMPTS:
        try:
            line_bot_api.reply_message(reply_token, messages)
            return
        except LineBotApiError as e:
            attempt_count = attempt_count + 1

    raise LineBotApiError

import json
import os
import boto3

# 休んだ時のオンデマンドメニュー
STATUS_DICT_ON_DEMAND_REST = {
    'sukosi_kaihuku': {
        'score': 0,
        'label': '少し回復',
    },
    'kannzen_kaihuku': {
        'score': -1,
        'label': '完全回復',
    }
}

def handler(event, context):
    payload = {
        'title': 'ちょっとは休めたかな？',
        'text': '体調はどうかな？',
        'status_dict': STATUS_DICT_ON_DEMAND_REST
    }
    function_name = 'linebot-kateiheiwa-' + os.environ['ENV'] + '-good_work'
    boto3.client('lambda').invoke(
        # TODO: ARNを環境変数から取得
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

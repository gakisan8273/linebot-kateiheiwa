## このリポジトリ何？
育児・仕事に疲れてるのに、一人になりたいと言い出せない。
疲れを溜め込んで結局爆発してしまう。

そんな気質の配偶者を持っている方の助けになればと思います。

このBOTはいい感じのタイミングで一人になることを促し、家庭の平和を守ってくれます。

## 設定方法
1. LINE DevelopersからMessaging APIの新規チャネルを作成する
  - 参考: https://developers.line.biz/ja/docs/messaging-api/getting-started/  #using-oa-manager

1. `.env` を生成し各値を設定
```:bash
$ cp .env.example .env

# 各値を設定してください
$ vim .env
```

1. Serverless Frameworkを用いてAWSアカウントにデプロイ

```
$ npm install -g serverless
$ export AWS_ACCESS_KEY_ID=<your-key-here>
$ export AWS_SECRET_ACCESS_KEY=<your-secret-key-here>
$ npm ci

$ sls deploy
Running "serverless" from node_modules

Deploying linebot-kateiheiwa to stage dev (<your-region>)

✔ Service deployed to stack linebot-kateiheiwa-dev (53s)

endpoint: POST - https://xxxxxxxxxx.execute-api.<your-region>.amazonaws.com/ ← 次のステップで使用します
functions:
  send_message: linebot-kateiheiwa-dev-send_message (7.1 MB)
  reset: linebot-kateiheiwa-dev-reset (7.1 MB)
  webhook: linebot-kateiheiwa-dev-webhook (7.1 MB)
layers:
  pythonRequirements: arn:aws:lambda:<your-region>:<your-aws-account-id>:layer:dev-requirementLayer:3
```

1. LINEチャネルの `Webhookの利用` をONにし、 WebhookURLに3で生成されたendpointのurlを設定する

1. LINEチャネルの `グループトーク・複数人トークへの参加を許可する` を有効にする

1. スマホでLINEチャネルのQRコードを読み取り友達登録する。

1. 自分・配偶者・作成したLINEチャネルのグループトークを作成する

## 使い方
### 仕事終わりの疲れ度合いチェック
- 平日17時に以下のお疲れ様メッセージがBOTから送信される
- 疲れ度合いに応じたものを選択する
- 内部で疲れ度合いの累積を計算する
- 疲れ度合いに応じたメッセージを返す
  - 疲れが溜まってると判断したら、一人の時間をとることを促すメッセージを返す

### 任意の時間の疲れ度合い送信
- なんでもいいので発話する
- 以下の選択肢がBOTから送信される
- 疲れ度合いに応じたものを選択する

### 疲れが回復したことを送信
- なんでもいいので発話する
- 以下の選択肢がBOTから送信される
- 回復度合いに応じたものを選択する

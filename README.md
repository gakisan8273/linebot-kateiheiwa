## このリポジトリ何？
育児・仕事に疲れてるのに、一人になりたいと言い出せない。
疲れを溜め込んで結局爆発してしまう。

そんな気質の配偶者を持っている方の助けになればと思います。

このBOTはいい感じのタイミングで一人になることを促し、家庭の平和を守ってくれます。

## 設定方法
本気で使う気がある方は、 https://twitter.com/gakisan8273 に連絡ください。サポートします。

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
```

1. LINEチャネルの `Webhookの利用` をONにし、 WebhookURLに3で生成されたendpointのurlを設定する

1. LINEチャネルの `グループトーク・複数人トークへの参加を許可する` を有効にする

1. スマホでLINEチャネルのQRコードを読み取り友達登録する。

1. 自分・配偶者・作成したLINEチャネルのグループトークを作成する

## 使い方
### 仕事終わりの疲れ度合いチェック
- 平日17時40分に以下のお疲れ様メッセージがBOTから送信される
  - 送信時間の変更はserverless.ymlのcronをいじってください
- 疲れ度合いに応じたものを選択する
- 内部で疲れ度合いの累積を計算する
- 疲れ度合いに応じたメッセージを返す
  - 疲れが溜まってると判断したら、一人の時間をとることを促すメッセージを返す
    - `ご飯を食べてくる` `子供が寝てから帰る` を選択されたら、90分後にどれだけ回復したかを確認するメッセージを送信する

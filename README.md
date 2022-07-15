## このリポジトリ何？
子供の世話があるので家に帰らないといけない。

ほんとうは育児・仕事に疲れてるのに、一人になりたいと言い出せない。

そして疲れを溜め込み、いつか結局爆発してしまう。

そんな気質の配偶者を持っている方の助けになればと思います。

このLINE BOTはいい感じのタイミングで一人になることを促し、家庭の平和を守ってくれます。


---

`そんなの毎日自分が気遣ってあげればいいじゃん？` と思う方、いらっしゃいますよね。

毎日毎日気遣うのはこちらもとてもしんどいのです。しんどいことはpythonにやらせよう

## 使用イメージ
1. 自分・配偶者・このリポジトリのLINE BOTのグループラインを作る
1. 定刻になるとBOTが配偶者に体調を伺う
1. 配偶者が体調を回答する
1. 体調に応じてBOTが一人になることを促す ← **一人になると言い出しやすい！！！！**
1. 配偶者が回復し、家庭がちょっと平和になる

<img src="https://user-images.githubusercontent.com/52925914/179214034-e369572c-8289-4806-a99f-9df1427a4de9.jpg" width="300">

<img src="https://user-images.githubusercontent.com/52925914/179214048-db2794f0-d023-4440-a2b5-988a2687eb67.jpg" width="300">

---

我が家は実際にこれを運用しています。ワンボタンで休むと言い出せるのでとても好評です。

平和に一歩近づきました。

## 設定方法
**使う気がある方は、 https://twitter.com/gakisan8273 に連絡ください。サポートします。**

このLINE BOTはAWSを使用します。以下、AWSアカウントを持っていること・AWS CLIがインストールされていることを前提として進めます。

### 環境変数
1. `.env` を生成
```:bash
$ cp .env.example .env
```

### Serverless Framework設定
1. AWS_ACCOUNT_IDとAWS_REGIONを設定
```:bash
$ vim .env

AWS_ACCOUNT_ID=<your-id-here>
AWS_REGION=<your-region-here>
```

2. Serverless Frameworkを用いてAWSにデプロイ

```
$ npm install -g serverless
$ export AWS_ACCESS_KEY_ID=<your-key-here>
$ export AWS_SECRET_ACCESS_KEY=<your-secret-key-here>
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

3. 生成されたendpoint `https://xxxxxxxxxx.execute-api.<your-region>.amazonaws.com/` を控えておく（LINE Developers設定で使います）


### LINE Developers設定
1. LINE DevelopersからMessaging APIの新規チャネルを作成する
  - 参考: https://developers.line.biz/ja/docs/messaging-api/getting-started/#using-oa-manager
2. 作成したチャネルから取得できる Channel access token / Channel Secret を.envに設定する

```:bash
$ vim .env

LINE_ACCESS_TOKEN=<your-token-here>
LINE_CHANNEL_SECRET=<your-secret-here>
```

3. LINEチャネルの `Webhookの利用` をONにし、WebhookURLに Serverless Framework設定の際に生成されたendpointのurl(`https://xxxxxxxxxx.execute-api.<your-region>.amazonaws.com/`)を設定する
4. LINEチャネルの `グループトーク・複数人トークへの参加を許可する` を有効にする



### LINE（スマホ）設定
1. LINE Developers設定で作成したチャネルのQRコードを読み取り友達登録する
1. 自分・配偶者・作成したLINEチャネルのグループトークを作成する


## カスタム方法
- これから書く

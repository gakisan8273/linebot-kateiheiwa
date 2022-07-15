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

1. LINE DevelopersからMessaging APIの新規チャネルを作成する
  - 参考: https://developers.line.biz/ja/docs/messaging-api/getting-started/#using-oa-manager

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

$ sls deploy
```

1. LINEチャネルの `Webhookの利用` をONにし、 WebhookURLに3で生成されたendpointのurlを設定する

1. LINEチャネルの `グループトーク・複数人トークへの参加を許可する` を有効にする

1. スマホでLINEチャネルのQRコードを読み取り友達登録する。

1. 自分・配偶者・作成したLINEチャネルのグループトークを作成する

## 使い方
### 仕事終わりの疲れ度合いチェック
- 平日17時40分に以下のお疲れ様メッセージがBOTから送信される
  - 送信時間の変更は `serverless.yml` のcronをいじってください
- 疲れ度合いに応じたものを選択する
- 内部で疲れ度合いの累積を計算する
- 疲れ度合いに応じたメッセージを返す
  - 疲れが溜まってると判断したら、一人の時間をとることを促すメッセージを返す
    - `ご飯を食べてくる` `子供が寝てから帰る` を選択されたら、90分後にどれだけ回復したかを確認するメッセージを送信する

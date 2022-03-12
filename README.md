## リッチメニューアップロード方法

リッチメニュー作成
```
$ curl -X POST https://api.line.me/v2/bot/richmenu \
-H 'Authorization: Bearer {ACCESS_TOKEN}' \
-H 'Content-Type: application/json' \
-d @richmenu.json

{"richMenuId":"richmenu-fe27d9c88a7a760c4225e14d2617b820"}
```

リッチメニューの画像をアップロード
```
$ curl -X POST https://api-data.line.me/v2/bot/richmenu/{richMenuId}}/content \
-H "Authorization: Bearer {ACCESS_TOKEN} " \
-H "Content-Type: image/jpeg" \
-T images/richmenu.jpg
```

デフォルトのリッチメニューを設定
```
$ curl -v -X POST https://api.line.me/v2/bot/user/all/richmenu/richmenu-fe27d9c88a7a760c4225e14d2617b820 \
-H "Authorization: Bearer {ACCESS_TOKEN} "
```
# 現在のTODO

## ソースコード側

- user dataの取得を可能に
- tweet可能なentrypointを用意
- ブラウザログインの実装
- 独自認証キーの発行
- fav, retweetの取得・表示
- fav, retweetを可能に

## LogiX側

- 画像の表示
- [x] UIの整備

# 仕様

## DB

### messages

- message_id: PK
- message
- user_id
- attachments
  - カンマ区切りのテキスト
- created_datetime
- client
  - twitter or discord

### user

- user_id: PK
- name
- icon_url
- client

## response

BNF
```
<response> := <datetime>"|"<num_of_messages>"|"<messages>
<datetime> := "yyyy-mm-dd HH:MM:ss"
<num_of_messages> := int
<messages> := <message>["$"<messages>]
<message>  := <datetime>";"<name>";"<icon_url>";"<images>";"<text>
<name>     := string (url encoded)
<icon_url> := string (url encoded)
<images>   := <image_url>[","<images>]
<image_url>:= string (url encoded)
<text>     := string (url encoded)
```

# memo

## 6/25

やること
- neotter_user dbの作成
- neotter_user dbへのput

## 4/12

oauthによるログイン機能の追加に向けて

案
- 期間限定のkeyを発行
- Neos側でkeyからaccess keyを生成
- ip制限
  - ipは取得しようと思えば簡単に取得可能 & 偽装も可能のため却下
  - と思ったけど、怪しいhostを許可しなければOKか
- 暗号化
  - logix自体をseedから自動生成し、他人からの読み取りを難しくする
- 二段階認証する？

### サーバー(現実)側

- oauthの実験
- ログイン画面
  - サーバーサイド実装
    - oauth認証
      - id/passのvalidation(xss対策)
      - ログインセッションの有効期限も設定しておく(一か月)
        - Cookie周り
    - ip判別
      - https://qiita.com/se_fy/items/d5aee7e8eb74bc892843
    - keyのリセット
    - keyとaccess token/secretとの結びつけ
    - user pageの閲覧可否判定
  - フロントエンド実装
    - 良さげなフレームワーク・ライブラリ探しておく
    - 注意書き・導入方法は書いておく
- callback画面
  - 説明を書く
- サーバのSSL化
  - どのPaaSが良いか検討
    - コスト
    - docker使えるか
    - DBどうするか
- DB設計
  - TBD
- ログインセッションの維持
  - 後回し可能
  - 参考: https://qiita.com/ikaro1192/items/d890eefbdbbfe1460252

### クライアント(Neos)側

- Neos側のクライアントからkeyを取得されない方法を模索
  - user-install型にするのはあり

## 公開に向けて

- 導入ドキュメントの用意
  - Neos内・Webページ上共に
- local viewとpublic viewの切り替えができるようにしたい
- 英語ページ・インターフェイス・ドキュメントも用意したい

## 4/5

### TODO

- collector.py
  - [x] timeline_to_dict_iter
    - media取得
    - client追加
    - name,screen_name
  - [x] pipeline
    - messageをurlencode
    - nameをurlencode
  - [x] store_timeline
    - user格納処理を追加
- db_write.py
  - [x] migration
    - messagesの形式変更
      - media
      - client
    - userを追加
  - [x] put_messages
  - [x] 追加: update_user
- app.py
  - [x] process_messages
- db_read.py
  - [x] get_recent_messages
    - userをjoinして取得
    - その他変更部分


- [x] 一定期間経過したデータの自動破棄
- [x] サーバーへのデプロイ
  - CircleCI連携
  - [x] CircleCIではなくgithub actionsに
- テストを書く
- [x] messageのフォーマットを再整理
- [x] user dbを作成
  - iconをdbに追加
  - twitterのnameの形式を変更
    - <screen_name>@<id>の形式に
  - 画像をparseしやすい形式で追加
    - dbにattachカラムを追加する？
- [x] messageをencodeして送信するようにする

## old

- セッション的なものをどう管理するか
  - あるクライアントについて、どこまで読み込んだか or どこがスタートか、を保持する必要がある
  - 何個読み込んだか、はクライアント側で値を保存可能

# 小さく試す

0. tweet収集worker
  - [x] 手元で動作確認
  - [x] dockerで動作確認
1. 最新tweetを表示
  - flaskサーバー立てる
    - [x] local
    - [x] docker
  - [x] 最新home tweet3つを取得するendpointを作成
  - [x] ngrokをdockerに入れ、環境変数で設定可能にする
2. [x] 文字列分割を試す
3. [x] 最新3tweetを表示
4. [x] 10秒表示されたら自己破壊するオブジェクトの表示
5. [x] オブジェクト生成を試す
6. [x] 以前に取得したtweetの続きから取得できるようにする
7. [x] 4〜6を連結し、右から左に流す
8. 取得速度の変更
9. 文字列を入力としたlogiX
10. ハッシュタグでの検索結果を表示する
11. コードの整理
12. 他の人でも使える方法を調べる

# その他

- common_settings
  - base dockerを用意して、そこからコピーする
- message構造体を用意した方が良さそう

# apiをどうするか

## 決定

下記の案1に決定

### api仕様

countパラメータはoptional

- 初回
  - リクエスト
    - パラメータなし
  - レスポンス
    - start_time|<message>\n<message>...
- 2度目以降
  - リクエスト
    - パラメータ
      - start_time
      - offset
  - レスポンス
    - 初回と同じ

### neos実装

countパラメータは外から渡せるようにする

- リクエスト前
  - Timerトリガーで起動
  - offsetの値に応じて場合分けを行いパラメータの構築
  - リクエスト飛ばす
- リクエスト後
  - 初回(offsetが0のとき)
    - start_timeの保持
  - 初回問わず
    - offsetの増加
  - responseのパース

### neos側のパラメータどうする

- 固定
  - request interval
  - host
  - delimiter
- 可変
  - tweet生成頻度
    - countにも影響
  - tweetの流れる速度
  - 生存時間
  - 高さ

## 案1

- (日時)パラメータなしで送った場合、現時刻よりn秒前のtweetを取得
- ~~返り値にoffsetを渡す~~ レスポンスで日時を渡す
  - split的な関数があるか要検証
    - 自作
- ~~内部idを保存してなかったので却下~~
  - ~~今から追加できるので~~
- パラメータ(すべて必須ではない)
  - 日時
  - offset
  - count

offsetのインクリメントはサーバー側で制御？
- 返ってきたレスポンス数に応じてクライアント側でも可能
- ただ返ってくるtweetの数を返す方がapiとしては親切だよね

## 案2

- パラメータとして
  - utcnow(起動時タイムスタンプ)
    - neos側でtime-nしておく
  - offset
を送る

受け取ったtweetの数だけ、内部offsetを進める

これが実現できるか？
- utcnowの動作確認
- カウントアップ
  - 時計の動画とかみればおけ

utcnowの動作確認、split的関数のチェック

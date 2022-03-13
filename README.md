# Mediapipe(947D改造版)を用いた情報取得のサンプルプログラム

- Author: Hiroaki Yaguchi, 947D-Tech.
- ライセンス: Apache 2.0

## 本プログラムについて

筆者による改造版Mediapipeを使った情報取得のサンプルプログラムです。

### 必要なもの

- Mediapipe Android appをビルドできる環境(Dockerを推奨します)
- ある程度の性能のAndroid端末(動作確認環境はGoogle Pixel 5です)
- Python3が動くPC(確認はUbuntuで行っています)

## Mediapipe Android appのインストール方法

まず、改造版mediapipeのソースコードをgithubから取得してください。

https://github.com/hyaguchi947d/mediapipe

`holistic_v089_release`というブランチを使用します。

mediapipe環境の構築はDockerの利用を推奨します。

https://google.github.io/mediapipe/getting_started/install.html#installing-using-docker

Androidビルド環境の構築は公式ドキュメントを参照してください。

https://google.github.io/mediapipe/getting_started/android.html

Android appのビルドは以下のコマンドでできます。

```
$ bazelisk build mediapipe/examples/android/src/java/com/google/mediapipe/apps/holistictrackinggpu:holistictrackinggpu
```

インストールは実機をadbで認識させた上で、以下の方法でできます。

```
$ adb install bazel-bin/mediapipe/examples/android/src/java/com/google/mediapipe/apps/holistictrackinggpu/holistictrackinggpu.apk
```

送信されてくるデータの仕様は基本的に元の仕様を参照してjsonにしたものです。

https://google.github.io/mediapipe/solutions/holistic.html

ただし、各ランドマークにタイムスタンプを追加しています。
利用方法は本プログラムを参照してください。


## 本プログラムの動かし方

まず、Android端末でネットワーク設定を行ってください。

- HolisticTrackingを起動
- 画面右上のメニューマーク -> Settingをタップ
- ip addressに送信先のipを入力
    - 間違えるとアプリが起動しなくなる恐れがあります。起動しなくなった場合はAndroidの設定からアプリの設定を消去して再起動してください。

また、接続されているネットワークの設定でポート番号947Dを開放してください。
この状態で、各プログラムを動かすことができます。

注意: 各プログラム内で`-p`を与えることでポート番号を指定できますが、
アプリ側には指定機能がありません。
変更したい場合はソースコードを編集してください。

### リアルタイム受信

```
$ python3 holistic_receiver.py
```

### データの保存と再生

本アプリはその性質上、
画面を見ながら確認するのが難しい動きをする場合など
リアルタイムでの確認が難しい場合があります。
そのため、オフラインでの確認を行うためのデータ保存・再生用スクリプトを用意しました。

#### 保存

```
$ python3 json_dump.py
```

json形式で保存します。
ファイル名は`%03d.json`となっています。
1000を超えるデータを保存したい場合は適宜ソースコードを書き換えてください。

オプションは以下のとおりです。

- `-o` (default: `data`): 出力ディレクトリを指定します。
- `-d` (default: 0): 指定した秒数が経過した後に保存を開始します。
- `-n` (default: 1): 指定のフレーム数を保存します。

#### 再生

単一ファイルの再生のみ行うことができます。

```
$ python3 json_sender.py -i <ファイル名>
```

`-t`にIPアドレスを与えることで送信先を変更することができます。


### オフラインでの確認

保存した単一データの中身を可視化するプログラムになります。

```
$ python3 holistic_offline.py -i <入力ファイル名>
```

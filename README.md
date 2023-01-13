# Mediapipe(947D改造版)を用いた情報取得のサンプルプログラム

- Author: Hiroaki Yaguchi, 947D-Tech.
- ライセンス: Apache 2.0
    - Google Mediapipeのコードを一部改変して利用しています。
    - Apache 2.0, Copyright 2020 The MediaPipe Authors.

## 本プログラムについて

筆者による改造版Mediapipeを使った情報取得のサンプルプログラムです。
holistic trackingを用いることで、スマホ一台で全身トラッキングが可能です。

Android側のアプリケーションは
Humanoid Interface for Real-time Observation 4の
コントローラとして使用されているものと同一のプログラムになります。

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
$ bazelisk build -c opt --config=android_arm64 --linkopt="-s" mediapipe/examples/android/src/java/com/google/mediapipe/apps/holistictrackinggpu:holistictrackinggpu
```

インストールは実機をadbで認識させた上で、以下の方法でできます。

```
$ adb install bazel-bin/mediapipe/examples/android/src/java/com/google/mediapipe/apps/holistictrackinggpu/holistictrackinggpu.apk
```

起動すると、イニシャライズ(そこそこ時間がかかります)の後、画面に認識結果が表示されます。
設定されたIPアドレスのポート番号947D(10進数で38013)にUDPでデータを送信します。
設定はアプリ側のsettingsから変更可能です。
送信されてくるデータの仕様は基本的に元の仕様を参照してjsonにしたものです。

https://google.github.io/mediapipe/solutions/holistic.html

- `pose_world_landmarks`にm単位での姿勢認識結果が格納されます。
- `pose_landmarks`に姿勢認識結果が格納されます。
- `face_landmarks`に表情認識結果が格納されます。
- `right_hand_landmarks`,`left_hand_landmarks`に両手の認識結果がそれぞれ格納されます。

ただし、各ランドマークにタイムスタンプを追加しています。
利用方法は本プログラムを参照してください。

`pose_world_landmarks`以外の認識結果は
画面のアスペクト比を考慮する必要があることに注意してください。

デフォルトではインカメラを利用しています。
そのため、鏡像であることに注意してください。

また、スマホの向きを認識するための`gravity`を同時に送信しています。
カメラ向きの推定にご利用ください。

- `gravity`: 重力ベクトル
- `gravity_stamp`: 取得時刻

(2022/11 update)
カメラパラメータを追加で送信しています。
これを用いることで、`pose_landmarks`と`pose_world_landmarks`を比較して
カメラ座標系における人物の三次元位置の推定が可能です。

- `camera_params`
    - `focal_length`: 焦点距離(単位はピクセル)
    - `frame_width`: 画像の幅
    - `frame_height`: 画像の高さ


## 本プログラムの動かし方

まず、Android端末でネットワーク設定を行ってください。

- HolisticTrackingを起動
- 画面右上のメニューマーク -> Settingをタップ
- ip addressに送信先のipを入力
    - 間違えるとアプリが起動しなくなる恐れがあります。起動しなくなった場合はAndroidの設定からアプリの設定を消去して再起動してください。

また、接続されているネットワークの設定でポート番号947D(10進数で38013)のUDPを開放してください。
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

#### 単一ファイルに保存する場合

##### 保存

```
$ python3 data_recorder.py
```

テキストファイル形式で保存します。
ファイルの中に1フレーム分のjsonを改行区切りで保存します。
Ctrl-Cを入力すると途中でも中断することができます。

オプションは以下のとおりです。

- `-o` (default: `mediapipe_record.dat`): 出力ディレクトリを指定します。
- `-d` (default: 0): 指定した秒数が経過した後に保存を開始します。
- `-n` (default: 1): 指定のフレーム数を保存します。0以下の値を指定するとCtrl-Cを入力するまで保存し続けます。

##### 再生

```
$ python3 data_player.py -i <ファイル名>
```

Ctrl-Cが入力されるまでループして送信します。
`-t`にIPアドレスを与えることで送信先を変更することができます。


#### 1フレーム1ファイルとしてディレクトリに保存する場合

##### 保存

```
$ python3 json_dump.py
```

json形式で保存します。
ファイル名は`%03d.json`となっています。
1000を超えるデータを保存したい場合は適宜ソースコードを書き換えてください。
Ctrl-Cを入力すると途中でも中断することができます。

オプションは以下のとおりです。

- `-o` (default: `data`): 出力ディレクトリを指定します。
- `-d` (default: 0): 指定した秒数が経過した後に保存を開始します。
- `-n` (default: 1): 指定のフレーム数を保存します。

##### 再生

単一のjsonファイルを指定した場合そのファイルを繰り返し送信します。
ディレクトリを指定した場合はディレクトリ内のファイルを連続で送信します。
どちらの場合もCtrl-Cが入力されるまでループして送信します。

```
$ python3 json_sender.py -i <ファイルもしくはディレクトリ名>
```

`-t`にIPアドレスを与えることで送信先を変更することができます。


### オフラインでの確認

保存した単一データの中身を可視化するプログラムになります。

```
$ python3 holistic_offline.py -i <入力ファイル名>
```

## ROSパッケージについて

mediapipe_receiver_rosにROSで動作するサンプルプログラムがあります。
このディレクトリだけで動作するように作成してあります。

### 利用方法

```
$ roslaunch mediapipe_receiver_ros holistic.launch
```

`holistic_receiver_node.py`が本体プログラムになります。

- subscribe: なし(スマホからはUDPでデータが送信されます)
- publish:
    - `pose_landmarks` (visualization_msgs/Marker)
    - `face_landmarks` (visualization_msgs/Marker)
    - `right_hand_landmarks` (visualization_msgs/Marker)
    - `left_hand_landmarks` (visualization_msgs/Marker)

それぞれ表示用に必要な部分のみを抜き出しています。


### 動作確認済み環境

- ROS melodic
- ROS noetic

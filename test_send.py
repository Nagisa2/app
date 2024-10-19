# test_send.py
# USBシリアル通信のテスト用データ送信スクリプト

import serial
import time
import random
import logging

# シリアルポートの設定
SERIAL_PORT = '/dev/ttyUSB0'  # 使用するシリアルポート名（適切に変更してください）
BAUDRATE = 1200  # ボーレート

# ゴミの種類を定義
GARBAGE_TYPES = ['ペットボトル', 'スチール缶', 'アルミ缶', 'スプレー缶', '中身有容器']
# ゴミ箱のIDのサンプル
BIN_IDS = ['1', '2', '3', '4', '5']  # 実際のIDに合わせて変更

# シリアルポートを開く
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)  # シリアルポートのオープン
    time.sleep(2)  # デバイスが接続されるまで待機
except serial.SerialException as e:
    logging.error(f"シリアルポート接続エラー: {e}")  # 接続エラーをログに記録
    exit(1)  # エラーが発生した場合はスクリプトを終了

# テストデータ送信
try:
    for _ in range(10):  # 10回テストデータを送信
        bin_id = random.choice(BIN_IDS)  # ランダムにbin_idを選択
        garbage_type = random.choice(GARBAGE_TYPES)  # ランダムにゴミの種類を選択

        message = f"{bin_id},{garbage_type}\n"  # メッセージの構築
        try:
            ser.write(message.encode())  # データの送信
            print(f"送信データ: {message.strip()}")  # 送信データを表示
        except serial.SerialException as e:
            logging.error(f"データ送信エラー: {e}")  # 送信エラーをログに記録

        # サーバーからの応答を受信
        time.sleep(1)  # 必要に応じて調整
        response = ser.readline().decode().strip()  # サーバーからの応答を受信
        print(f"サーバー応答: {response}")  # サーバーからの応答を表示

finally:
    ser.close()  # 最後にシリアルポートを閉じる

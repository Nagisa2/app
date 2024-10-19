# test_receive.py
# USBシリアル通信のテスト用データ受信スクリプト

import serial
import logging
import time

# シリアルポートの設定
SERIAL_PORT = 'COM3'  # 使用するシリアルポート名（適切に変更してください）
BAUDRATE = 1200  # ボーレート

# シリアルポートを開く
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)  # シリアルポートのオープン
    time.sleep(2)  # デバイスが接続されるまで待機
except serial.SerialException as e:
    logging.error(f"シリアルポート接続エラー: {e}")  # 接続エラーをログに記録
    exit(1)  # エラーが発生した場合はスクリプトを終了

# データ受信
try:
    while True:
        if ser.in_waiting:  # データが受信待機中か確認
            data = ser.readline().decode().strip()  # データを受信
            print(f"受信データ: {data}")  # 受信データを表示
            
            # 受信したデータに応じて応答を送信
            response = f"受信したデータ: {data}"  # 応答メッセージ
            ser.write(response.encode())  # 応答を送信

finally:
    ser.close()  # 最後にシリアルポートを閉じる

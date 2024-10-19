import serial
import logging
import time

# シリアルポートの設定
SERIAL_PORT = '/dev/ttyUSB0'  # 使用するシリアルポート名（適切に変更してください）
BAUDRATE = 9600  # ボーレート

# シリアルポートを開く
try:
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)  # シリアルポートのオープン
    time.sleep(2)  # デバイスが接続されるまで待機
except serial.SerialException as e:
    logging.error(f"シリアルポート接続エラー: {e}")  # 接続エラーをログに記録
    exit(1)  # エラーが発生した場合はスクリプトを終了

# データ送信
try:
    while True:
        bin_id = input("bin_id: ")  # ゴミ箱IDの入力
        
        print("1: ペットボトル, 2: スチール缶, 3: アルミ缶, 4: スプレー缶, 5: 中身有容器")  # 数字を対応するゴミの種類にマップ
        garbage_number = input("ゴミの種類を選択してください (1-5): ")  # ゴミの種類の数字を入力
        
        if garbage_number not in ['1', '2', '3', '4', '5']:  # 無効な入力がないか確認
            print("無効な入力です。1から5の数字を入力してください。")
            continue  # 無効な入力の場合は再入力を促す

        message = f"{bin_id},{garbage_number}\n"  # メッセージの構築 (bin_id, garbage_number)
        try:
            ser.write(message.encode())  # データの送信
        except serial.SerialException as e:
            logging.error(f"データ送信エラー: {e}")  # 送信エラーをログに記録
            print("データの送信に失敗しました。")

        # サーバーからの応答を受信（応答を待つ時間を指定）
        time.sleep(1)  # 必要に応じて調整
        response = ser.readline().decode().strip()  # サーバーからの応答を受信
        print(f"サーバー応答: {response}")  # サーバーからの応答を表示

        if input("続けますか？ (y/n): ").lower() != 'y':  # 続行の確認
            break

finally:
    ser.close()  # 最後にシリアルポートを閉じる

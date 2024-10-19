import sqlite3
import serial
import logging

# ゴミの種類を数字にマッピング
GARBAGE_TYPES = {
    '1': 'ペットボトル',
    '2': 'スチール缶',
    '3': 'アルミ缶',
    '4': 'スプレー缶',
    '5': '中身有容器'
}

SERIAL_PORT = 'COM3'  # シリアルポート名（例: WindowsのCOM3、Linuxの/dev/ttyUSB0）
BAUD_RATE = 9600  # ボーレート

DATABASE = 'garbage.db'  # 使用するデータベースファイルの名前

class SerialServer:
    def __init__(self):
        self.serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE)  # シリアル接続を開く
        logging.info(f"シリアルポート {SERIAL_PORT} で待機中...")

    def start(self):
        try:
            while True:
                if self.serial_connection.in_waiting > 0:  # データが受信待機中か確認
                    data = self.serial_connection.readline().decode('utf-8').strip()  # データの受信
                    logging.info(f"受信データ: {data}")
                    
                    try:
                        bin_id, garbage_number = data.split(',')  # データをカンマで分割
                        
                        # 受信した数字をゴミの種類に変換
                        if garbage_number in GARBAGE_TYPES:
                            garbage_type = GARBAGE_TYPES[garbage_number]  # 数字からゴミの種類を取得
                            self.update_count(bin_id, garbage_type)  # カウントを更新
                            response = f"ゴミ箱 {bin_id} の {garbage_type} をカウントしました。"
                        else:
                            response = f"無効なゴミの種類番号: {garbage_number}"
                            logging.warning(response)
                    
                    except ValueError as e:
                        response = f"メッセージペイロードの解析に失敗しました: {data}, エラー: {e}"
                        logging.error(response)  # エラーをログに記録
                    
                    # 応答をシリアルポートに送信
                    self.serial_connection.write(response.encode('utf-8'))

        except Exception as e:
            logging.error(f"シリアル通信中にエラーが発生しました: {e}")  # 通信エラーをログに記録
        finally:
            self.serial_connection.close()  # シリアル接続を閉じる

    def update_count(self, bin_id, garbage_type):
        conn = None  # データベース接続を初期化
        try:
            conn = sqlite3.connect(DATABASE)  # データベースに接続
            c = conn.cursor()
            
            # countを加算
            c.execute(''' 
                INSERT INTO garbage (bin_id, type, count)
                VALUES (?, ?, 1)
                ON CONFLICT(bin_id, type) DO UPDATE SET count = count + 1
            ''', (bin_id, garbage_type))  # データの挿入または更新
            
            conn.commit()  # 変更をデータベースに反映
            logging.info(f"ゴミ箱 {bin_id} とゴミの種類 {garbage_type} のカウントを更新しました")
        except sqlite3.Error as e:
            logging.error(f"SQLiteエラー: {e}")  # データベースエラーをログに記録
        except Exception as e:
            logging.error(f"予期しないエラー: {e}")  # その他のエラーをログに記録
        finally:
            if conn:
                conn.close()  # データベース接続を閉じる

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # ログの基本設定
    serial_server = SerialServer()  # SerialServerのインスタンスを作成
    serial_server.start()  # サーバーを開始

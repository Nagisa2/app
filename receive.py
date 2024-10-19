# receive.py
# TCP通信のサーバー側のスクリプト

import sqlite3
import socket
import logging

# ゴミの種類を定義
GARBAGE_TYPES = ['ペットボトル', 'スチール缶', 'アルミ缶', 'スプレー缶', '中身有容器']  

# サーバーの設定
SERVER_IP = '192.168.1.10'  # サーバーのIPアドレス
PORT = 4000  # サーバーのポート番号
DATABASE = 'garbage.db'  # 使用するデータベースファイルの名前

class LANServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # サーバーソケットの作成
        try:
            self.server_socket.bind((SERVER_IP, PORT))  # サーバーのバインド
            self.server_socket.listen(1)  # 接続の待機
            logging.info(f"サーバーが {SERVER_IP}:{PORT} で待機しています...")
        except Exception as e:
            logging.error(f"サーバーの初期化に失敗しました: {e}")  # エラーをログに記録
            raise

    def start(self):
        while True:
            try:
                conn, addr = self.server_socket.accept()  # クライアントからの接続を待機
                logging.info(f"接続元: {addr} が接続しました")
                
                with conn:
                    conn.settimeout(10)  # タイムアウトを10秒に設定
                    while True:
                        try:
                            data = conn.recv(1024).decode()  # データの受信
                            if not data:
                                logging.warning("クライアントからの接続が切断されました。")  # 切断時のログ
                                break  # データがない場合、ループを終了
                            
                            logging.info(f"受信データ: {data}")
                            
                            try:
                                bin_id, garbage_type = data.split(',')  # データをカンマで分割
                                
                                if garbage_type in GARBAGE_TYPES:
                                    self.update_count(bin_id, garbage_type)  # カウントを更新
                                    response = f"ゴミ箱 {bin_id} の {garbage_type} をカウントしました。"
                                else:
                                    response = f"未知のゴミの種類: {garbage_type}"
                                    logging.warning(response)
                                
                            except ValueError as e:
                                response = f"メッセージペイロードの解析に失敗しました: {data}, エラー: {e}"
                                logging.error(response)  # エラーをログに記録
                            
                            conn.send(response.encode())  # クライアントへの応答送信

                        except socket.timeout:
                            logging.warning("データ受信がタイムアウトしました。クライアントに応答を返します。")
                            # タイムアウト時のデフォルト応答を送信する
                            default_response = "サーバーがタイムアウトしました。再接続してください。"
                            conn.send(default_response.encode())
                            break  # 受信タイムアウトの場合はループを終了

            except Exception as e:
                logging.error(f"クライアントとの通信中にエラーが発生しました: {e}")  # 通信エラーをログに記録

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
    lan_server = LANServer()  # LANServerのインスタンスを作成
    lan_server.start()  # サーバーを開始

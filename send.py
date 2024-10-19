# send.py
# TCP通信の送信側のスクリプト

import sqlite3
import socket
import logging

# サーバーIPとポートの設定
SERVER_IP = '192.168.1.10'  # サーバーのIPアドレス
PORT = 4000  # サーバーのポート番号

# ゴミの種類を定義
GARBAGE_TYPES = ['ペットボトル', 'スチール缶', 'アルミ缶', 'スプレー缶', '中身有容器']

DATABASE = 'garbage.db'  # 使用するデータベースファイルの名前

"""
    データベースからゴミ箱のIDを取得する関数。
    戻り値: ids ゴミ箱のIDのリスト。エラーが発生した場合は空リストを返す。
"""
def get_ids():    
    conn = None  # データベース接続を初期化
    try:
        conn = sqlite3.connect(DATABASE)  # データベースに接続
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM bins")  # ゴミ箱のIDを取得
        ids = [row[0] for row in cursor.fetchall()]  # 行をリストに変換
    except sqlite3.Error as e:
        logging.error(f"SQLiteエラー: {e}")  # データベースエラーをログに記録
        ids = []  # エラー時は空のリストを返す
    finally:
        if conn:  # 接続が存在する場合に閉じる
            conn.close()  
    return ids  # ゴミ箱のIDのリストを返す

# クライアントソケットの作成
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCPソケットの作成

# サーバーに接続
try:
    client_socket.connect((SERVER_IP, PORT))  # サーバーへの接続
except socket.error as e:
    logging.error(f"サーバー接続エラー: {e}")  # ソケット接続エラーをログに記録
    exit(1)  # エラーが発生した場合はスクリプトを終了

ids = get_ids()  # ゴミ箱のIDを取得

# データ送信
try:
    while True:
        print("既存のbin_idを選んでください:", ids)  # ゴミ箱IDの選択を促す
        bin_id = input("bin_id: ")  # bin_idの入力
        if bin_id not in ids:  # 入力されたbin_idがリストに存在しない場合
            print("無効なbin_idです。もう一度入力してください。")
            continue  # 無効なIDの場合は再入力を促す

        print("ゴミの種類を選んでください:", GARBAGE_TYPES)  # ゴミの種類の選択を促す
        garbage_type = input("garbage_type: ")  # garbage_typeの入力
        if garbage_type not in GARBAGE_TYPES:  # 入力されたgarbage_typeがリストに存在しない場合
            print("無効なゴミの種類です。もう一度入力してください。")
            continue  # 無効な種類の場合は再入力を促す

        message = f"{bin_id},{garbage_type}"
        try:
            client_socket.send(message.encode())  # データの送信
        except socket.error as e:
            logging.error(f"データ送信エラー: {e}")  # 送信エラーをログに記録
            print("データの送信に失敗しました。")

        try:
            response = client_socket.recv(1024).decode()  # サーバーからの応答を受信
            print(f"サーバー応答: {response}")  # サーバーからの応答を表示
        except socket.error as e:
            logging.error(f"応答受信エラー: {e}")  # 受信エラーをログに記録
            print("サーバーからの応答を受信できませんでした。")

        if input("続けますか？ (y/n): ").lower() != 'y':  # 続行の確認
            break

finally:
    client_socket.close()  # 最後にソケット接続を閉じる

# setup_db.py
# データベースのセットアップを行うスクリプト

import sqlite3
import logging

DATABASE = 'garbage.db'  # 使用するデータベースファイルの名前を定義

"""
    データベースにテーブルを作成する関数。
        bins、garbage、capacitiesの3つのテーブルを作成する。
        すでに存在する場合は新しく作成しない。
"""
def create_tables():
    conn = None  # データベース接続を初期化
    try:
        # データベースに接続
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        
        # bins テーブルの作成
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS bins (
                id TEXT PRIMARY KEY,
                location TEXT NOT NULL
            )
        ''')

        # garbage テーブルの作成
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS garbage (
                bin_id TEXT,
                type TEXT,
                count INTEGER,
                PRIMARY KEY (bin_id, type),
                FOREIGN KEY (bin_id) REFERENCES bins (id)
            )
        ''')

        # capacities テーブルの作成
        c.execute(''' 
            CREATE TABLE IF NOT EXISTS capacities (
                bin_id TEXT,
                type TEXT,
                capacity INTEGER,
                PRIMARY KEY (bin_id, type),
                FOREIGN KEY (bin_id) REFERENCES bins (id)
            )
        ''')

        conn.commit()  # 変更をデータベースに反映
        logging.info("テーブルの作成に成功しました。")  # 成功メッセージをログに記録

    # エラーをログに記録
    except sqlite3.OperationalError as oe:
        logging.error(f"操作エラー: {oe}")
    except sqlite3.IntegrityError as ie:
        logging.error(f"整合性エラー: {ie}")
    except sqlite3.Error as e:
        logging.error(f"SQLiteエラー: {e}")
    except Exception as ex:
        logging.error(f"予期しないエラー: {ex}")

    finally:
        if conn:
            conn.close()  # データベース接続を閉じる

if __name__ == '__main__':
    create_tables()  # スクリプトが直接実行された場合、テーブル作成関数を実行

# app.py
# Flaskアプリケーションのメインスクリプト

from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
import logging
import secrets
import ssl
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 16バイトのランダムな16進数の秘密鍵を生成

 # 使用するデータベースのファイル名
DATABASE = 'garbage.db'

 # ゴミの種類のリスト
GARBAGE_TYPES = ['ペットボトル', 'スチール缶', 'アルミ缶', 'スプレー缶', '中身有容器']

''' 
    データベース接続を取得する関数
        戻り値: g.db データベース接続オブジェクト
'''
def get_db():
    if 'db' not in g:
        try:
            g.db = sqlite3.connect(DATABASE) # データベースに接続
        except sqlite3.Error as e:
            logging.error(f"データベース接続エラー: {e}") # エラーをログに記録
            raise
    return g.db

'''
    各ゴミの種類の量とその容量を基にパーセンテージを計算する関数
        引数: garbage_data 各ゴミの種類と数量のリスト
              capacity_data 各ゴミの種類とその容量のリスト
        戻り値: percentages パーセンテージのリスト
'''
def percentage(garbage_data, capacity_data):
    capacities = {row[0]: row[1] for row in capacity_data} # 容量データを辞書に変換
    percentages = []

    for garbage_type, count in garbage_data:
        capacity = capacities.get(garbage_type, 1)  # 0除算対策でデフォルト値を1に設定
        percentage = (count / capacity) * 100 # パーセンテージ計算
        percentages.append((garbage_type, count, capacity, percentage)) # 結果をリストに追加
    
    return percentages

'''
    アプリケーションコンテキスト終了時にデータベース接続を閉じる関数
        引数: exception 例外が発生した場合の情報
'''
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None) # グローバルオブジェクトからデータベース接続を取得
    if db is not None:
        db.close() # データベース接続を閉じる

'''
    アプリケーションの起動時のページを表示するルート
'''
@app.route('/')
def index():
    try:
        conn = get_db() # データベース接続を取得
        cursor = conn.cursor()

        # ゴミ箱データを取得
        cursor.execute("SELECT * FROM bins")
        bins = cursor.fetchall()
        
        notifications = [] # 通知リストを初期化

        for bin in bins:
            # ゴミの種類と数量を取得
            cursor.execute("SELECT type, count FROM garbage WHERE bin_id = ?", (bin[0],))
            garbage_data = cursor.fetchall()

            # 容量データを取得
            cursor.execute("SELECT type, capacity FROM capacities WHERE bin_id = ?", (bin[0],))
            capacity_data = cursor.fetchall()

            # パーセンテージ計算
            percentages = percentage(garbage_data, capacity_data)

            # 80%に達したゴミの種類をメッセージリストに追加
            message = [
                f"{garbage_type}が{percentage:.1f}%に達しています"
                for garbage_type, _, _, percentage in percentages if percentage >= 80
            ]

            # ゴミ箱とメッセージリストを追加
            notifications.append((bin, message))

    except sqlite3.Error as e:
        logging.error(f"ゴミ箱 取得エラー: {e}") # エラーをログに記録
        notifications = [] # エラー時通知リストを空にする

    return render_template('index.html', bins=notifications)

'''
    指定されたゴミ箱の詳細情報を表示するルート
        引数: bin_id ゴミ箱のID
'''
@app.route('/bin/<string:bin_id>')
def bin_details(bin_id):
    try:
        conn = get_db() # データベース接続を取得
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bins WHERE id = ?", (bin_id,))
        bin_data = cursor.fetchone() # 指定されたIDの情報を取得

        if bin_data is None:
            logging.error(f"ゴミ箱データが存在しません。") # エラーログ
            flash(f"ゴミ箱ID {bin_id} は存在しません。", 'warning')
            return redirect(url_for('index')) # 一覧ページにリダイレクト
        
        # ゴミの種類と数量を取得
        cursor.execute("SELECT type, count FROM garbage WHERE bin_id = ?", (bin_id,))
        garbage_data = cursor.fetchall()
        
        # 容量データを取得
        cursor.execute("SELECT type, capacity FROM capacities WHERE bin_id = ?", (bin_id,))
        capacity_data = cursor.fetchall()
        
        # パーセンテージ計算
        garbage_percentages = percentage(garbage_data, capacity_data)

    except sqlite3.Error as e:
        logging.error(f"ゴミ箱の詳細データ 取得エラー: {e}") # エラーをログに記録
        garbage_percentages = [] # エラー時パーセンテージリストを空にする
        flash("ゴミ箱の詳細を取得中にエラーが発生しました。", 'error')

    return render_template('bin_details.html', bin=bin_data, results=garbage_percentages)

'''
    新しいゴミ箱を登録するためのルート
'''
@app.route('/new_bin', methods=['GET', 'POST'])
def new_bin():
    error_message = None  # エラーメッセージの初期化
    if request.method == 'POST':
        bin_id = request.form['bin_id'] # フォームからIDを取得
        location = request.form['location'] # フォームから設置場所を取得

        try:
            conn = get_db() # データベース接続を取得
            c = conn.cursor()

            # 既にIDが存在するかをチェック
            c.execute('SELECT id FROM bins WHERE id = ?', (bin_id,))
            existing_bin = c.fetchone() # 既存のゴミ箱を取得

            if existing_bin:
                error_message = f"ゴミ箱ID {bin_id} は既に存在しています。" # エラーメッセージを設定
            else:
                # ゴミ箱を新規登録
                c.execute('INSERT INTO bins (id, location) VALUES (?, ?)', (bin_id, location))

                for garbage_type in GARBAGE_TYPES:
                    c.execute('INSERT INTO garbage (bin_id, type, count) VALUES (?, ?, ?)', (bin_id, garbage_type, 0)) # ゴミデータの初期化
                    c.execute('INSERT INTO capacities (bin_id, type, capacity) VALUES (?, ?, ?)', (bin_id, garbage_type, 10)) # 容量データの初期化(初期値10)

                conn.commit() # 変更をデータベースに反映
                logging.info(f"ゴミ箱 {bin_id} が新規登録されました。") # 成功ログ
                return redirect(url_for('index')) # 一覧ページにリダイレクト

        except sqlite3.Error as e:
            logging.error(f"SQLiteエラー: {e}") # エラーをログに記録
            error_message = "新しいゴミ箱の登録中にエラーが発生しました。" # エラーメッセージを設定

        finally:
            if conn:
                conn.close()  # データベース接続を閉じる

    return render_template('new_bin.html', error_message=error_message)

'''
    IDからゴミ箱を検索するためのルート
'''
@app.route('/search_bin', methods=['GET', 'POST'])
def search_bin():
    try:
        conn = get_db()  # データベース接続を取得
        c = conn.cursor()
        bin_data = None
        error_message = None

        if request.method == 'POST':
            bin_id = request.form.get('searched_bin_id', '')  # フォームからゴミ箱IDを取得

            if not bin_id:
                return "ゴミ箱IDが必要です", 400

            # 指定されたゴミ箱IDのデータを検索
            c.execute('SELECT id, location FROM bins WHERE id = ?', (bin_id,))
            bin_data = c.fetchone()

            if bin_data:
                return redirect(url_for('bin_details', bin_id=bin_id))  # 詳細ページにリダイレクト
            else:
                error_message = f"ゴミ箱ID {bin_id} は存在しません。"  # エラーメッセージを設定

    except sqlite3.Error as e:
        logging.error(f"ゴミ箱検索エラー: {e}")  # エラーをログに記録
        error_message = "ゴミ箱検索中にエラーが発生しました。"  # エラーメッセージを表示

    finally:
        if conn:
            conn.close()  # データベース接続を閉じる

    return render_template('search_bin.html', error_message=error_message)

'''
    ゴミの量をリセットするためのルート
'''
@app.route('/reset_garbage', methods=['GET', 'POST'])
def reset_garbage():
    if request.method == 'POST':
        bin_id = request.form.get('bin_id')  # フォームからIDを取得
        garbage_types = request.form.getlist('garbage_types')  # フォームからゴミの種類を取得

        try:
            conn = get_db()  # データベース接続を取得
            c = conn.cursor()

            # 入力された bin_id がデータベースに存在するか確認
            c.execute('SELECT COUNT(1) FROM bins WHERE id = ?', (bin_id,))
            bin_exists = c.fetchone()[0]

            # bin_id が存在しない場合
            if not bin_exists:
                flash(f'ゴミ箱ID {bin_id} は存在しません。', 'warning')
                return redirect(url_for('reset_garbage'))

            # ゴミの種類が選択されていない場合（bin_idが存在する場合のみ）
            if not garbage_types:
                flash('ゴミの種類が選択されていません。', 'warning')
                return redirect(url_for('reset_garbage'))

            # 選択されたゴミの種類の量をリセット
            for garbage_type in garbage_types:
                c.execute('''
                    UPDATE garbage
                    SET count = 0
                    WHERE bin_id = ? AND type = ?
                ''', (bin_id, garbage_type))

            conn.commit()  # 変更をデータベースに反映
            flash('ゴミの量がリセットされました。', 'success')  # 成功メッセージ
        except sqlite3.Error as e:
            logging.error(f"ゴミのリセット中エラー: {e}")  # エラーをログに記録
            flash(f'エラーが発生しました: {e}', 'error')
        finally:
            if conn:
                conn.close()  # データベース接続を閉じる

        return redirect(url_for('reset_garbage'))

    return render_template('reset_garbage.html', garbage_types=GARBAGE_TYPES)

'''
    ゴミ箱の情報を編集するためのルート
'''
@app.route('/edit_bin', methods=['GET', 'POST'])
def edit_bin():
    conn = get_db() # データベース接続を取得
    c = conn.cursor()
    selected_bin_id = None
    bin_data = None
    capacity_data = None

    if request.method == 'POST':
         # フォームデータを取得
        selected_bin_id = request.form.get('selected_bin_id', None)
        new_bin_id = request.form.get('new_bin_id', None)
        new_capacity = request.form.get('new_capacity', None)
        new_location = request.form.get('new_location', None)
        action = request.form['action'] # 実行するアクションを取得

        if action == 'select_bin' and selected_bin_id:
            # ゴミ箱のIDと設置場所を取得
            try:
                c.execute('SELECT id, location FROM bins WHERE id = ?', (selected_bin_id,))
                bin_data = c.fetchone()

                c.execute('SELECT capacity FROM capacities WHERE bin_id = ?', (selected_bin_id,))
                capacity_data = c.fetchone()

                if not bin_data:
                    flash(f"ゴミ箱ID {selected_bin_id} は存在しません。", 'danger')
                    return render_template('edit_bin.html', selected_bin_id=selected_bin_id, bin_data=bin_data, capacity=capacity_data)
            except sqlite3.Error as e:
                flash(f"データ取得中にエラーが発生しました: {e}", 'danger')

        elif action == 'update_id' and selected_bin_id and new_bin_id:
            try:
                 # 新しいIDが既に存在しないか確認
                c.execute('SELECT id FROM bins WHERE id = ?', (new_bin_id,))
                if c.fetchone():
                    flash(f"新しいゴミ箱ID {new_bin_id} は既に存在します。", 'danger')
                    return render_template('edit_bin.html', selected_bin_id=selected_bin_id, bin_data=bin_data, capacity=capacity_data)

                 # IDの更新と関連するデータの更新
                c.execute('UPDATE bins SET id = ? WHERE id = ?', (new_bin_id, selected_bin_id))
                c.execute('UPDATE garbage SET bin_id = ? WHERE bin_id = ?', (new_bin_id, selected_bin_id))
                c.execute('UPDATE capacities SET bin_id = ? WHERE bin_id = ?', (new_bin_id, selected_bin_id))

                conn.commit() # 変更をデータベースに反映
                flash('ゴミ箱IDが更新されました。', 'success')
            except sqlite3.Error as e:
                flash(f"ゴミ箱IDの更新中にエラーが発生しました: {e}", 'danger')

        elif action == 'update_location' and selected_bin_id and new_location:
            try:
                # ゴミ箱の設置場所の更新
                c.execute('UPDATE bins SET location = ? WHERE id = ?', (new_location, selected_bin_id))
                conn.commit() # 変更をデータベースに反映
                flash('ゴミ箱の設置場所が更新されました。', 'success')
            except sqlite3.Error as e:
                flash(f"設置場所の更新中にエラーが発生しました: {e}", 'danger')

        elif action == 'update_capacity' and selected_bin_id and new_capacity:
            try:
                # ゴミ箱の容量の更新
                c.execute('UPDATE capacities SET capacity = ? WHERE bin_id = ?', (new_capacity, selected_bin_id))
                conn.commit() # 変更をデータベースに反映
                flash('ゴミ箱の容量が更新されました。', 'success')
            except sqlite3.Error as e:
                flash(f"容量の更新中にエラーが発生しました: {e}", 'danger')

        elif action == 'delete' and selected_bin_id:
            try:
                # データの削除
                c.execute('DELETE FROM garbage WHERE bin_id = ?', (selected_bin_id,))
                c.execute('DELETE FROM capacities WHERE bin_id = ?', (selected_bin_id,))
                c.execute('DELETE FROM bins WHERE id = ?', (selected_bin_id,))
                conn.commit()
                flash(f'ゴミ箱 {selected_bin_id} が削除されました。', 'success')
            except sqlite3.Error as e:
                flash(f'削除中にエラーが発生しました: {e}', 'danger')
            finally:
                 # 削除後、選択されたIDとデータをクリア
                selected_bin_id = None
                bin_data = None
                capacity_data = None

    if selected_bin_id:
         # 選択されたIDと設置場所を再取得
        try:
            c.execute('SELECT id, location FROM bins WHERE id = ?', (selected_bin_id,))
            bin_data = c.fetchone()

            c.execute('SELECT capacity FROM capacities WHERE bin_id = ?', (selected_bin_id,))
            capacity_data = c.fetchone()
        except sqlite3.Error as e:
            flash(f"データ再取得中にエラーが発生しました: {e}", 'danger')

    return render_template('edit_bin.html', selected_bin_id=selected_bin_id, bin_data=bin_data, capacity=capacity_data)

'''
    ヘルプページのルート
'''
@app.route('/help')
def help():
    return render_template('help.html')

'''
    音神経衰弱のルート
'''
@app.route('/memory_game')
def memory_game():
    return render_template('memory_game.html')

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=4000, debug=True) # アプリケーションの起動
    except Exception as e:
        print(f"アプリケーションの起動中にエラーが発生しました: {e}")
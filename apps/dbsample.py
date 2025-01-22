from flask import Flask, render_template
import psycopg2
import psycopg2.extras

# Flask作成
app = Flask(__name__)

@app.route('/')
def main():

    # PostgreSQL Serverとの接続を定義
    conn = psycopg2.connect(
        host='192.168.1.92',
        port=5432,
        database='postgres',
        user='postgres',
        password='postgres',
    )

    # PostgreSQL Serverと接続を作成
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # SQLを投入して情報取得
    cur.execute('select * from example')
    # 結果を取得
    rows = cur.fetchall()
    for row in rows:
        print(row)
    # 接続終了
    conn.close()

    # データをhtmlに渡して表示
    return render_template(
        'flask_to_postgresql.html',
        title='Flask PostgreSQL',
        dataset=rows
    )
    
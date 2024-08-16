from flask import Flask, render_template
from dotenv import load_dotenv
from yaml import safe_load
from logging import getLogger
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy

# 環境変数を.envで上書き
load_dotenv(override=True)

# 設定ファイルを読み込み
with open('./apps/application.yml') as yml:
    config = safe_load(yml)

# ロギングを設定する
dictConfig(config['logging'])

# アプリケーションのインスタンスを生成する
app = Flask(__name__, static_folder='./static', template_folder='./templates')

# DBエンジンを生成する
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    config['database']['user'],
    config['database']['password'],
    config['database']['host'],
    config['database']['port'],
    config['database']['name']
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = False
engine = SQLAlchemy(app)

"""
Exampleモデル
    動作確認用テーブルを操作する
"""
class Example(engine.Model):
    __tablename__ = 'example'
    __table_args__ = {"schema":"app"}

    id = engine.Column(primary_key=True, autoincrement=True)

"""
アプリケーションを実行する
Returns:
    トップページを表示する
"""
@app.route('/')
def main():
    # 動作確認用テーブルの全レコードを取得する
    query = engine.session.query(Example).where(Example.id == '2').first()

    # ログに書き込む
    logger = getLogger()
    logger.info(query)

    return render_template('index.html')

# おまじない
if __name__ == '__main__':
    app.run()
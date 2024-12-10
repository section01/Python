from flask import Flask, render_template, request
from dotenv import load_dotenv
from yaml import safe_load
from logging import getLogger
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, and_

import datetime

# 環境読込
load_dotenv(override=True)

# コンフィグ読込
with open('./apps/application.yml') as yml:
    config = safe_load(yml)

# Flaskインスタンス作成
app = Flask(__name__, static_folder='./public', template_folder='./views')

# ロギング
dictConfig(config['logging'])
logger = getLogger(__name__)

# DB接続
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    config['database']['user'],
    config['database']['password'],
    config['database']['host'],
    config['database']['port'],
    config['database']['name'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
engine = SQLAlchemy(app)

# ルートパス
@app.route('/')
def main():
    return render_template('kintai-input.html')

# おまじない
if __name__ == '__main__':
    app.run(debug=True)

# モデル基底クラス
class Serializer(object):
    __table_args__ = { 'schema': 'python', 'quote': False }

# 勤怠表モデルクラス
class Kintai(engine.Model, Serializer):
    __tablename__ = 'Kintai'

    # 勤怠ID
    kintai_id = engine.Column('kintai_id', engine.Sequence('Kintai_kintai_id'), primary_key=True)
    # 従業員ID
    employee_id = engine.Column('employee_id', engine.Sequence('Kintai_employee_id'))
    # 出勤日
    date = engine.Column('date', engine.Date)
    # 始業
    start = engine.Column('start', engine.Time)
    # 終業
    close = engine.Column('close', engine.Time)
    # 休憩
    rest = engine.Column('rest', engine.Time)
    # 備考
    remark = engine.Column('remark', engine.String(256))
    # 削除フラグ
    delete_flag = engine.Column('delete_flag', engine.Boolean)
    # 更新日
    update_at = engine.Column('update_at', engine.DateTime)
    # 作成日
    create_at = engine.Column('create_at', engine.DateTime)

# 勤怠入力画面クラス
class KintaiInput:

    # 初期表示
    @app.route('/kintai/input/init', methods=['GET'])
    def input_init():
        return render_template('kintai-input.html')

# 勤怠照会画面クラス
class KintaiInquire:

    # 初期表示
    @app.route('/kintai/inquire/init', methods=['GET'])
    def init():
        # 勤怠テーブル検索
        date = datetime.datetime.now()
        list = KintaiInquire.findKintai('1', date.year, date.month)

        return render_template('kintai-inquire.html', list=list)

    # 照会
    @app.route('/kintai/inquire/search', methods=['POST'])
    def search():
        # バリデーションチェック
        if not request.form['condition']:
            return render_template('kintai-inquire.html', msg = '出勤年月を入力して下さい。')

        # 勤怠テーブル検索
        date = request.form['condition'].split('-')
        list = KintaiInquire.findKintai('1', date[0], date[1])
        
        return render_template('kintai-inquire.html', list=list)

    # 勤怠テーブル検索
    # @param employee_id -> ログインユーザの従業員ID
    # @param year -> 検索年
    # @param month -> 検索月
    # @return ヒットした勤怠データ
    def findKintai(employee_id, year, month):
        return Kintai.query.with_entities(
                Kintai.date.label('date'),
                Kintai.start.label('start'),
                Kintai.close.label('close'),
                Kintai.rest.label('rest'),
                Kintai.remark.label('remark')) \
            .filter(Kintai.employee_id == employee_id) \
            .filter(and_(extract('year', Kintai.date) == year, extract('month', Kintai.date) == month)) \
            .all()

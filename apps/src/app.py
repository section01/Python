from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, and_
from dotenv import load_dotenv
from yaml import safe_load
from logging import getLogger
from logging.config import dictConfig
import datetime

# 環境情報をenvで上書き可能にする
load_dotenv(override=True)

# application.ymlを読み込む
with open('./apps/application.yml') as yml:
    config = safe_load(yml)

# アプリケーションのインスタンスを取得する
app = Flask(__name__, static_folder='../public', template_folder='../views')

# データベースの接続情報を設定する
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    config['database']['user'],
    config['database']['password'],
    config['database']['host'],
    config['database']['port'],
    config['database']['name'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True

# データベースに接続する
db = SQLAlchemy(app)

# ロガーを取得する
dictConfig(config['logging'])
log = getLogger(__name__)

# 基底モデル
class Serializer(object):
    __table_args__ = { 'schema': 'python', 'quote': True }

# 勤怠表モデル
class Kintai(db.Model, Serializer):
    __tablename__ = 'Kintai'

    # 勤怠ID
    kintai_id = db.Column('kintai_id', db.Sequence('Kintai_kintai_id_seq', schema='python', start=1, increment=1), primary_key=True)
    # 従業員ID
    employee_id = db.Column('employee_id', db.String(32))
    # 出勤日
    date = db.Column('date', db.Date)
    # 始業
    start = db.Column('start', db.Time)
    # 終業
    close = db.Column('close', db.Time)
    # 休憩
    rest = db.Column('rest', db.Time)
    # 備考
    remark = db.Column('remark', db.String(256))
    # 削除フラグ
    delete_flag = db.Column('delete_flag', db.Boolean)
    # 更新日
    update_at = db.Column('update_at', db.DateTime)
    # 作成日
    create_at = db.Column('create_at', db.DateTime)

# アプリケーションを実行する
@app.route('/')
def main():
    return render_template('kintai-input.html')

# おまじない
if __name__ == '__main__':
    app.run(debug=True)

# 勤怠入力画面
class KintaiInput:

    # 初期表示
    @app.route('/kintai/input', methods=['GET'])
    def input_init():
        return render_template('kintai-input.html')

    # 登録ボタンが押下された場合
    @app.route('/kintai/input/entry', methods=['POST'])
    def input_entry():
        msg = []
        if not request.form['date']:
            msg.append('出勤年月日を入力して下さい。')
        if not request.form['start']:
            msg.append('始業時間を入力して下さい。')
        if not request.form['close']:
            msg.append('終業時間を入力して下さい。')
        if not request.form['rest']:
            msg.append('休憩時間を入力して下さい。')

        if len(msg) > 0:
            return render_template('kintai-input.html', msg = msg)

        newKintai = Kintai(
            employee_id = '1',
            date = request.form['date'],
            start = request.form['start'],
            close = request.form['close'],
            rest = request.form['rest'],
            remark = request.form['remark'],
            delete_flag = False
        )

        db.session.add(newKintai)
        db.session.flush()
        db.session.commit()

        return render_template('kintai-input.html')

# 勤怠照会画面
class KintaiInquire:

    # 初期表示
    @app.route('/kintai/inquire', methods=['GET'])
    def inquire_init():
        date = datetime.datetime.now()
        list = KintaiInquire.findKintai(Kintai, '1', date.year, date.month)

        return render_template('kintai-inquire.html', list=list)

    # 検索ボタンが押下された場合
    @app.route('/kintai/inquire/search', methods=['POST'])
    def inquire_search():
        if not request.form['condition']:
            return render_template('kintai-inquire.html', msg = '出勤年月を入力して下さい。')
        
        date = request.form['condition'].split('-')
        list = KintaiInquire.findKintai(Kintai, '1', date[0], date[1])
        
        return render_template('kintai-inquire.html', list=list)

    # 勤怠テーブルを検索
    def findKintai(Kintai, employee_id, year, month):
        return Kintai.query.with_entities(
                Kintai.date.label('date'),
                Kintai.start.label('start'),
                Kintai.close.label('close'),
                Kintai.rest.label('rest'),
                Kintai.remark.label('remark')) \
            .filter(Kintai.employee_id == employee_id) \
            .filter(and_(extract('year', Kintai.date) == year, extract('month', Kintai.date) == month)) \
            .all()

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

# DB定義
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    config['database']['user'],
    config['database']['password'],
    config['database']['host'],
    config['database']['port'],
    config['database']['name'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
engine = SQLAlchemy(app)

class Serializer(object):
    __table_args__ = { 'schema': 'python' }

class Kintai(engine.Model, Serializer):
    __tablename__ = "Kintai"

    kintai_id = engine.Column('kintai_id', engine.Sequence('Kintai_kintai_id'), primary_key=True)
    employee_id = engine.Column('employee_id', engine.Sequence('Kintai_employee_id'))
    date = engine.Column('date', engine.Date)
    start = engine.Column('start', engine.Time)
    close = engine.Column('close', engine.Time)
    rest = engine.Column('rest', engine.Time)
    remark = engine.Column('remark', engine.String(256))
    delete_flag = engine.Column('delete_flag', engine.Boolean)
    update_at = engine.Column('update_at', engine.DateTime)
    create_at = engine.Column('create_at', engine.DateTime)

# ルートパス
@app.route('/')
def main():
    return render_template('kintai-input.html')

# TODO ファイル分割が分からなかったのでとりあえず定義
# 勤怠登録
@app.route('/kintai/input_init', methods=['GET'])
def input_init():
    return render_template('kintai-input.html')

# 勤怠検索
@app.route('/kintai/search_init', methods=['GET'])
def search_init():
    date = datetime.datetime.now()

    list = Kintai.query \
        .with_entities(
            Kintai.date.label('date'),
            Kintai.start.label('start'),
            Kintai.close.label('close'),
            Kintai.rest.label('rest'),
            Kintai.remark.label('remark')) \
        .filter(Kintai.employee_id == '1') \
        .filter(and_(extract('year', Kintai.date) == date.year, extract('month', Kintai.date) == date.month)) \
        .all()

    return render_template('kintai-search.html', list=list)

@app.route('/kintai/search_find', methods=['POST'])
def search_find():
    date = request.form['condition'].split('-')
    print(date)
    year = date[0]
    month = date[1]

    list = Kintai.query \
        .with_entities(
            Kintai.date.label('date'),
            Kintai.start.label('start'),
            Kintai.close.label('close'),
            Kintai.rest.label('rest'),
            Kintai.remark.label('remark')) \
        .filter(Kintai.employee_id == '1') \
        .filter(and_(extract('year', Kintai.date) == year, extract('month', Kintai.date) == month)) \
        .all()
    
    return render_template('kintai-search.html', list=list)

# おまじない
if __name__ == '__main__':
    app.run(debug=True)

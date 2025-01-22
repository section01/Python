from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from yaml import safe_load
from logging import getLogger
from logging.config import dictConfig
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect

load_dotenv(override=True)

with open('./apps/application.yml') as yml:
    config = safe_load(yml)

app = Flask(__name__, static_folder='./static', template_folder='./templates')
app.secret_key = 'employee'

dictConfig(config['logging'])
logger = getLogger(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    config['database']['user'],
    config['database']['password'],
    config['database']['host'],
    config['database']['port'],
    config['database']['name']
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
engine = SQLAlchemy(app)

class Serializer(object):
    __table_args__ = { 'schema':'python' }

class Example(engine.Model, Serializer):
    __tablename__ = 'example'

    id = engine.Column(primary_key=True, autoincrement=True)

@app.route('/')
def main():
    query = engine.session.query(Example).where(Example.id == '2').first()
    return render_template('login.html')

class Serializer(object):
    __table_args__ = { 'schema': 'python', 'quote': True }

#従業員TBL
class Employees(engine.Model, Serializer):
    __tablename__ = 'Employees'
    employee_id = engine.Column('employee_id', engine.Sequence('Employees_employee_id'), primary_key=True)
    email = engine.Column('email',engine.String(32))
    name = engine.Column('name',engine.String(64))
    role_id = engine.Column('role_id',engine.Integer)
    password = engine.Column('password',engine.String(10))
    delete_flag = engine.Column('delete_flag',engine.Boolean)
    update_at = engine.Column('update_at',engine.DateTime)
    create_at = engine.Column('create_at',engine.DateTime)

#ログイン認証
@app.route('/login_auth', methods=['POST'])
def login_auth():

    #入力された従業員IDとパスワードを取得
    req_employee_id = request.form['employee_id']
    req_password = request.form['password']

    #取得した従業員IDでDB検索し、一致したレコードのパスワードを1件取得
    user_ps = Employees.query.with_entities(
        Employees.password.label('password')) \
            .filter(Employees.employee_id == req_employee_id).first()

    #該当したパスワードの存在確認
    if user_ps :
    #存在する場合
        #パスワードを比較
        if req_password == user_ps.password :
        #一致した場合
            #従業員IDをセッションへ格納し、メニュー画面へ遷移　#TODO
            session["employee_id"] = req_employee_id
            return render_template('menu.html')

        #一致しない場合
        return render_template('login.html', variable='従業員IDまたはパスワードが間違っています。')

    #存在しない場合
    return render_template('login.html', variable='従業員IDまたはパスワードが間違っています。')

if __name__ == '__main__':
    app.run(debug=True)

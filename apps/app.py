from flask import Flask, render_template
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

    __table_args__ = {
        "schema":"app"
    }

    def serialize(self):
        return { c: getattr(self, c) for c in inspect(self).attrs.keys() }

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Example(engine.Model, Serializer):
    __tablename__ = 'example'

    id = engine.Column(primary_key=True, autoincrement=True)

@app.route('/')
def main():
    query = engine.session.query(Example).where(Example.id == '2').first()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

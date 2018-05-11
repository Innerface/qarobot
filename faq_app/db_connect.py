from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.mysql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db_session = db.create_scoped_session()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.close()



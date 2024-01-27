from flask_sqlalchemy import SQLAlchemy
import urllib.parse
from flask_marshmallow import Marshmallow


def initialize_db(app):
    # Connection to Azure SQL Database
    params = urllib.parse.quote_plus(
        "Driver={ODBC Driver 18 for SQL Server};Server=tcp:shs-genai-sql-01.database.windows.net,1433;Database=shs-genai-omr-01;Uid=sqldba;Pwd=P2ssw0rd!;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;")
    app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


db = SQLAlchemy()
ma = Marshmallow()

class Results(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamname = db.Column(db.String(255))
    score = db.Column(db.String(255))
    submitted_text = db.Column(db.String)

    def __init__(self, teamname, score, submitted_text):
        self.teamname = teamname
        self.score = score
        self.submitted_text = submitted_text

class ResultsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'teamname', 'score', 'submitted_text')        
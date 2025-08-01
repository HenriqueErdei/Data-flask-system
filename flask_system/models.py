from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cor_tema = db.Column(db.String(16), default="#ffd700")
    logo_path = db.Column(db.String(256), default=None)

class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=True)
    pode_estoque = db.Column(db.Boolean, default=False)
    pode_compras = db.Column(db.Boolean, default=False)
    pode_faturamento = db.Column(db.Boolean, default=False)
    pode_financeiro = db.Column(db.Boolean, default=False)
    pode_relatorios = db.Column(db.Boolean, default=False) 
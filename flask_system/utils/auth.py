from flask import session, redirect, url_for, flash
from ..models import User
from functools import wraps

def autenticar_usuario(username, senha):
    usuario = User.query.filter_by(username=username, password=senha).first()
    return usuario

def login_user(usuario):
    session['user_id'] = usuario.id
    session['username'] = usuario.username
    session['is_admin'] = getattr(usuario, 'is_admin', False)
    session['pode_estoque'] = getattr(usuario, 'pode_estoque', False)
    session['pode_compras'] = getattr(usuario, 'pode_compras', False)
    session['pode_faturamento'] = getattr(usuario, 'pode_faturamento', False)
    session['pode_financeiro'] = getattr(usuario, 'pode_financeiro', False)
    session['pode_relatorios'] = getattr(usuario, 'pode_relatorios', False)

def logout_user():
    session.clear()

def usuario_logado():
    return 'user_id' in session

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not usuario_logado() or not session.get('is_admin'):
            flash('Acesso restrito ao administrador.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not usuario_logado():
            flash('Faça login para acessar esta página.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

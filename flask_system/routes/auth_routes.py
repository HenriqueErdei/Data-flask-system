from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..utils.auth import autenticar_usuario, login_user, logout_user, login_required
from ..utils.logger import registrar_log

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['password']
        usuario = autenticar_usuario(username, senha)
        if usuario:
            login_user(usuario)
            registrar_log(f'Login realizado com sucesso.', usuario.username)
            flash('Login realizado com sucesso!')
            return redirect(url_for('auth.index'))
        else:
            flash('Usuário ou senha inválidos.')
    return render_template('auth/login.html')

@bp_auth.route('/logout')
@login_required
def logout():
    usuario = session.get('username')
    logout_user()
    registrar_log('Logout realizado.', usuario)
    flash('Logout realizado com sucesso!')
    return redirect(url_for('auth.login'))

@bp_auth.route('/')
@login_required
def index():
    return render_template('index.html') 
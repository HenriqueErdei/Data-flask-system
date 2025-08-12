from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from utils.auth import admin_required, login_user
from utils.logger import registrar_log
from models import User, db
import uuid
from werkzeug.utils import secure_filename
import os
from models import Settings

bp_admin = Blueprint('admin', __name__)

@bp_admin.route('/admin', methods=['GET', 'POST'])
@admin_required
def admin_index():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(cor_tema="#ffd700", logo_path=None)
        db.session.add(settings)
        db.session.commit()
    if request.method == 'POST':
        cor_tema = request.form.get('cor_tema', '#ffd700')
        logo_file = request.files.get('logo')
        if logo_file and logo_file.filename:
            filename = secure_filename(logo_file.filename)
            logo_path = os.path.join('static', 'logo', filename)
            abs_logo_path = os.path.join(current_app.root_path, logo_path)
            os.makedirs(os.path.dirname(abs_logo_path), exist_ok=True)
            logo_file.save(abs_logo_path)
            settings.logo_path = '/' + logo_path.replace('\\', '/')
        settings.cor_tema = cor_tema
        db.session.commit()
        flash('Customização salva com sucesso!')
        return redirect(url_for('admin.admin_index'))
    return render_template('admin/index.html', settings=settings)

@bp_admin.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@bp_admin.route('/admin/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def novo_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        is_admin = bool(request.form.get('is_admin'))
        pode_estoque = bool(request.form.get('pode_estoque'))
        pode_compras = bool(request.form.get('pode_compras'))
        pode_faturamento = bool(request.form.get('pode_faturamento'))
        pode_financeiro = bool(request.form.get('pode_financeiro'))
        pode_relatorios = bool(request.form.get('pode_relatorios'))
        usuario = User(id=str(uuid.uuid4()), username=username, password=password, email=email, is_admin=is_admin,
                       pode_estoque=pode_estoque, pode_compras=pode_compras, pode_faturamento=pode_faturamento, pode_financeiro=pode_financeiro, pode_relatorios=pode_relatorios)
        db.session.add(usuario)
        db.session.commit()
        registrar_log(f'Usuário cadastrado: {username}', session['username'])
        flash('Usuário cadastrado com sucesso!')
        return redirect(url_for('admin.admin_usuarios'))
    return render_template('admin/novo_usuario.html')

@bp_admin.route('/admin/usuarios/editar/<user_id>', methods=['GET', 'POST'])
@admin_required
def editar_usuario(user_id):
    usuario = User.query.get(user_id)
    if not usuario:
        flash('Usuário não encontrado.')
        return redirect(url_for('admin.admin_usuarios'))
    if request.method == 'POST':
        usuario.username = request.form['username']
        usuario.email = request.form['email']
        usuario.is_admin = bool(request.form.get('is_admin'))
        usuario.pode_estoque = bool(request.form.get('pode_estoque'))
        usuario.pode_compras = bool(request.form.get('pode_compras'))
        usuario.pode_faturamento = bool(request.form.get('pode_faturamento'))
        usuario.pode_financeiro = bool(request.form.get('pode_financeiro'))
        usuario.pode_relatorios = bool(request.form.get('pode_relatorios'))
        nova_senha = request.form['password']
        if nova_senha:
            usuario.password = nova_senha
        db.session.commit()
        # Atualiza a sessão se o usuário editado for o logado
        if usuario.id == session.get('user_id'):
            login_user(usuario)
        registrar_log(f'Usuário editado: {usuario.username}', session['username'])
        flash('Usuário atualizado com sucesso!')
        return redirect(url_for('admin.admin_usuarios'))
    return render_template('admin/editar_usuario.html', usuario=usuario)

@bp_admin.route('/admin/usuarios/remover/<user_id>', methods=['POST'])
@admin_required
def remover_usuario(user_id):
    usuario = User.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        registrar_log(f'Usuário removido: {user_id}', session['username'])
        flash('Usuário removido com sucesso!')
    return redirect(url_for('admin.admin_usuarios')) 
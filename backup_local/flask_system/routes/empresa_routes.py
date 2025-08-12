from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from utils.faturamento import get_dashboard_data
import pandas as pd, os
from utils.estoque import get_estoque_dashboard_data
from models import User
from .ia_routes import bp_ia

bp_empresa = Blueprint('empresa', __name__)

def usuario_logado():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

@bp_empresa.route('/faturamento')
def faturamento():
    usuario = usuario_logado()
    if not usuario or not usuario.pode_faturamento:
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('admin.admin_index'))
    dashboard = get_dashboard_data()
    # Carregar opções de filtro
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_faturamento.csv')
    df = pd.read_csv(csv_path, sep=';')
    df.columns = df.columns.str.strip()
    anos_disponiveis = sorted(df['Ano'].dropna().unique())
    filiais_disponiveis = sorted(df['Filial'].dropna().unique())
    categorias_disponiveis = sorted(df['Categoria'].dropna().unique())
    estados_disponiveis = sorted(df['Estado_Cliente'].dropna().unique())
    produtos_disponiveis = sorted(df['Produto'].dropna().unique())
    status_disponiveis = sorted(df['Status'].dropna().unique())
    return render_template('empresa/faturamento.html', **dashboard, anos_disponiveis=anos_disponiveis, filiais_disponiveis=filiais_disponiveis, categorias_disponiveis=categorias_disponiveis, estados_disponiveis=estados_disponiveis, produtos_disponiveis=produtos_disponiveis, status_disponiveis=status_disponiveis)

@bp_empresa.route('/compras')
def compras():
    usuario = usuario_logado()
    if not usuario or not usuario.pode_compras:
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('admin.admin_index'))
    return render_template('empresa/compras.html')

@bp_empresa.route('/estoque')
def estoque():
    usuario = usuario_logado()
    if not usuario or not usuario.pode_estoque:
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('admin.admin_index'))
    # Carregar dados iniciais e opções de filtro
    dashboard = get_estoque_dashboard_data()
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_estoque.csv')
    df = pd.read_csv(csv_path, sep=';')
    df.columns = df.columns.str.strip()
    filiais_disponiveis = sorted(df['Filial'].dropna().unique())
    categorias_disponiveis = sorted(df['Categoria'].dropna().unique())
    produtos_disponiveis = sorted(df['Produto'].dropna().unique())
    status_disponiveis = sorted(df['Status_Estoque'].dropna().unique())
    return render_template('empresa/estoque.html', **dashboard, filiais_disponiveis=filiais_disponiveis, categorias_disponiveis=categorias_disponiveis, produtos_disponiveis=produtos_disponiveis, status_disponiveis=status_disponiveis)

@bp_empresa.route('/financeiro')
def financeiro():
    usuario = usuario_logado()
    if not usuario or not usuario.pode_financeiro:
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('admin.admin_index'))
    return render_template('empresa/financeiro.html')

@bp_empresa.route('/relatorios')
def relatorios():
    usuario = usuario_logado()
    if not usuario or not usuario.pode_relatorios:
        flash('Você não tem permissão para acessar esta página.')
        return redirect(url_for('admin.admin_index'))
    return render_template('empresa/relatorios.html')

@bp_empresa.route('/faturamento/dados')
def faturamento_dados():
    ano = request.args.get('ano')
    filial = request.args.get('filial')
    categoria = request.args.get('categoria')
    estado = request.args.get('estado')
    produto = request.args.get('produto')
    status = request.args.get('status')
    dashboard = get_dashboard_data(ano=ano, filial=filial, categoria=categoria, estado=estado, produto=produto, status=status)
    return jsonify(dashboard)

@bp_empresa.route('/estoque/dados')
def estoque_dados():
    filial = request.args.get('filial')
    categoria = request.args.get('categoria')
    status = request.args.get('status')
    produto = request.args.get('produto')
    dashboard = get_estoque_dashboard_data(filial=filial, categoria=categoria, status=status, produto=produto)
    return jsonify(dashboard) 
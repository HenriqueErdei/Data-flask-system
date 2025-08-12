from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from ..utils.faturamento import get_dashboard_data
import os
from ..utils.estoque import get_estoque_dashboard_data
from ..models import User
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
    import csv
    anos_disponiveis = []
    filiais_disponiveis = []
    categorias_disponiveis = []
    estados_disponiveis = []
    produtos_disponiveis = []
    status_disponiveis = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                if cleaned_row.get('Ano') and cleaned_row['Ano'] not in anos_disponiveis:
                    anos_disponiveis.append(cleaned_row['Ano'])
                if cleaned_row.get('Filial') and cleaned_row['Filial'] not in filiais_disponiveis:
                    filiais_disponiveis.append(cleaned_row['Filial'])
                if cleaned_row.get('Categoria') and cleaned_row['Categoria'] not in categorias_disponiveis:
                    categorias_disponiveis.append(cleaned_row['Categoria'])
                if cleaned_row.get('Estado_Cliente') and cleaned_row['Estado_Cliente'] not in estados_disponiveis:
                    estados_disponiveis.append(cleaned_row['Estado_Cliente'])
                if cleaned_row.get('Produto') and cleaned_row['Produto'] not in produtos_disponiveis:
                    produtos_disponiveis.append(cleaned_row['Produto'])
                if cleaned_row.get('Status') and cleaned_row['Status'] not in status_disponiveis:
                    status_disponiveis.append(cleaned_row['Status'])
    except FileNotFoundError:
        pass
    
    return render_template('empresa/faturamento.html', **dashboard, 
                         anos_disponiveis=sorted(anos_disponiveis), 
                         filiais_disponiveis=sorted(filiais_disponiveis), 
                         categorias_disponiveis=sorted(categorias_disponiveis), 
                         estados_disponiveis=sorted(estados_disponiveis), 
                         produtos_disponiveis=sorted(produtos_disponiveis), 
                         status_disponiveis=sorted(status_disponiveis))

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
    import csv
    filiais_disponiveis = []
    categorias_disponiveis = []
    produtos_disponiveis = []
    status_disponiveis = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
                if cleaned_row.get('Filial') and cleaned_row['Filial'] not in filiais_disponiveis:
                    filiais_disponiveis.append(cleaned_row['Filial'])
                if cleaned_row.get('Categoria') and cleaned_row['Categoria'] not in categorias_disponiveis:
                    categorias_disponiveis.append(cleaned_row['Categoria'])
                if cleaned_row.get('Produto') and cleaned_row['Produto'] not in produtos_disponiveis:
                    produtos_disponiveis.append(cleaned_row['Produto'])
                if cleaned_row.get('Status_Estoque') and cleaned_row['Status_Estoque'] not in status_disponiveis:
                    status_disponiveis.append(cleaned_row['Status_Estoque'])
    except FileNotFoundError:
        pass
    
    return render_template('empresa/estoque.html', **dashboard, 
                         filiais_disponiveis=sorted(filiais_disponiveis), 
                         categorias_disponiveis=sorted(categorias_disponiveis), 
                         produtos_disponiveis=sorted(produtos_disponiveis), 
                         status_disponiveis=sorted(status_disponiveis))

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
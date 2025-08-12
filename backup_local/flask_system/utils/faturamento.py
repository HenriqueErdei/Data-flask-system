import pandas as pd
import os

def get_dashboard_data(ano=None, filial=None, categoria=None, estado=None, produto=None, status=None):
    # Caminho do CSV
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_faturamento.csv')
    df = pd.read_csv(csv_path, sep=';')
    df.columns = df.columns.str.strip()

    if ano:
        df = df[df['Ano'] == int(ano)]
    if filial:
        df = df[df['Filial'] == filial]
    if categoria:
        df = df[df['Categoria'] == categoria]
    if estado:
        df = df[df['Estado_Cliente'] == estado]
    if produto:
        df = df[df['Produto'] == produto]
    if status:
        df = df[df['Status'] == status]

    # Faturamento por ano
    faturamento_por_ano = df.groupby('Ano')['Total'].sum().to_dict()
    # Faturamento por mês (agregado de todos os anos)
    faturamento_por_mes = df.groupby('Mes')['Total'].sum().to_dict()
    # Faturamento por categoria
    faturamento_por_categoria = df.groupby('Categoria')['Total'].sum().sort_values(ascending=False).head(10).to_dict()
    # Faturamento por produto (top 10)
    faturamento_por_produto = df.groupby('Produto')['Total'].sum().sort_values(ascending=False).head(10).to_dict()
    # Faturamento por filial
    faturamento_por_filial = df.groupby('Filial')['Total'].sum().sort_values(ascending=False).head(10).to_dict()
    # Faturamento por estado
    faturamento_por_estado = df.groupby('Estado_Cliente')['Total'].sum().sort_values(ascending=False).head(10).to_dict()
    # Ticket médio por mês
    ticket_medio_por_mes = df.groupby('Mes')['Ticket_Medio'].mean().to_dict()
    # Devoluções por mês
    devolucoes = df[df['Status'] == 'Com Devolução']
    devolucoes_por_mes = devolucoes.groupby('Mes')['Status'].count().to_dict()

    return {
        'faturamento_por_ano': faturamento_por_ano,
        'faturamento_por_mes': faturamento_por_mes,
        'faturamento_por_categoria': faturamento_por_categoria,
        'faturamento_por_produto': faturamento_por_produto,
        'faturamento_por_filial': faturamento_por_filial,
        'faturamento_por_estado': faturamento_por_estado,
        'ticket_medio_por_mes': ticket_medio_por_mes,
        'devolucoes_por_mes': devolucoes_por_mes
    } 
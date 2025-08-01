import pandas as pd
import os

def get_estoque_dashboard_data(filial=None, categoria=None, status=None, produto=None):
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_estoque.csv')
    df = pd.read_csv(csv_path, sep=';')
    df.columns = df.columns.str.strip()

    if filial:
        df = df[df['Filial'] == filial]
    if categoria:
        df = df[df['Categoria'] == categoria]
    if status:
        df = df[df['Status_Estoque'] == status]
    if produto:
        df = df[df['Produto'] == produto]

    # Indicadores para cartões
    total_itens_estoque = int(df['Quantidade_Fisica'].sum())
    valor_total_estoque = float(df['CMC_Total'].sum())
    produtos_abaixo_minimo = int(df[df['Status_Estoque'] == 'Abaixo do Mínimo'].shape[0])
    produtos_unicos = int(df['Produto'].nunique())
    filiais_ativas = int(df['Filial'].nunique())
    categorias_distintas = int(df['Categoria'].nunique())

    # Gráficos (agora sem head(10))
    estoque_por_produto = df.groupby('Produto')['Quantidade_Fisica'].sum().sort_values(ascending=False).to_dict()
    estoque_por_categoria = df.groupby('Categoria')['Quantidade_Fisica'].sum().sort_values(ascending=False).to_dict()
    estoque_por_filial = df.groupby('Filial')['Quantidade_Fisica'].sum().sort_values(ascending=False).to_dict()
    estoque_por_status = df.groupby('Status_Estoque')['Quantidade_Fisica'].sum().to_dict()
    abaixo_minimo = df[df['Status_Estoque'] == 'Abaixo do Mínimo']
    produtos_abaixo_minimo_dict = abaixo_minimo.groupby('Produto')['Quantidade_Fisica'].sum().sort_values(ascending=True).to_dict()
    giro_por_produto = df.groupby('Produto')['Giro_Estoque'].sum().sort_values(ascending=False).to_dict()
    valor_total_por_filial = df.groupby('Filial')['CMC_Total'].sum().sort_values(ascending=False).to_dict()
    valor_total_por_categoria = df.groupby('Categoria')['CMC_Total'].sum().sort_values(ascending=False).to_dict()

    return {
        'total_itens_estoque': total_itens_estoque,
        'valor_total_estoque': valor_total_estoque,
        'produtos_abaixo_minimo': produtos_abaixo_minimo,
        'produtos_unicos': produtos_unicos,
        'filiais_ativas': filiais_ativas,
        'categorias_distintas': categorias_distintas,
        'estoque_por_produto': estoque_por_produto,
        'estoque_por_categoria': estoque_por_categoria,
        'estoque_por_filial': estoque_por_filial,
        'estoque_por_status': estoque_por_status,
        'produtos_abaixo_minimo_dict': produtos_abaixo_minimo_dict,
        'giro_por_produto': giro_por_produto,
        'valor_total_por_filial': valor_total_por_filial,
        'valor_total_por_categoria': valor_total_por_categoria
    } 
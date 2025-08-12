import csv
import os
from collections import defaultdict

def get_estoque_dashboard_data(filial=None, categoria=None, status=None, produto=None):
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_estoque.csv')
    
    # Ler CSV com csv.DictReader
    data = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            # Limpar espaços em branco das chaves
            cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
            
            # Aplicar filtros
            if filial and cleaned_row['Filial'] != filial:
                continue
            if categoria and cleaned_row['Categoria'] != categoria:
                continue
            if status and cleaned_row['Status_Estoque'] != status:
                continue
            if produto and cleaned_row['Produto'] != produto:
                continue
                
            data.append(cleaned_row)
    
    if not data:
        return {
            'total_itens_estoque': 0,
            'valor_total_estoque': 0.0,
            'produtos_abaixo_minimo': 0,
            'produtos_unicos': 0,
            'filiais_ativas': 0,
            'categorias_distintas': 0,
            'estoque_por_produto': {},
            'estoque_por_categoria': {},
            'estoque_por_filial': {},
            'estoque_por_status': {},
            'produtos_abaixo_minimo_dict': {},
            'giro_por_produto': {},
            'valor_total_por_filial': {},
            'valor_total_por_categoria': {}
        }
    
    # Calcular indicadores
    total_itens_estoque = sum(float(row['Quantidade_Fisica']) for row in data)
    valor_total_estoque = sum(float(row['CMC_Total']) for row in data)
    produtos_abaixo_minimo = sum(1 for row in data if row['Status_Estoque'] == 'Abaixo do Mínimo')
    produtos_unicos = len(set(row['Produto'] for row in data))
    filiais_ativas = len(set(row['Filial'] for row in data))
    categorias_distintas = len(set(row['Categoria'] for row in data))
    
    # Agregações
    estoque_por_produto = defaultdict(float)
    estoque_por_categoria = defaultdict(float)
    estoque_por_filial = defaultdict(float)
    estoque_por_status = defaultdict(float)
    produtos_abaixo_minimo_dict = defaultdict(float)
    giro_por_produto = defaultdict(float)
    valor_total_por_filial = defaultdict(float)
    valor_total_por_categoria = defaultdict(float)
    
    for row in data:
        qtd = float(row['Quantidade_Fisica'])
        valor = float(row['CMC_Total'])
        giro = float(row['Giro_Estoque'])
        
        estoque_por_produto[row['Produto']] += qtd
        estoque_por_categoria[row['Categoria']] += qtd
        estoque_por_filial[row['Filial']] += qtd
        estoque_por_status[row['Status_Estoque']] += qtd
        giro_por_produto[row['Produto']] += giro
        valor_total_por_filial[row['Filial']] += valor
        valor_total_por_categoria[row['Categoria']] += valor
        
        if row['Status_Estoque'] == 'Abaixo do Mínimo':
            produtos_abaixo_minimo_dict[row['Produto']] += qtd
    
    # Ordenar dicionários
    def sort_dict(d, reverse=True):
        return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))
    
    return {
        'total_itens_estoque': int(total_itens_estoque),
        'valor_total_estoque': valor_total_estoque,
        'produtos_abaixo_minimo': produtos_abaixo_minimo,
        'produtos_unicos': produtos_unicos,
        'filiais_ativas': filiais_ativas,
        'categorias_distintas': categorias_distintas,
        'estoque_por_produto': sort_dict(estoque_por_produto),
        'estoque_por_categoria': sort_dict(estoque_por_categoria),
        'estoque_por_filial': sort_dict(estoque_por_filial),
        'estoque_por_status': dict(estoque_por_status),
        'produtos_abaixo_minimo_dict': sort_dict(produtos_abaixo_minimo_dict, reverse=False),
        'giro_por_produto': sort_dict(giro_por_produto),
        'valor_total_por_filial': sort_dict(valor_total_por_filial),
        'valor_total_por_categoria': sort_dict(valor_total_por_categoria)
    } 
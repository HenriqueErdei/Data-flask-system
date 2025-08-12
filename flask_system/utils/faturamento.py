import csv
import os
from collections import defaultdict

def get_dashboard_data(ano=None, filial=None, categoria=None, estado=None, produto=None, status=None):
    # Caminho do CSV
    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios/base_faturamento.csv')
    
    # Ler CSV com csv.DictReader
    data = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            # Limpar espaços em branco das chaves
            cleaned_row = {k.strip(): v.strip() for k, v in row.items()}
            
            # Aplicar filtros
            if ano and int(cleaned_row['Ano']) != int(ano):
                continue
            if filial and cleaned_row['Filial'] != filial:
                continue
            if categoria and cleaned_row['Categoria'] != categoria:
                continue
            if estado and cleaned_row['Estado_Cliente'] != estado:
                continue
            if produto and cleaned_row['Produto'] != produto:
                continue
            if status and cleaned_row['Status'] != status:
                continue
                
            data.append(cleaned_row)
    
    if not data:
        return {
            'faturamento_por_ano': {},
            'faturamento_por_mes': {},
            'faturamento_por_categoria': {},
            'faturamento_por_produto': {},
            'faturamento_por_filial': {},
            'faturamento_por_estado': {},
            'ticket_medio_por_mes': {},
            'devolucoes_por_mes': {}
        }
    
    # Agregações
    faturamento_por_ano = defaultdict(float)
    faturamento_por_mes = defaultdict(float)
    faturamento_por_categoria = defaultdict(float)
    faturamento_por_produto = defaultdict(float)
    faturamento_por_filial = defaultdict(float)
    faturamento_por_estado = defaultdict(float)
    ticket_medio_por_mes = defaultdict(list)
    devolucoes_por_mes = defaultdict(int)
    
    for row in data:
        total = float(row['Total'])
        ticket_medio = float(row['Ticket_Medio'])
        
        faturamento_por_ano[row['Ano']] += total
        faturamento_por_mes[row['Mes']] += total
        faturamento_por_categoria[row['Categoria']] += total
        faturamento_por_produto[row['Produto']] += total
        faturamento_por_filial[row['Filial']] += total
        faturamento_por_estado[row['Estado_Cliente']] += total
        ticket_medio_por_mes[row['Mes']].append(ticket_medio)
        
        if row['Status'] == 'Com Devolução':
            devolucoes_por_mes[row['Mes']] += 1
    
    # Calcular ticket médio por mês
    ticket_medio_final = {}
    for mes, valores in ticket_medio_por_mes.items():
        ticket_medio_final[mes] = sum(valores) / len(valores)
    
    # Ordenar e limitar top 10
    def sort_dict_top10(d):
        sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_items[:10])
    
    return {
        'faturamento_por_ano': dict(faturamento_por_ano),
        'faturamento_por_mes': dict(faturamento_por_mes),
        'faturamento_por_categoria': sort_dict_top10(faturamento_por_categoria),
        'faturamento_por_produto': sort_dict_top10(faturamento_por_produto),
        'faturamento_por_filial': sort_dict_top10(faturamento_por_filial),
        'faturamento_por_estado': sort_dict_top10(faturamento_por_estado),
        'ticket_medio_por_mes': ticket_medio_final,
        'devolucoes_por_mes': dict(devolucoes_por_mes)
    } 
from flask import Blueprint, request, jsonify
import os
import requests
import pandas as pd
import re
import numpy as np

bp_ia = Blueprint('ia', __name__)

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def aplicar_filtros_faturamento(df, pergunta):
    """Detecta e aplica filtros relevantes para a base de faturamento."""
    filtros = {}
    # Ano
    ano_match = re.search(r'(?:ano de |em |no ano de |de |do ano de )?(20\d{2})', pergunta)
    if ano_match and 'Ano' in df.columns:
        filtros['Ano'] = int(ano_match.group(1))
    # Mês
    mes_match = re.search(r'(?:mes|mês|em|de)\s*(\d{1,2})[ /-](20\d{2})', pergunta)
    if mes_match and 'Mes' in df.columns and 'Ano' in df.columns:
        filtros['Mes'] = int(mes_match.group(1))
        filtros['Ano'] = int(mes_match.group(2))
    # Data específica
    data_match = re.search(r'(\d{2}/\d{2}/\d{4})|(\d{4}-\d{2}-\d{2})', pergunta)
    if data_match and 'Data_Compra' in df.columns:
        data_str = data_match.group(1) or data_match.group(2)
        try:
            data_norm = pd.to_datetime(data_str, dayfirst=True).strftime('%Y-%m-%d')
            filtros['Data_Compra'] = data_norm
        except Exception:
            pass
    # Filial
    filial_match = re.search(r'filial\s*([\w\s]+)', pergunta, re.IGNORECASE)
    if filial_match and 'Filial' in df.columns:
        filtros['Filial'] = filial_match.group(1).strip()
    # Produto
    prod_match = re.search(r'produto\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if prod_match and 'Produto' in df.columns:
        filtros['Produto'] = prod_match.group(1).strip()
    # Categoria
    cat_match = re.search(r'categoria\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if cat_match and 'Categoria' in df.columns:
        filtros['Categoria'] = cat_match.group(1).strip()
    # Status
    if 'com devolução' in pergunta.lower() and 'Status' in df.columns:
        filtros['Status'] = 'Com Devolução'
    if 'sem devolução' in pergunta.lower() and 'Status' in df.columns:
        filtros['Status'] = 'Sem Devolução'
    # Estado_Cliente
    est_match = re.search(r'estado\s*([\w\s\-\(\)]+)', pergunta, re.IGNORECASE)
    if est_match and 'Estado_Cliente' in df.columns:
        filtros['Estado_Cliente'] = est_match.group(1).strip()
    # Nome_Cliente
    cli_match = re.search(r'cliente\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if cli_match and 'Nome_Cliente' in df.columns:
        filtros['Nome_Cliente'] = cli_match.group(1).strip()
    # Nome_Vendedor
    vend_match = re.search(r'vendedor\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if vend_match and 'Nome_Vendedor' in df.columns:
        filtros['Nome_Vendedor'] = vend_match.group(1).strip()
    # Aplica filtros
    df_filtrado = df.copy()
    for col, val in filtros.items():
        if col in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col].astype(str).str.lower() == str(val).lower()]
    return df_filtrado, filtros

def aplicar_filtros_estoque(df, pergunta):
    """Detecta e aplica filtros relevantes para a base de estoque."""
    filtros = {}
    # Filial
    filial_match = re.search(r'filial\s*([\w\s]+)', pergunta, re.IGNORECASE)
    if filial_match and 'Filial' in df.columns:
        filtros['Filial'] = filial_match.group(1).strip()
    # Produto
    prod_match = re.search(r'produto\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if prod_match and 'Produto' in df.columns:
        filtros['Produto'] = prod_match.group(1).strip()
    # Categoria
    cat_match = re.search(r'categoria\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if cat_match and 'Categoria' in df.columns:
        filtros['Categoria'] = cat_match.group(1).strip()
    # Status_Estoque
    status_match = re.search(r'status\s*([\w\s\-]+)', pergunta, re.IGNORECASE)
    if status_match and 'Status_Estoque' in df.columns:
        filtros['Status_Estoque'] = status_match.group(1).strip()
    if 'abaixo do mínimo' in pergunta.lower() and 'Status_Estoque' in df.columns:
        filtros['Status_Estoque'] = 'Abaixo do Mínimo'
    if 'normal' in pergunta.lower() and 'Status_Estoque' in df.columns:
        filtros['Status_Estoque'] = 'Normal'
    # Data_Ultima_Entrada
    data_ult_match = re.search(r'(\d{2}/\d{2}/\d{4})|(\d{4}-\d{2}-\d{2})', pergunta)
    if data_ult_match and 'Data_Ultima_Entrada' in df.columns:
        data_str = data_ult_match.group(1) or data_ult_match.group(2)
        try:
            data_norm = pd.to_datetime(data_str, dayfirst=True).strftime('%Y-%m-%d')
            filtros['Data_Ultima_Entrada'] = data_norm
        except Exception:
            pass
    # Validade
    val_match = re.search(r'validade\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', pergunta)
    if val_match and 'Validade' in df.columns:
        data_str = val_match.group(1)
        try:
            data_norm = pd.to_datetime(data_str, dayfirst=True).strftime('%Y-%m-%d')
            filtros['Validade'] = data_norm
        except Exception:
            pass
    # Aplica filtros
    df_filtrado = df.copy()
    for col, val in filtros.items():
        if col in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col].astype(str).str.lower() == str(val).lower()]
    return df_filtrado, filtros

def gerar_resumo_robusto_faturamento(df):
    """Gera um resumo completo para perguntas genéricas de faturamento."""
    resumo = ''
    if 'Ano' in df.columns and 'Total' in df.columns:
        total_ano = df.groupby('Ano')['Total'].sum()
        resumo += f"Total por ano:\n{total_ano.to_string()}\n"
    if 'Ano' in df.columns and 'Mes' in df.columns and 'Total' in df.columns:
        total_mes = df.groupby(['Ano', 'Mes'])['Total'].sum().sort_index(ascending=False)
        resumo += f"Total por mês (Ano/Mês):\n{total_mes.head(12).to_string()}\n"
    if 'Produto' in df.columns and 'Total' in df.columns:
        top_prod = df.groupby('Produto')['Total'].sum().sort_values(ascending=False)
        resumo += f"Top 10 produtos por faturamento:\n{top_prod.head(10).to_string()}\n"
    if 'Categoria' in df.columns and 'Total' in df.columns:
        top_cat = df.groupby('Categoria')['Total'].sum().sort_values(ascending=False)
        resumo += f"Top 10 categorias por faturamento:\n{top_cat.head(10).to_string()}\n"
    if 'Filial' in df.columns and 'Total' in df.columns:
        top_filial = df.groupby('Filial')['Total'].sum().sort_values(ascending=False)
        resumo += f"Top 5 filiais por faturamento:\n{top_filial.head(5).to_string()}\n"
    if 'Ticket_Medio' in df.columns:
        resumo += f"Ticket médio geral: {df['Ticket_Medio'].mean():.2f}\n"
    if 'Total' in df.columns:
        resumo += f"Faturamento máximo de uma venda: {df['Total'].max():.2f}\n"
        resumo += f"Faturamento mínimo de uma venda: {df['Total'].min():.2f}\n"
    return resumo

def gerar_resumo_robusto_estoque(df):
    """Gera um resumo completo para perguntas genéricas de estoque."""
    resumo = ''
    if 'Produto' in df.columns and 'Quantidade_Fisica' in df.columns:
        top_prod = df.groupby('Produto')['Quantidade_Fisica'].sum().sort_values(ascending=False)
        resumo += f"Top 10 produtos por quantidade física:\n{top_prod.head(10).to_string()}\n"
    if 'Categoria' in df.columns and 'Quantidade_Fisica' in df.columns:
        top_cat = df.groupby('Categoria')['Quantidade_Fisica'].sum().sort_values(ascending=False)
        resumo += f"Top 10 categorias por quantidade física:\n{top_cat.head(10).to_string()}\n"
    if 'Filial' in df.columns and 'Quantidade_Fisica' in df.columns:
        top_filial = df.groupby('Filial')['Quantidade_Fisica'].sum().sort_values(ascending=False)
        resumo += f"Top 5 filiais por quantidade física:\n{top_filial.head(5).to_string()}\n"
    if 'Quantidade_Fisica' in df.columns:
        resumo += f"Quantidade física total: {df['Quantidade_Fisica'].sum()}\n"
        resumo += f"Quantidade máxima de um produto: {df['Quantidade_Fisica'].max()}\n"
        resumo += f"Quantidade mínima de um produto: {df['Quantidade_Fisica'].min()}\n"
    return resumo

@bp_ia.route('/api/ia_chat', methods=['POST'])
def ia_chat():
    data = request.json
    if not data:
        print('[IA_CHAT] Requisição inválida: corpo vazio')
        return jsonify({'erro': 'Requisição inválida'}), 400
    pergunta = data.get('pergunta')
    modulo = data.get('modulo')
    filtros = data.get('filtros', {})

    print(f'[IA_CHAT] Chave Gemini: {GEMINI_API_KEY}')
    print(f'[IA_CHAT] Pergunta: {pergunta} | Módulo: {modulo}')

    csv_map = {
        'estoque': 'base_estoque.csv',
        'faturamento': 'base_faturamento.csv',
        'compras': 'base_compras.csv',
        'financeiro': 'base_financeiro.csv'
    }
    csv_file = csv_map.get(modulo)
    if not csv_file:
        print('[IA_CHAT] Módulo inválido:', modulo)
        return jsonify({'erro': 'Módulo inválido'}), 400

    csv_path = os.path.join(os.path.dirname(__file__), '../relatorios', csv_file)
    print(f'[IA_CHAT] Caminho do CSV: {csv_path}')
    if not os.path.exists(csv_path):
        print('[IA_CHAT] Arquivo CSV não encontrado:', csv_path)
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

    file_size = os.path.getsize(csv_path)
    print(f'[IA_CHAT] Tamanho do CSV: {file_size} bytes')
    df = pd.read_csv(csv_path, sep=';')
    contexto = f"Colunas: {', '.join(df.columns)}\n"

    filtro_aplicado = False
    resumo = ''
    filtros_detectados = {}
    # Aplica filtros conforme o módulo
    if modulo == 'faturamento':
        df_filtrado, filtros_detectados = aplicar_filtros_faturamento(df, pergunta)
    elif modulo == 'estoque':
        df_filtrado, filtros_detectados = aplicar_filtros_estoque(df, pergunta)
    else:
        df_filtrado = df.copy()
    # Se algum filtro foi aplicado e resultou em linhas
    if len(filtros_detectados) > 0 and not df_filtrado.empty:
        filtro_aplicado = True
        resumo = f"Resumo filtrado para os critérios {filtros_detectados}:\n"
        # Se houver coluna Total, soma
        if 'Total' in df_filtrado.columns:
            total = df_filtrado['Total'].sum()
            resumo += f"Total: {total:.2f}\n"
        # Se houver coluna Quantidade_Fisica, soma
        if 'Quantidade_Fisica' in df_filtrado.columns:
            qtd = df_filtrado['Quantidade_Fisica'].sum()
            resumo += f"Quantidade Física: {qtd}\n"
        # --- NOVO: Detecta perguntas de ranking/top e gera ranking ---
        ranking_gerado = False
        if modulo == 'faturamento' and 'produto' in pergunta.lower() and any(p in pergunta.lower() for p in ['mais', 'maior', 'top']):
            if 'Produto' in df_filtrado.columns and 'Total' in df_filtrado.columns:
                ranking = df_filtrado.groupby('Produto')['Total'].sum().sort_values(ascending=False)
                resumo += f"\nRanking de produtos por faturamento:\n{ranking.head(10).to_string()}\n"
                ranking_gerado = True
        if modulo == 'faturamento' and 'categoria' in pergunta.lower() and any(p in pergunta.lower() for p in ['mais', 'maior', 'top']):
            if 'Categoria' in df_filtrado.columns and 'Total' in df_filtrado.columns:
                ranking = df_filtrado.groupby('Categoria')['Total'].sum().sort_values(ascending=False)
                resumo += f"\nRanking de categorias por faturamento:\n{ranking.head(10).to_string()}\n"
                ranking_gerado = True
        if modulo == 'faturamento' and 'filial' in pergunta.lower() and any(p in pergunta.lower() for p in ['mais', 'maior', 'top']):
            if 'Filial' in df_filtrado.columns and 'Total' in df_filtrado.columns:
                ranking = df_filtrado.groupby('Filial')['Total'].sum().sort_values(ascending=False)
                resumo += f"\nRanking de filiais por faturamento:\n{ranking.head(5).to_string()}\n"
                ranking_gerado = True
        # Para estoque: ranking de produtos por quantidade física
        if modulo == 'estoque' and 'produto' in pergunta.lower() and any(p in pergunta.lower() for p in ['mais', 'maior', 'top']):
            if 'Produto' in df_filtrado.columns and 'Quantidade_Fisica' in df_filtrado.columns:
                ranking = df_filtrado.groupby('Produto')['Quantidade_Fisica'].sum().sort_values(ascending=False)
                resumo += f"\nRanking de produtos por quantidade física:\n{ranking.head(10).to_string()}\n"
                ranking_gerado = True
        contexto += resumo + '\n'
    else:
        # Fallback: sempre envia resumo robusto se não houver filtro claro ou resultado
        if modulo == 'faturamento':
            contexto += gerar_resumo_robusto_faturamento(df)
        elif modulo == 'estoque':
            contexto += gerar_resumo_robusto_estoque(df)
        elif file_size <= 100_000:
            contexto += f"Dados completos:\n{df.to_string(index=False)}\n"
        else:
            data_col = None
            for col in df.columns:
                if 'ano' in col.lower() or 'data' in col.lower():
                    data_col = col
                    break
            resumo = ''
            if data_col:
                try:
                    if df[data_col].dtype == 'O' and any('-' in str(x) for x in df[data_col].head(10)):
                        df['__ano'] = pd.to_datetime(df[data_col], errors='coerce').dt.year
                        group_col = '__ano'
                    else:
                        group_col = data_col
                    num_cols = df.select_dtypes(include='number').columns
                    resumo_df = df.groupby(group_col)[num_cols].sum().reset_index()
                    resumo = resumo_df.to_string(index=False)
                    contexto += f"Resumo por {group_col}:\n{resumo}\n"
                except Exception as e:
                    contexto += f"Não foi possível resumir por ano/data. Exibindo primeiras linhas:\n{df.head(10).to_string(index=False)}\n"
            else:
                contexto += f"Primeiras linhas:\n{df.head(10).to_string(index=False)}\n"

    # Log pergunta e filtros aplicados
    print(f'[IA_CHAT] Filtros detectados: {filtros_detectados}')
    print(f'[IA_CHAT] Resumo enviado para IA:\n{contexto[:1000]}...')

    prompt = f"""
Você é um assistente especializado no módulo {modulo.upper()}. Responda apenas perguntas baseadas nos dados abaixo.
Se a pergunta não puder ser respondida com esses dados, diga: 'Não tenho essa informação nos dados fornecidos.'
NÃO invente informações. NÃO responda perguntas fora do escopo do módulo {modulo}.

DADOS DISPONÍVEIS:\n{contexto}
Pergunta do usuário: {pergunta}
"""

    print('[IA_CHAT] Enviando requisição para Gemini...')
    response = requests.post(
        GEMINI_URL,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY
        }
    )
    print(f'[IA_CHAT] Status Gemini: {response.status_code}')
    if response.status_code != 200:
        print('[IA_CHAT] Corpo da resposta Gemini:', response.text)
        return jsonify({'erro': 'Erro na IA'}), 500

    resposta = response.json()['candidates'][0]['content']['parts'][0]['text']
    print('[IA_CHAT] Resposta Gemini:', resposta)
    return jsonify({'resposta': resposta}) 
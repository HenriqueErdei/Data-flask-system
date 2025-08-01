# Dataview Flask System

Este é um sistema web simples feito com Flask, utilizando SQLite como banco de dados relacional. O sistema permite:

- Cadastro, edição e remoção de usuários
- Login e autenticação de usuários (com distinção de admin)
- Definição de permissões de acesso por usuário para os módulos: Estoque, Compras, Faturamento, Financeiro, Relatórios
- Páginas de módulos para exibição de dashboards interativos com gráficos dinâmicos (sem persistência de dados nessas páginas)

## Novidades: Dashboard de Estoque Padronizado

O módulo de **Estoque** foi totalmente padronizado seguindo o modelo do dashboard de Faturamento, trazendo:

- **Filtros dinâmicos**: filial, categoria, status, produto (com seleção automática dos valores disponíveis)
- **Gráficos interativos** (Chart.js + DataLabels):
  - Pizza: Estoque por Status, Valor Total por Filial, Valor Total por Categoria
  - Barras verticais/horizontais: Produtos em Estoque, Giro de Estoque, Filiais, Categorias, Produtos Abaixo do Mínimo
  - Todos os gráficos de barras suportam rolagem para muitos itens (sem limite de top 10)
- **Cartões de indicadores**:
  - Total em Estoque, Valor Total (abreviado: K, M, B), Produtos Abaixo do Mínimo, Produtos Únicos, Filiais Ativas, Categorias
  - Visual moderno, valores centralizados e abreviados, moeda alinhada
- **Atualização dinâmica via AJAX**: ao mudar qualquer filtro, todos os gráficos e cartões são atualizados automaticamente sem recarregar a página
- **Exibição de percentuais nas fatias das pizzas** (valor completo apenas no tooltip)

## Estrutura do Banco de Dados

O sistema utiliza apenas uma tabela principal:
- **user**: informações dos usuários, incluindo permissões de acesso aos módulos

## Como rodar o projeto

1. Instale as dependências:
   ```bash
   pip install flask flask_sqlalchemy pandas
   ```
2. Crie o banco de dados e as tabelas:
   ```bash
   python create_db.py
   ```
3. (Opcional) Popule o banco com um usuário admin:
   ```bash
   python seed_db.py
   ```
4. Rode o servidor Flask:
   ```bash
   python app.py
   ```
5. Acesse em [http://localhost:5000](http://localhost:5000)

## Estrutura de Pastas

- `app.py` — inicialização do Flask
- `models.py` — definição do model User
- `routes/` — rotas do sistema (admin, empresa, auth)
- `templates/` — templates HTML (admin, empresa, auth)
- `static/` — arquivos estáticos (CSS)
- `relatorios/` — bases de dados CSV para dashboards (`base_livros.csv`, `base_estoque.csv`)
- `utils/` — utilitários de autenticação, logs e extração de dados para dashboards
- `data/database.db` — banco de dados SQLite

## Dashboards e Filtros

### Faturamento
- Filtros: Ano, Filial, Categoria, Estado, Produto, Status
- Gráficos: Faturamento por ano, mês, categoria, produto, filial, estado, ticket médio, devoluções

### Estoque
- Filtros: Filial, Categoria, Status, Produto
- Cartões: Total em Estoque, Valor Total, Produtos Abaixo do Mínimo, Produtos Únicos, Filiais Ativas, Categorias
- Gráficos:
  - Pizza: Estoque por Status, Valor Total por Filial, Valor Total por Categoria
  - Barras: Produtos em Estoque, Giro de Estoque, Filiais, Categorias, Produtos Abaixo do Mínimo
- Todos os gráficos são atualizados dinamicamente via AJAX conforme os filtros

## Observações
- As páginas de módulos servem apenas para exibição de dashboards, sem salvar dados.
- Para visualizar ou editar o banco, use o [DB Browser for SQLite](https://sqlitebrowser.org/) ou uma extensão do VS Code.
- Os dashboards utilizam Chart.js e plugin DataLabels para exibição de valores e percentuais.
- Valores grandes são automaticamente abreviados (ex: 1.2M, 850K).

## Segurança
- Autenticação obrigatória para acesso aos módulos
- Permissões de acesso por usuário para cada módulo
- Proteção contra CSRF e XSS nas rotas e templates
- Dados sensíveis e segredos devem ser configurados via variáveis de ambiente
- Recomenda-se uso de HTTPS, headers de segurança e rate limiting em produção

---

Se tiver dúvidas ou quiser contribuir, fique à vontade para abrir uma issue ou PR! 

---

### **models.py**
- O model `User` está **correto** e inclui o campo:
  ```python
  pode_relatorios = db.Column(db.Boolean, default=False)
  ```

---

### **create_db.py**
- O script está assim:
  ```python
  from app import app, db
  import models  # Garante que os models sejam registrados

  with app.app_context():
      db.create_all()
      print("Tabelas criadas com sucesso!") 
  ```

---

## **O que fazer depois:**
1. Salve o arquivo `create_db.py` com a alteração acima.
2. Apague o banco de dados:
   ```bash
   rm -f data/database.db
   ```
3. Rode novamente:
   ```bash
   python flask_system/create_db.py
   python flask_system/seed_db.py
   ```

Assim, a tabela será criada do zero, já com a coluna `pode_relatorios`, e o seed funcionará normalmente.

Se quiser, posso aplicar essa alteração automaticamente para você! 
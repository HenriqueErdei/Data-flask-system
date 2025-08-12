from app import app, db
from models import User

with app.app_context():
    # Cria o usuário admin com todas as permissões
    user = User(
        id='1',
        username='admin',
        password='123',
        is_admin=True,
        email='admin@admin.com',
        pode_estoque=True,
        pode_compras=True,
        pode_faturamento=True,
        pode_financeiro=True,
        pode_relatorios=True  # <-- nova permissão incluída
    )
    db.session.add(user)
    db.session.commit()
    print('Usuário admin criado com sucesso!') 
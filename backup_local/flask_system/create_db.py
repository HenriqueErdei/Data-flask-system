from app import app, db
import models  # Garante que os models sejam registrados

with app.app_context():
    db.drop_all()
    db.create_all()
    print("Tabelas criadas com sucesso!") 
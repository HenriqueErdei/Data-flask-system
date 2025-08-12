from flask import Flask
import os
from config import SECRET_KEY
from flask_sqlalchemy import SQLAlchemy
import config
from models import db, Settings
from dotenv import load_dotenv
load_dotenv()

# Importar blueprints
from routes.auth_routes import bp_auth
from routes.admin_routes import bp_admin
from routes.empresa_routes import bp_empresa
from routes.ia_routes import bp_ia

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = SECRET_KEY

# Criação dos diretórios de dados caso não existam
os.makedirs(app.config['DATA_PATH'], exist_ok=True)
os.makedirs(app.config['LOG_PATH'], exist_ok=True)

# Registrar blueprints
app.register_blueprint(bp_auth)
app.register_blueprint(bp_admin)
app.register_blueprint(bp_empresa)
app.register_blueprint(bp_ia)

db.init_app(app)

@app.context_processor
def inject_settings():
    settings = Settings.query.first()
    return dict(settings=settings)

def abrevia_numero(valor):
    try:
        valor = float(valor)
        if valor >= 1e9:
            return f"{valor/1e9:.1f}B"
        elif valor >= 1e6:
            return f"{valor/1e6:.1f}M"
        elif valor >= 1e3:
            return f"{valor/1e3:.1f}K"
        else:
            return f"{valor:.0f}"
    except Exception:
        return valor

app.jinja_env.filters['abrevia_numero'] = abrevia_numero

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import os

# Instâncias globais
bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurações adicionais para uploads
    app.config.update({
        'UPLOAD_FOLDER': os.path.join(app.root_path, 'uploads'),
        'MAX_CONTENT_LENGTH': 10 * 1024 * 1024,  # 10MB
        'ALLOWED_EXTENSIONS': {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'},
        'SECURE_FILENAME': True  # Usar secure_filename para nomes de arquivo
    })

    # Inicialização de extensões
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .models import Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registro de blueprints
    from .auth import auth_bp
    from .routes import main_bp, admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Criação de diretório de uploads e tabelas do banco
    with app.app_context():
        # Garante que o diretório de uploads existe
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
                app.logger.info(f'Diretório de uploads criado: {upload_folder}')
            except OSError as e:
                app.logger.error(f'Erro ao criar diretório de uploads: {e}')
        
        # Cria todas as tabelas do banco de dados
        db.create_all()
        app.logger.info('Tabelas do banco de dados verificadas')

    return app
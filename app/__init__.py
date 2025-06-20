from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from datetime import datetime
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
        'SECURE_FILENAME': True
    })

    # Inicialização de extensões
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .models import Usuario, MensagemPublica, Precatorio

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registro de blueprints
    from .auth import auth_bp
    from .routes import main_bp
    from .admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    # Context processor para notificações
    @app.context_processor
    def inject_notificacoes():
        try:
            msg_count = MensagemPublica.query.filter_by(lida=False).count()
            form_count = Precatorio.query.filter_by(tipo_entrada='compra', usuario_id=None).count()
            cad_user_count = Usuario.query.filter_by(ativo=True).filter(Usuario.data_cadastro >= datetime.utcnow().date()).count()
            cad_precatorio_count = Precatorio.query.filter(Precatorio.data_cadastro >= datetime.utcnow().date()).count()
        except Exception:
            msg_count = form_count = cad_user_count = cad_precatorio_count = 0

        return dict(
            msgs_nao_lidas=msg_count,
            forms_nao_respondidos=form_count,
            novos_usuarios=cad_user_count,
            novos_precatorios=cad_precatorio_count
        )

    # Criação de diretório de uploads e tabelas do banco
    with app.app_context():
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder)
                app.logger.info(f'Diretório de uploads criado: {upload_folder}')
            except OSError as e:
                app.logger.error(f'Erro ao criar diretório de uploads: {e}')

        db.create_all()
        app.logger.info('Tabelas do banco de dados verificadas')

    return app

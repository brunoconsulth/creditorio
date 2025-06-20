from . import db
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tipo = db.Column(db.String(20), default='usuario')
    ativo = db.Column(db.Boolean, default=True)
    saldo = db.Column(db.Float, default=0.0)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    precatorios_comprados = db.relationship(
        'Precatorio',
        foreign_keys='Precatorio.comprador_id',
        backref='comprador_user',
        lazy=True
    )

    def get_id(self):
        return str(self.id)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha).decode('utf-8')

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def gerar_token_redefinicao(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'usuario_id': self.id})

    def is_active(self):
        return self.ativo

    @staticmethod
    def verificar_token_redefinicao(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_sec)
        except Exception:
            return None
        return Usuario.query.get(data['usuario_id'])

class Precatorio(db.Model):
    __tablename__ = 'precatorio'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50))  # Número do precatório (opcional)
    tipo = db.Column(db.String(50), nullable=False)
    tipo_entrada = db.Column(db.String(20), nullable=False)  # 'compra' ou 'venda'
    nome = db.Column(db.String(100), nullable=False)
    cpf_cnpj = db.Column(db.String(20), nullable=False)  
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(2))
    municipio = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pendente')  # ex: Pendente, Em análise, Fechado
    vendido = db.Column(db.Boolean, default=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    comprador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='precatorios_criados')


class MensagemPublica(db.Model):
    __tablename__ = 'mensagem_publica'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefone = db.Column(db.String(20))
    assunto = db.Column(db.String(150), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)


class Mensagem(db.Model):
    __tablename__ = 'mensagem'

    id = db.Column(db.Integer, primary_key=True)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow)
    lida = db.Column(db.Boolean, default=False)

    remetente = db.relationship('Usuario', foreign_keys=[remetente_id], backref='mensagens_enviadas')
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id], backref='mensagens_recebidas')


class LogAcao(db.Model):
    __tablename__ = 'log_acao'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    acao = db.Column(db.String(255), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='logs')


class Proposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    precatorio_id = db.Column(db.Integer, db.ForeignKey('precatorio.id'), nullable=False)
    remetente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    destinatario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    mensagem = db.Column(db.Text)
    status = db.Column(db.String(20))  # 'pendente', 'aceita', 'recusada'
    data = db.Column(db.DateTime, default=datetime.utcnow)

    remetente = db.relationship('Usuario', foreign_keys=[remetente_id])
    destinatario = db.relationship('Usuario', foreign_keys=[destinatario_id])

class Documento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    precatorio_id = db.Column(db.Integer, db.ForeignKey('precatorio.id'), nullable=False)

    usuario = db.relationship('Usuario', backref='documentos')
    precatorio = db.relationship('Precatorio', backref='documentos')

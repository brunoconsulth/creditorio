# app/auth.py
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from . import db, bcrypt
from .models import Usuario
from flask_login import login_user, logout_user, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf_cnpj = request.form['cpf_cnpj']
        telefone = request.form['telefone']
        senha = request.form['senha']

        if Usuario.query.filter((Usuario.email == email) | (Usuario.cpf_cnpj == cpf_cnpj)).first():
            flash('E-mail ou CPF/CNPJ já cadastrado.', 'danger')
            return redirect(url_for('auth.cadastro'))

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone
        )
        novo_usuario.set_senha(senha)

        db.session.add(novo_usuario)
        db.session.commit()
        flash('Cadastro realizado com sucesso. Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        cpf_cnpj = request.form['cpf_cnpj']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(cpf_cnpj=cpf_cnpj).first()

        if usuario and usuario.verificar_senha(senha):
            if not usuario.ativo:
                flash('Conta inativa. Contate o suporte.', 'warning')
                return redirect(url_for('auth.login'))

            login_user(usuario)
       
            return redirect(url_for('main.dashboard'))
        else:
            flash('CPF/CNPJ ou senha inválidos.', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

# Solicitação de redefinição
@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            # gerar e enviar token por email
            token = usuario.gerar_token_redefinicao()  # você vai implementar
            link = url_for('auth.redefinir_senha', token=token, _external=True)
            # enviar email com o link (implementaremos)
            enviar_email_recuperacao(usuario.email, link)
            flash('Instruções enviadas para seu e-mail.', 'info')
        else:
            flash('E-mail não encontrado.', 'danger')
    return render_template('recuperar_senha.html')

# Redefinição de senha
@auth_bp.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    usuario = Usuario.verificar_token_redefinicao(token)  # você vai implementar
    if not usuario:
        flash('Link inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        nova_senha = request.form.get('senha')
        usuario.set_senha(nova_senha)

        return redirect(url_for('auth.login'))

    return render_template('redefinir_senha.html')

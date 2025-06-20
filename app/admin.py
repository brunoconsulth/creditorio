from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Usuario, Precatorio, MensagemPublica, LogAcao
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def verificar_admin():
    if not current_user.is_authenticated or current_user.tipo != 'administrador':
        flash('Acesso restrito a administradores.', 'danger')
        return redirect(url_for('auth.login'))

@admin_bp.route('/')
@login_required
def painel_admin():
    usuarios = Usuario.query.all()
    precatorios = Precatorio.query.order_by(Precatorio.data_cadastro.desc()).all()
    mensagens = MensagemPublica.query.order_by(MensagemPublica.data_envio.desc()).all()
    logs = LogAcao.query.order_by(LogAcao.data.desc()).limit(50).all()
    return render_template('admin.html', usuarios=usuarios, precatorios=precatorios, mensagens=mensagens, logs=logs)

@admin_bp.route('/usuarios')
@login_required
def listar_usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/gerenciar_usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/atualizar', methods=['POST'])
@login_required
def atualizar_usuarios():
    for usuario in Usuario.query.all():
        uid = str(usuario.id)
        usuario.nome = request.form.get(f'nome_{uid}', usuario.nome)
        usuario.email = request.form.get(f'email_{uid}', usuario.email)
        usuario.cpf_cnpj = request.form.get(f'cpf_cnpj_{uid}', usuario.cpf_cnpj)
        usuario.telefone = request.form.get(f'telefone_{uid}', usuario.telefone)
        usuario.ativo = request.form.get(f'status_{uid}') == '1'
        usuario.tipo = request.form.get(f'tipo_{uid}', usuario.tipo)
    db.session.commit()
    flash('Dados dos usuários atualizados com sucesso.', 'success')
    return redirect(url_for('admin.listar_usuarios'))

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nome = request.form['nome']
        usuario.email = request.form['email']
        usuario.cpf_cnpj = request.form['cpf_cnpj']
        usuario.telefone = request.form['telefone']
        db.session.commit()
        flash('Usuário atualizado com sucesso.', 'success')
        return redirect(url_for('admin.listar_usuarios'))
    return render_template('admin/editar_usuario.html', usuario=usuario)

@admin_bp.route('/alterar_status_precatorio/<int:id>', methods=['POST'])
@login_required
def alterar_status_precatorio(id):
    precatorio = Precatorio.query.get_or_404(id)
    novo_status = request.form.get('status')
    if novo_status:
        precatorio.status = novo_status
        db.session.commit()
        flash('Status do precatório atualizado com sucesso.', 'success')
    return redirect(request.referrer or url_for('admin.painel_admin'))



@admin_bp.route('/mensagens')
@login_required
def listar_mensagens():
    mensagens = MensagemPublica.query.order_by(MensagemPublica.data_envio.desc()).all()
    return render_template('admin/listar_mensagens.html', mensagens=mensagens)

@admin_bp.route('/mensagens/<int:id>')
@login_required
def visualizar_mensagem(id):
    mensagem = MensagemPublica.query.get_or_404(id)
    return render_template('admin/visualizar_mensagem.html', mensagem=mensagem)


@admin_bp.route('/solicitacoes')
@login_required
def listar_solicitacoes():
    solicitacoes = Precatorio.query.filter_by(tipo_entrada='compra') \
        .order_by(Precatorio.data_cadastro.desc()).all()
    return render_template('admin/solicitacoes.html', solicitacoes=solicitacoes)

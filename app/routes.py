from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Precatorio, Usuario, Mensagem, MensagemPublica, LogAcao, Proposta
from datetime import datetime
import smtplib
from email.message import EmailMessage

main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@main_bp.route('/')
def home():
    precatorios = Precatorio.query.filter_by(vendido=False, tipo_entrada='venda')\
                                  .order_by(Precatorio.data_cadastro.desc()).limit(10).all()
    return render_template('index.html', precatorios=precatorios)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    precatorios = Precatorio.query.filter_by(usuario_id=current_user.id).order_by(Precatorio.data_cadastro.desc()).all()
    return render_template('dashboard.html', usuario=current_user, precatorios=precatorios)

@main_bp.route('/vender', methods=['GET', 'POST'])
def vender_precatorio():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        nome = current_user.nome if current_user.is_authenticated else request.form.get('nome')
        telefone = current_user.telefone if current_user.is_authenticated else request.form.get('telefone')
        email = current_user.email if current_user.is_authenticated else request.form.get('email')
        valor = request.form.get('valor')
        estado = request.form.get('estado') if tipo in ['Estadual', 'Municipal'] else None
        municipio = request.form.get('municipio') if tipo == 'Municipal' else None

        if not all([tipo, nome, telefone, email, valor]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('main.vender_precatorio'))

        novo = Precatorio(
            tipo=tipo,
            tipo_entrada='venda',
            nome=nome,
            telefone=telefone,
            email=email,
            valor=valor,
            estado=estado,
            municipio=municipio,
            usuario_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(novo)
        db.session.commit()
        flash('Cadastrado com sucesso!', 'success')
        return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('main.home'))

    return render_template('vender.html')

@main_bp.route('/comprar', methods=['GET', 'POST'])
def comprar_precatorio():
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        nome = current_user.nome if current_user.is_authenticated else request.form.get('nome')
        telefone = current_user.telefone if current_user.is_authenticated else request.form.get('telefone')
        email = current_user.email if current_user.is_authenticated else request.form.get('email')
        valor = request.form.get('valor')
        estado = request.form.get('estado') if tipo in ['Estadual', 'Municipal'] else None
        municipio = request.form.get('municipio') if tipo == 'Municipal' else None

        if not all([tipo, nome, telefone, email, valor]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('main.comprar_precatorio'))

        novo = Precatorio(
            tipo=tipo,
            tipo_entrada='compra',
            nome=nome,
            telefone=telefone,
            email=email,
            valor=valor,
            estado=estado,
            municipio=municipio,
            usuario_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(novo)
        db.session.commit()
        flash('Cadastrado com sucesso!', 'success')
        return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('main.home'))

    return render_template('comprar.html')

@main_bp.route('/mensagem', methods=['GET', 'POST'])
def mensagem_admin():
    if request.method == 'POST':
        nome = current_user.nome if current_user.is_authenticated else request.form['nome']
        email = current_user.email if current_user.is_authenticated else request.form['email']
        telefone = current_user.telefone if current_user.is_authenticated else request.form['telefone']
        assunto = request.form['assunto']
        mensagem = request.form['mensagem']

        nova = MensagemPublica(
            nome=nome,
            email=email,
            telefone=telefone,
            assunto=assunto,
            mensagem=mensagem
        )
        db.session.add(nova)
        db.session.commit()

        try:
            msg = EmailMessage()
            msg['Subject'] = f'Nova mensagem: {assunto}'
            msg['From'] = email
            msg['To'] = 'admin@seudominio.com'
            msg.set_content(f'''
            Nome: {nome}
            Email: {email}
            Telefone: {telefone}
            Assunto: {assunto}
            Mensagem:
            {mensagem}
            ''')

            with smtplib.SMTP('smtp.seuprovedor.com', 587) as smtp:
                smtp.starttls()
                smtp.login('seu_email@seudominio.com', 'sua_senha')
                smtp.send_message(msg)
        except Exception as e:
            print(f"Erro ao enviar email: {e}")

        flash("Mensagem enviada com sucesso!", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('mensagem.html')

@main_bp.route('/admin')
@login_required
def painel_admin():
    if current_user.tipo != 'administrador':
        flash("Acesso negado", "error")
        return redirect(url_for('main.dashboard'))

    usuarios = Usuario.query.all()
    precatorios = Precatorio.query.order_by(Precatorio.data_cadastro.desc()).all()
    mensagens = MensagemPublica.query.order_by(MensagemPublica.data_envio.desc()).all()
    logs = LogAcao.query.order_by(LogAcao.data.desc()).limit(50).all()

    return render_template('admin.html', usuarios=usuarios, precatorios=precatorios, mensagens=mensagens, logs=logs)

@admin_bp.route('/alterar_tipo_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def alterar_tipo_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.tipo = 'usuario' if usuario.tipo == 'administrador' else 'administrador'
    db.session.commit()
    flash('Tipo de usuário alterado com sucesso.')
    return redirect(url_for('main.painel_admin'))

@admin_bp.route('/alterar_status_usuario/<int:usuario_id>', methods=['POST'])
@login_required
def alterar_status_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.ativo = not usuario.ativo
    db.session.commit()
    flash('Status do usuário alterado com sucesso.')
    return redirect(url_for('main.painel_admin'))

@admin_bp.route('/alterar_status_precatorio/<int:id>', methods=['POST'])
@login_required
def alterar_status_precatorio(id):
    if current_user.tipo != 'administrador':
        flash("Acesso negado", "danger")
        return redirect(url_for('main.dashboard'))

    precatorio = Precatorio.query.get_or_404(id)
    precatorio.status = 'Finalizado' if precatorio.status != 'Finalizado' else 'Pendente'
    db.session.commit()
    flash("Status do precatório atualizado com sucesso.", "success")
    return redirect(url_for('main.painel_admin'))

@main_bp.route('/precatorio/<int:id>')
@login_required
def detalhar_precatorio(id):
    precatorio = Precatorio.query.get_or_404(id)
    return render_template('detalhar_precatorio.html', precatorio=precatorio)



@admin_bp.route('/mensagem/<int:id>')
@login_required
def visualizar_mensagem(id):
    mensagem = MensagemPublica.query.get_or_404(id)
    return render_template('visualizar_mensagem.html', mensagem=mensagem)



import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/upload_documento/<int:id>', methods=['POST'])
@login_required
def upload_documento(id):
    precatorio = Precatorio.query.get_or_404(id)

    if 'documentos' not in request.files:
        flash("Nenhum arquivo enviado.", "warning")
        return redirect(url_for('main.detalhar_precatorio', id=id))

    arquivos = request.files.getlist('documentos')

    for arquivo in arquivos:
        if arquivo and allowed_file(arquivo.filename):
            if len(arquivo.read()) > 10 * 1024 * 1024:
                flash("Arquivo excede o limite de 10MB.", "danger")
                return redirect(url_for('main.detalhar_precatorio', id=id))
            arquivo.seek(0)

            nome_seguro = secure_filename(arquivo.filename)
            caminho = os.path.join(UPLOAD_FOLDER, nome_seguro)
            arquivo.save(caminho)

            doc = Documento(nome_arquivo=nome_seguro, caminho=caminho, usuario_id=current_user.id, precatorio_id=precatorio.id)
            db.session.add(doc)
    db.session.commit()
    flash("Documento(s) enviado(s) com sucesso.", "success")
    return redirect(url_for('main.detalhar_precatorio', id=id))

@main_bp.route('/download_documento/<int:id>')
@login_required
def download_documento(id):
    doc = Documento.query.get_or_404(id)
    return send_from_directory(directory=os.path.dirname(doc.caminho), path=os.path.basename(doc.caminho), as_attachment=True)


@main_bp.route('/formulario-contato', methods=['POST'])
def receber_formulario():
    from .models import Precatorio
    from . import db

    tipo = request.form.get('precatory-type')
    tipo_entrada = request.form.get('acao')
    nome = request.form.get('name')
    cpf_cnpj = request.form.get('cpf_cnpj')
    telefone = request.form.get('phone')
    email = request.form.get('email')
    valor = request.form.get('value').replace("R$", "").replace(".", "").replace(",", ".")
    estado = request.form.get('estado') or None
    municipio = request.form.get('municipio') or None

    if not all([tipo, tipo_entrada, nome, cpf_cnpj, telefone, email, valor]):
        flash("Por favor, preencha todos os campos obrigatórios.", "danger")
        return redirect(url_for('main.home'))

    novo = Precatorio(
        tipo=tipo.capitalize(),
        tipo_entrada=tipo_entrada.lower(),
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email=email,
        valor=float(valor),
        estado=estado,
        municipio=municipio,
        status='Pendente',
        vendido=False
    )

    db.session.add(novo)
    db.session.commit()

    flash("Formulário enviado com sucesso! Em breve entraremos em contato.", "success")
    return redirect(url_for('main.home'))

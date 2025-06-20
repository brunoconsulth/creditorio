from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from . import db
from .models import Precatorio, Usuario, Mensagem, MensagemPublica, Proposta, Documento
from datetime import datetime
import smtplib
from email.message import EmailMessage
import os
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy.exc import SQLAlchemyError

main_bp = Blueprint('main', __name__)

# Função auxiliar para verificar extensões permitidas
def allowed_file(filename):
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
        cpf_cnpj = current_user.cpf_cnpj if current_user.is_authenticated else request.form.get('cpf_cnpj')
        numero = request.form.get('numero', None)
        valor_str = request.form.get('valor', '').replace('R$', '').replace('.', '').replace(',', '.').strip()

        try:
            valor = float(valor_str)
        except ValueError:
            flash("Valor inválido.", "danger")
            return redirect(url_for('main.vender_precatorio'))

        estado = request.form.get('estado') if tipo in ['Estadual', 'Municipal'] else None
        municipio = request.form.get('municipio') if tipo == 'Municipal' else None

        if not all([tipo, nome, telefone, email, valor_str, cpf_cnpj]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('main.vender_precatorio'))

        novo = Precatorio(
            tipo=tipo,
            tipo_entrada='venda',
            nome=nome,
            cpf_cnpj=cpf_cnpj,
            telefone=telefone,
            email=email,
            valor=valor,
            estado=estado,
            municipio=municipio,
            numero=numero,
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
        cpf_cnpj = current_user.cpf_cnpj if current_user.is_authenticated else request.form.get('cpf_cnpj')
        valor = request.form.get('valor')
        estado = request.form.get('estado') if tipo in ['Estadual', 'Municipal'] else None
        municipio = request.form.get('municipio') if tipo == 'Municipal' else None

        if not all([tipo, nome, telefone, email, cpf_cnpj, valor]):
            flash('Preencha todos os campos obrigatórios.', 'danger')
            return redirect(url_for('main.comprar_precatorio'))

        try:
            valor_formatado = float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())
        except ValueError:
            flash('Valor inválido.', 'danger')
            return redirect(url_for('main.comprar_precatorio'))

        novo = Precatorio(
            tipo=tipo,
            tipo_entrada='compra',
            nome=nome,
            telefone=telefone,
            email=email,
            cpf_cnpj=cpf_cnpj,
            valor=valor_formatado,
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

        nova = MensagemPublica(nome=nome, email=email, telefone=telefone, assunto=assunto, mensagem=mensagem)
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

@main_bp.route('/precatorio/<int:id>')
@login_required
def detalhar_precatorio(id):
    precatorio = Precatorio.query.get_or_404(id)
    documentos = Documento.query.filter_by(precatorio_id=id).all()
    return render_template('detalhar_precatorio.html', precatorio=precatorio, documentos=documentos)

@main_bp.route('/upload_documento/<int:id>', methods=['POST'])
@login_required
def upload_documento(id):
    try:
        UPLOAD_FOLDER = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        precatorio = Precatorio.query.get_or_404(id)
        if not (current_user.id == precatorio.usuario_id or current_user.tipo == 'administrador'):
            flash("Acesso não autorizado.", "danger")
            return redirect(url_for('main.dashboard'))

        if 'documentos' not in request.files:
            flash("Nenhum arquivo selecionado.", "warning")
            return redirect(url_for('main.detalhar_precatorio', id=id))

        arquivos = request.files.getlist('documentos')
        uploads_sucesso = 0

        for arquivo in arquivos:
            if arquivo.filename == '':
                continue

            if arquivo and allowed_file(arquivo.filename):
                try:
                    arquivo.seek(0, os.SEEK_END)
                    file_size = arquivo.tell()
                    arquivo.seek(0)
                    if file_size > current_app.config['MAX_CONTENT_LENGTH']:
                        flash(f"Arquivo {arquivo.filename} excede o tamanho máximo permitido (10MB)", "warning")
                        continue

                    file_ext = os.path.splitext(arquivo.filename)[1].lower()
                    unique_id = uuid.uuid4().hex[:8]
                    safe_filename = f"{unique_id}{file_ext}"
                    save_path = os.path.join(UPLOAD_FOLDER, safe_filename)

                    arquivo.save(save_path)

                    novo_doc = Documento(
                        nome_arquivo=secure_filename(arquivo.filename),
                        caminho=save_path,
                        usuario_id=current_user.id,
                        precatorio_id=precatorio.id,
                        data_upload=datetime.utcnow()
                    )
                    db.session.add(novo_doc)
                    uploads_sucesso += 1
                except Exception as file_error:
                    current_app.logger.error(f"Erro ao processar arquivo: {str(file_error)}")
                    continue

        if uploads_sucesso > 0:
            db.session.commit()
            flash(f"{uploads_sucesso} documento(s) enviado(s) com sucesso!", "success")
        else:
            flash("Nenhum arquivo válido foi processado.", "warning")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro no upload: {str(e)}", exc_info=True)
        flash("Ocorreu um erro ao processar seu upload. Tente novamente.", "danger")

    return redirect(url_for('main.detalhar_precatorio', id=id))

@main_bp.route('/download_documento/<int:id>')
@login_required
def download_documento(id):
    doc = Documento.query.get_or_404(id)
    if not (current_user.id == doc.usuario_id or current_user.tipo == 'administrador'):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for('main.dashboard'))

    try:
        return send_from_directory(
            directory=os.path.dirname(doc.caminho),
            path=os.path.basename(doc.caminho),
            as_attachment=True
        )
    except FileNotFoundError:
        flash("Arquivo não encontrado no servidor.", "danger")
        return redirect(url_for('main.detalhar_precatorio', id=doc.precatorio_id))

@main_bp.route('/formulario-contato', methods=['POST'])
def receber_formulario():
    data = request.get_json() if request.is_json else request.form
    tipo = data.get('precatory-type')
    tipo_entrada = data.get('acao')
    nome = data.get('name')
    cpf_cnpj = data.get('cpf_cnpj')
    telefone = data.get('phone')
    email = data.get('email')
    valor_raw = data.get('value')
    estado = data.get('estado') or None
    municipio = data.get('municipio') or None

    if not all([tipo, tipo_entrada, nome, cpf_cnpj, telefone, email, valor_raw]):
        return ({"message": "Por favor, preencha todos os campos obrigatórios."}, 400) if request.is_json else redirect(url_for('main.home'))

    try:
        valor = float(str(valor_raw).replace("R$", "").replace(".", "").replace(",", "."))
    except Exception:
        return ({"message": "Valor inválido."}, 400) if request.is_json else redirect(url_for('main.home'))

    novo = Precatorio(
        tipo=tipo.capitalize(),
        tipo_entrada=tipo_entrada.lower(),
        nome=nome,
        cpf_cnpj=cpf_cnpj,
        telefone=telefone,
        email=email,
        valor=valor,
        estado=estado,
        municipio=municipio,
        status='Pendente',
        vendido=False
    )

    try:
        db.session.add(novo)
        db.session.commit()
        return ({"message": "Formulário enviado com sucesso!"}, 200) if request.is_json else redirect(url_for('main.home'))
    except Exception:
        db.session.rollback()
        return ({"message": "Erro ao enviar formulário."}, 500) if request.is_json else redirect(url_for('main.home'))

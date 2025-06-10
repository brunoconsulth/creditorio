# set_admin.py
from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    usuario = Usuario.query.filter_by(email='bruno.padilha@consulth.com.br').first()

    if usuario:
        usuario.tipo = 'administrador'
        db.session.commit()
        print("✅ Usuário atualizado para administrador com sucesso.")
    else:
        print("❌ Usuário não encontrado. Verifique o e-mail.")

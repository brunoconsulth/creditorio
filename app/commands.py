# app/commands.py
from flask.cli import with_appcontext
import click
from .models import db, Usuario

@click.command('tornar-admin')
@click.argument('email')
@with_appcontext
def tornar_admin(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        click.echo(f"Usuário com e-mail {email} não encontrado.")
        return

    usuario.tipo = 'administrador'
    db.session.commit()
    click.echo(f"Usuário {email} agora é administrador.")

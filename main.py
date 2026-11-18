import os
import secrets
from functools import wraps

import mysql.connector
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from mysql.connector.errorcode import ER_DUP_ENTRY, ER_ROW_IS_REFERENCED_2
from werkzeug.security import check_password_hash

from db import consultar, executar, fechar_db

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("DOCE_PAUSA_SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_SAMESITE="Lax",
)
app.teardown_appcontext(fechar_db)


def login_obrigatorio(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para continuar.", "erro")
            return redirect(url_for("login"))
        return funcao(*args, **kwargs)

    return verificar


def somente_admin(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if session.get("perfil") != "admin":
            abort(403)
        return funcao(*args, **kwargs)

    return verificar


@app.template_global()
def token_formulario():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def proteger_formulario(funcao):
    @wraps(funcao)
    def verificar(*args, **kwargs):
        if request.method == "POST":
            esperado = session.get("csrf_token", "")
            recebido = request.form.get("csrf_token", "")
            if not esperado or not secrets.compare_digest(esperado.encode(), recebido.encode()):
                abort(400)
        return funcao(*args, **kwargs)

    return verificar


@app.template_filter()
def reais(valor):
    numero = f"{valor:,.2f}".translate(str.maketrans(",.", ".,"))
    return f"R$ {numero}"


@app.route("/login", methods=["GET", "POST"])
@proteger_formulario
def login():
    if "usuario_id" in session:
        return redirect(url_for("inicio"))

    login_digitado = ""
    if request.method == "POST":
        login_digitado = request.form.get("login", "").strip()
        senha = request.form.get("senha", "")
        usuario = None
        if 1 <= len(login_digitado) <= 50 and senha:
            usuario = consultar(
                "SELECT id, nome, senha_hash, perfil FROM usuario WHERE login = %s",
                (login_digitado,),
                um=True,
            )
        if usuario and check_password_hash(usuario["senha_hash"], senha):
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["nome"] = usuario["nome"]
            session["perfil"] = usuario["perfil"]
            flash(f"Bem-vindo, {usuario['nome']}!", "sucesso")
            return redirect(url_for("inicio"), code=303)
        flash("Login ou senha incorretos.", "erro")
    return render_template("login.html", login_digitado=login_digitado)


@app.post("/logout")
@login_obrigatorio
@proteger_formulario
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"), code=303)


@app.get("/")
@login_obrigatorio
def inicio():
    produtos = consultar(
        """SELECT p.nome, c.nome AS categoria, p.preco
           FROM produto AS p
           JOIN categoria AS c ON c.id = p.categoria_id
           ORDER BY c.nome, p.nome, p.id"""
    )
    return render_template("inicio.html", produtos=produtos)


@app.get("/categorias")
@login_obrigatorio
def categorias():
    registros = consultar("SELECT id, nome FROM categoria ORDER BY nome, id")
    return render_template("categorias.html", categorias=registros)


def buscar_categoria(categoria_id):
    categoria = consultar(
        "SELECT id, nome FROM categoria WHERE id = %s", (categoria_id,), um=True
    )
    if categoria is None:
        abort(404)
    return categoria


@app.route("/categorias/nova", methods=["GET", "POST"])
@app.route("/categorias/<int(min=1, max=2147483647):categoria_id>/editar", methods=["GET", "POST"])
@login_obrigatorio
@somente_admin
@proteger_formulario
def formulario_categoria(categoria_id=None):
    editando = categoria_id is not None
    titulo = "Editar categoria" if editando else "Nova categoria"
    if request.method == "GET":
        nome = buscar_categoria(categoria_id)["nome"] if editando else ""
        return render_template("categoria_form.html", titulo=titulo, nome=nome)

    nome = request.form.get("nome", "").strip()
    if not 1 <= len(nome) <= 60:
        flash("Informe um nome de 1 a 60 caracteres.", "erro")
        return render_template("categoria_form.html", titulo=titulo, nome=nome), 422

    try:
        if editando:
            alteradas = executar("UPDATE categoria SET nome = %s WHERE id = %s", (nome, categoria_id))
            if not alteradas:
                abort(404)
        else:
            executar("INSERT INTO categoria (nome) VALUES (%s)", (nome,))
    except mysql.connector.IntegrityError as erro:
        if erro.errno != ER_DUP_ENTRY:
            raise
        flash("Já existe uma categoria com esse nome.", "erro")
        return render_template("categoria_form.html", titulo=titulo, nome=nome), 409

    flash("Categoria atualizada." if editando else "Categoria cadastrada.", "sucesso")
    return redirect(url_for("categorias"), code=303)


@app.route("/categorias/<int(min=1, max=2147483647):categoria_id>/excluir", methods=["GET", "POST"])
@login_obrigatorio
@somente_admin
@proteger_formulario
def excluir_categoria(categoria_id):
    if request.method == "GET":
        categoria = buscar_categoria(categoria_id)
        return render_template("categoria_excluir.html", categoria=categoria)

    if request.form.get("confirmar") != "sim":
        flash("Confirme a exclusão da categoria.", "erro")
        return redirect(url_for("excluir_categoria", categoria_id=categoria_id), code=303)

    try:
        if not executar("DELETE FROM categoria WHERE id = %s", (categoria_id,)):
            abort(404)
    except mysql.connector.IntegrityError as erro:
        if erro.errno != ER_ROW_IS_REFERENCED_2:
            raise
        flash("A categoria tem produtos vinculados e não pode ser excluída.", "erro")
    else:
        flash("Categoria excluída.", "sucesso")
    return redirect(url_for("categorias"), code=303)


@app.errorhandler(400)
def requisicao_invalida(_erro):
    return render_template(
        "erro.html",
        titulo="Formulário inválido",
        mensagem="Abra o formulário novamente e reenvie os dados.",
    ), 400


@app.errorhandler(403)
def proibido(_erro):
    return render_template(
        "erro.html",
        titulo="Acesso negado",
        mensagem="Apenas administradores podem gerenciar categorias.",
    ), 403


@app.errorhandler(404)
def nao_encontrado(_erro):
    return render_template(
        "erro.html",
        titulo="Página não encontrada",
        mensagem="O endereço ou registro solicitado não foi encontrado.",
    ), 404


@app.errorhandler(mysql.connector.Error)
def erro_de_banco(erro):
    app.logger.error("Falha ao acessar o MySQL.", exc_info=erro)
    return render_template(
        "erro.html",
        titulo="Falha no banco de dados",
        mensagem="O painel não conseguiu acessar o banco. Tente novamente em instantes.",
    ), 500


if __name__ == "__main__":
    app.run()

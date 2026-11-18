from getpass import getpass

import mysql.connector
from mysql.connector.errorcode import ER_DUP_ENTRY
from werkzeug.security import generate_password_hash

from db import conectar


def main():
    nome = input("Nome completo: ").strip()
    login = input("Login: ").strip()
    senha = getpass("Senha (não aparece ao digitar): ")
    perfil = input("Perfil (admin/comum) [comum]: ").strip().lower() or "comum"
    if not (1 <= len(nome) <= 100 and 1 <= len(login) <= 50 and len(senha) >= 4):
        print("Informe um nome de até 100 caracteres, um login de até 50 e uma senha de pelo menos 4.")
        return 1
    if perfil not in ("admin", "comum"):
        print("Informe o perfil admin ou comum.")
        return 1

    senha_hash = generate_password_hash(senha)
    try:
        with conectar() as conexao, conexao.cursor() as cursor:
            cursor.execute(
                """INSERT INTO usuario (nome, login, senha_hash, perfil)
                   VALUES (%s, %s, %s, %s)""",
                (nome, login, senha_hash, perfil),
            )
            conexao.commit()
    except mysql.connector.Error as erro:
        if erro.errno == ER_DUP_ENTRY:
            print("Já existe um usuário com esse login.")
        else:
            print(f"Não foi possível criar o usuário no MySQL: {erro}")
        return 1

    print(f"Usuário {login} criado com o perfil {perfil}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

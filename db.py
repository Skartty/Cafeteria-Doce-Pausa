import os

import mysql.connector
from flask import g
from mysql.connector.constants import ClientFlag

CONFIG = {
    "host": os.environ.get("DOCE_PAUSA_MYSQL_HOST", "127.0.0.1"),
    "user": os.environ.get("DOCE_PAUSA_MYSQL_USER", "root"),
    "password": os.environ.get("DOCE_PAUSA_MYSQL_PASSWORD", ""),
    "database": "doce_pausa",
    "port": int(os.environ.get("DOCE_PAUSA_MYSQL_PORT", "3306")),
}


def conectar(usar_banco=True):
    config = CONFIG.copy()
    if not usar_banco:
        config.pop("database")
    # Conta a linha encontrada mesmo quando a edição mantém o nome atual.
    return mysql.connector.connect(
        **config, client_flags=[ClientFlag.FOUND_ROWS], connection_timeout=5
    )


def get_db():
    if "db" not in g:
        g.db = conectar()
    return g.db


def fechar_db(_erro=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def consultar(sql, parametros=(), um=False):
    with get_db().cursor(dictionary=True, buffered=True) as cursor:
        cursor.execute(sql, parametros)
        return cursor.fetchone() if um else cursor.fetchall()


def executar(sql, parametros=()):
    db = get_db()
    with db.cursor() as cursor:
        try:
            cursor.execute(sql, parametros)
            db.commit()
        except mysql.connector.Error:
            db.rollback()
            raise
        return cursor.rowcount

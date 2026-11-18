from pathlib import Path

import mysql.connector

from db import conectar

def main():
    try:
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        with conectar(usar_banco=False) as conexao, conexao.cursor() as cursor:
            cursor.execute(schema)
            # Avança pelos resultados para detectar erros em qualquer comando do SQL.
            while cursor.nextset():
                pass
    except OSError as erro:
        print(f"Não foi possível ler schema.sql: {erro}")
        return 1
    except mysql.connector.Error as erro:
        print(f"Não foi possível preparar o banco doce_pausa: {erro}")
        return 1

    print("Banco doce_pausa preparado. Os registros existentes foram preservados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

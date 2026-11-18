# Doce Pausa

Painel interno de uma cafeteria fictícia para consultar produtos, categorias e preços.

- **Administrador (`admin`)** consulta o cardápio e pode cadastrar, listar, editar e excluir categorias. Categorias com produtos vinculados ficam protegidas contra exclusão.
- **Comum (`comum`)** consulta o cardápio e a lista de categorias.

## Executar no Windows

Com Python 3.12 instalado, abra o PowerShell na pasta do projeto e crie o ambiente virtual fora dela.

```powershell
$docePausaVenv = Join-Path $env:LOCALAPPDATA 'DocePausa\venv'
python -m venv $docePausaVenv
$docePausaPython = Join-Path $docePausaVenv 'Scripts\python.exe'
& $docePausaPython -m pip install -r requisitos.txt
```

Inicie o serviço do MySQL Server e use uma conta com permissão para criar o banco `doce_pausa` e operar suas tabelas. A conexão usa `127.0.0.1:3306` por padrão. Se necessário, ajuste `DOCE_PAUSA_MYSQL_HOST` e `DOCE_PAUSA_MYSQL_PORT`. [Instalação do MySQL no Windows](https://dev.mysql.com/doc/refman/8.4/en/windows-installation.html).

```powershell
$env:DOCE_PAUSA_MYSQL_USER = 'root'
$docePausaSenha = Read-Host 'Senha do MySQL' -AsSecureString
$env:DOCE_PAUSA_MYSQL_PASSWORD = [System.Net.NetworkCredential]::new('', $docePausaSenha).Password
& $docePausaPython preparar_banco.py
& $docePausaPython criar_usuario.py
& $docePausaPython main.py
```

O script `preparar_banco.py` pode ser reexecutado e preserva os registros existentes. Em `criar_usuario.py`, escolha `admin` ou `comum` e execute o script novamente para cada conta adicional.

Acesse [http://127.0.0.1:5000](http://127.0.0.1:5000) e entre com o usuário criado. Use **Ctrl+C** no PowerShell para encerrar.

# Doce Pausa

Painel interno de uma cafeteria fictícia. A equipe de atendimento consulta os produtos e os preços em um só lugar. A administração organiza as categorias do cardápio.

**Tecnologias** · Python 3.12, Flask, MySQL 8.4, Jinja e CSS.

## Funcionalidades

| Perfil | Permissões |
| --- | --- |
| Administrador (`admin`) | Consulta o cardápio e cadastra, lista, edita e exclui categorias. |
| Comum (`comum`) | Consulta o cardápio e a lista de categorias. |

O cardápio usa um `JOIN` entre produtos e categorias e exibe os preços em reais. A exclusão de categoria pede confirmação e o banco impede a exclusão quando há produtos vinculados. O acesso ao painel exige login, e as senhas da aplicação são armazenadas como hash.

## Executar no Windows

Abra o PowerShell na pasta do projeto, onde estão `main.py` e `requisitos.txt`. Use a mesma janela para configurar a conexão e iniciar o painel.

### Criar o ambiente virtual

O ambiente virtual fica em `%LOCALAPPDATA%\DocePausa\venv`. O `uv` pode instalar o Python 3.12 ao criar esse ambiente. [Como instalar o uv](https://docs.astral.sh/uv/getting-started/installation/).

```powershell
$docePausaVenv = Join-Path $env:LOCALAPPDATA 'DocePausa\venv'
$docePausaPython = Join-Path $docePausaVenv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $docePausaPython)) {
    uv venv --python 3.12 --seed $docePausaVenv
}
& $docePausaPython --version
& $docePausaPython -m pip install -r requisitos.txt
```

Se já tiver o Python 3.12 e o inicializador `py`, você também pode criar o ambiente com `py -3.12 -m venv $docePausaVenv`. Os comandos seguintes usam diretamente o executável do ambiente virtual.

### Configurar o MySQL

Tenha o MySQL Server 8.4 em execução. Em uma instalação nova no Windows, use o MySQL Configurator para habilitar TCP/IP, escolher a porta e definir a senha da conta de administração. [Configuração do MySQL no Windows](https://dev.mysql.com/doc/refman/8.4/en/mysql-configurator.html).

Informe uma conta MySQL com permissão para criar o banco `doce_pausa` e operar suas tabelas. Ajuste a porta e o usuário conforme a sua instalação. O PowerShell pede a senha sem exibi-la.

```powershell
$env:DOCE_PAUSA_MYSQL_HOST = '127.0.0.1'
$env:DOCE_PAUSA_MYSQL_PORT = '3306'
$env:DOCE_PAUSA_MYSQL_USER = 'root'
$docePausaSenha = Read-Host 'Senha do MySQL' -AsSecureString
$env:DOCE_PAUSA_MYSQL_PASSWORD = [System.Net.NetworkCredential]::new('', $docePausaSenha).Password

Test-NetConnection -ComputerName $env:DOCE_PAUSA_MYSQL_HOST -Port ([int]$env:DOCE_PAUSA_MYSQL_PORT)
```

Com `TcpTestSucceeded` igual a `True`, execute o script que cria o banco e suas tabelas. Você pode reexecutá-lo com os dados existentes.

```powershell
& $docePausaPython -B preparar_banco.py
```

### Criar contas do painel

Execute o comando uma vez para cada conta. Informe nome, login, uma senha escolhida por você e o perfil. Para seguir o roteiro de testes abaixo, use `admin_teste` com o perfil `admin` e `comum_teste` com o perfil `comum`.

```powershell
& $docePausaPython -B criar_usuario.py
```

Use essas contas na tela de login. As credenciais da conexão com o MySQL ficam nas variáveis de ambiente da janela do PowerShell.

### Iniciar o painel

```powershell
& $docePausaPython -B main.py
```

Abra [http://127.0.0.1:5000](http://127.0.0.1:5000) no navegador. Para encerrar o Flask, pressione **Ctrl+C** no PowerShell.

## Testar o painel

### Login e permissões

1. Em uma janela anônima, abra `http://127.0.0.1:5000/categorias`. O painel deve redirecionar para o login.
2. Tente entrar com uma senha incorreta e confira a mensagem de erro. Em seguida, entre como `admin_teste` com a senha escolhida no cadastro.
3. Em um banco recém-criado, o cardápio deve exibir **Nenhum produto cadastrado no momento.**
4. Clique em **Sair** e entre como `comum_teste`. Confira que o cardápio e a lista de categorias abrem. Acesse `/categorias/nova` nessa sessão e verifique a página **Acesso negado**.

### Cadastro, edição e exclusão de categorias

1. Entre como `admin_teste` e abra **Categorias → Nova categoria**. Cadastre `Categoria temporária de teste` e confira a mensagem de sucesso e o item na lista.
2. Abra **Editar**, altere o nome para `Categoria editada de teste` e salve. Confira o nome atualizado.
3. Clique em **Excluir** e depois em **Cancelar**. Verifique se a categoria continua na lista. Abra **Excluir** novamente, confirme e confira a remoção.

### Cardápio com produtos e exclusão bloqueada

Entre como `admin_teste` e cadastre a categoria `Bebidas de teste` pelo painel. Conecte o MySQL Workbench ou o cliente `mysql` à mesma instância usada pelo Flask e execute o SQL abaixo.

```sql
USE doce_pausa;

INSERT INTO produto (nome, preco, categoria_id, criado_por)
SELECT 'Café coado de teste', 7.50, c.id, u.id
FROM categoria AS c
JOIN usuario AS u ON u.login = 'admin_teste' AND u.perfil = 'admin'
LEFT JOIN produto AS p
    ON p.categoria_id = c.id AND p.nome = 'Café coado de teste'
WHERE c.nome = 'Bebidas de teste' AND p.id IS NULL;
```

1. Atualize o **Cardápio** e confira **Café coado de teste**, **Bebidas de teste** e **R$ 7,50**.
2. Em **Categorias**, tente excluir **Bebidas de teste**. A mensagem deve informar que há produtos vinculados e a categoria deve continuar na lista.
3. Pare o Flask com **Ctrl+C**, execute `& $docePausaPython -B preparar_banco.py` e inicie o Flask novamente. Entre no painel e confirme que a categoria e o produto continuam cadastrados.

## Resolver problemas

| Sintoma | O que conferir |
| --- | --- |
| O comando `python` abre a Microsoft Store | Use o comando `uv venv` para criar o ambiente e chame `$docePausaPython` pelo caminho mostrado acima. |
| O painel exibe falha no banco | Confira se o MySQL está em execução, se a porta está correta e se a conta MySQL tem acesso ao banco `doce_pausa`. |
| O login do painel é recusado | Confira a conta criada por `criar_usuario.py` e a senha escolhida no cadastro. |

# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from db import init_db  # Importe a função init_db de db.py

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

# Iniciar o banco de dados
init_db()  # Chame a função init_db para garantir que as tabelas sejam criadas



# Conectar ao banco de dados
def connect_db():
    conn = sqlite3.connect('estoque.db')
    conn.row_factory = sqlite3.Row  # Para acessar as colunas como dicionários
    return conn

# Página inicial
@app.route('/')
def index():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT SUM(quantidade) FROM estoque_papel')
    estoque_papel = c.fetchone()[0] or 0  # Caso não haja dados, retorna 0
    return render_template('index.html', estoque_atual_papel=estoque_papel)

# Adicionar papel
@app.route('/adicionar_papel', methods=['POST'])
def adicionar_papel():
    quantidade = request.form['quantidade']
    conn = connect_db()
    c = conn.cursor()

    # Inserir no estoque de papel
    c.execute('INSERT INTO estoque_papel (quantidade) VALUES (?)', (quantidade,))
    conn.commit()

    # Registrar no histórico
    c.execute('INSERT INTO historico (acao, data) VALUES (?, ?)', ('Adicionou papel', '2025-03-24'))
    conn.commit()

    flash('Papel adicionado com sucesso!', 'success')
    return redirect(url_for('index'))

# Retirar papel
@app.route('/retirar_papel', methods=['POST'])
def retirar_papel():
    quantidade = request.form['quantidade']
    local = request.form['local']
    conn = connect_db()
    c = conn.cursor()
    c.execute('INSERT INTO estoque_papel (quantidade) VALUES (?)', (-int(quantidade),))
    conn.commit()
    flash('Papel retirado com sucesso!', 'success')
    return redirect(url_for('index'))

# Adicionar toner
@app.route('/adicionar_toner', methods=['POST'])
def adicionar_toner():
    marca = request.form['marca']
    tipo = request.form['tipo']
    quantidade = request.form['quantidade']
    validade = request.form['validade']
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO estoque_toner (marca, tipo, quantidade, validade)
        VALUES (?, ?, ?, ?)
    ''', (marca, tipo, quantidade, validade))
    conn.commit()
    flash('Toner adicionado com sucesso!', 'success')
    return redirect(url_for('index'))

# Retirar toner
@app.route('/retirar_toner', methods=['POST'])
def retirar_toner():
    marca = request.form['marca']
    tipo = request.form['tipo']
    quantidade = request.form['quantidade']
    local = request.form['local']
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO estoque_toner (marca, tipo, quantidade, validade)
        VALUES (?, ?, ?, ?)
    ''', (marca, tipo, -int(quantidade), '0000-00-00'))  # Exemplo de data fixa para retirar toner
    conn.commit()
    flash('Toner retirado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/historico')
def historico():
    conn = connect_db()
    c = conn.cursor()
    c.execute('SELECT * FROM historico ORDER BY data DESC')
    registros_historico = c.fetchall()  # Obtém todos os registros de histórico
    return render_template('historico.html', registros_historico=registros_historico)

"""
def listar_tabelas_e_conteudo():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Obter todas as tabelas no banco de dados
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = c.fetchall()

    for tabela in tabelas:
        nome_tabela = tabela[0]
        print(f"Tabela: {nome_tabela}")

        # Consultar e exibir os dados de cada tabela
        c.execute(f"SELECT * FROM {nome_tabela}")
        conteudo = c.fetchall()

        if conteudo:
            for linha in conteudo:
                print(linha)
        else:
            print("A tabela está vazia.")

        print("-" * 50)

    conn.close()
"""
# Chamar a função para listar tabelas e conteúdo
#listar_tabelas_e_conteudo()


if __name__ == '__main__':
    app.run(debug=True)

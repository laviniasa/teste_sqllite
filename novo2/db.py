import sqlite3

# Criação do banco de dados e das tabelas
def init_db():
    conn = sqlite3.connect('estoque.db')
    c = conn.cursor()

    # Criar a tabela para o estoque de papel
    c.execute('''
        CREATE TABLE IF NOT EXISTS estoque_papel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quantidade INTEGER NOT NULL
        )
    ''')

    # Criar a tabela para o estoque de toner
    c.execute('''
        CREATE TABLE IF NOT EXISTS estoque_toner (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            tipo TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            validade DATE NOT NULL
        )
    ''')

    # Criar a tabela para o histórico de ações
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT NOT NULL,
            data TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Iniciar o banco de dados
init_db()

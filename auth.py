import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import sqlite3
from sqlite3 import Error

# Configuração de autenticação
usernames = ['user1', 'user2']
passwords = ['password1', 'password2']  # Senhas em texto simples, mas você deve usar hashes em um ambiente de produção

# Inicializar a autenticação
authenticator = stauth.Authenticate(usernames, passwords, 'cookie_name', 'signature_key', cookie_expiry_days=30)

# Tela de login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    st.sidebar.success(f"Bem-vindo, {username}")

    # Conectar ao banco de dados SQLite
    def create_connection(db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    # Criar a tabela se não existir
    def create_table(conn):
        create_table_sql = """ CREATE TABLE IF NOT EXISTS backtests (
                                    id integer PRIMARY KEY,
                                    username text NOT NULL,
                                    backtest_name text NOT NULL,
                                    data text NOT NULL
                                ); """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    # Inserir um backtest no banco de dados
    def insert_backtest(conn, backtest):
        sql = ''' INSERT INTO backtests(username, backtest_name, data)
                  VALUES(?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, backtest)
        conn.commit()
        return cur.lastrowid

    # Carregar o arquivo CSV
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Visualização dos dados:", df.head())
        
        # Salvar o backtest no banco de dados
        conn = create_connection("backtests.db")
        create_table(conn)
        
        backtest_name = st.text_input("Nome do Backtest")
        if st.button("Salvar Backtest"):
            data_str = df.to_csv(index=False)
            backtest = (username, backtest_name, data_str)
            insert_backtest(conn, backtest)
            st.success("Backtest salvo com sucesso!")

    # Visualizar backtests salvos
    if st.button("Ver Backtests Salvos"):
        conn = create_connection("backtests.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM backtests WHERE username=?", (username,))
        rows = cur.fetchall()
        for row in rows:
            st.write(f"Backtest: {row[2]}")
            st.write(pd.read_csv(pd.compat.StringIO(row[3])))

    # Adicionar opção para visualizar todo o banco de dados
    if st.button("Ver Todo o Banco de Dados"):
        conn = create_connection("backtests.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM backtests")
        rows = cur.fetchall()
        for row in rows:
            st.write(f"Usuário: {row[1]}, Backtest: {row[2]}")
            st.write(pd.read_csv(pd.compat.StringIO(row[3])))

elif authentication_status == False:
    st.error("Nome de usuário/senha incorretos")
elif authentication_status == None:
    st.warning("Por favor, insira seu nome de usuário e senha")

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ==========================================================
# 🔥  BANCO DE DADOS — SQLite
# ==========================================================

def conectar():
    return sqlite3.connect("fintrack.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        tipo TEXT,
        valor REAL,
        categoria TEXT,
        descricao TEXT,
        data TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )""")

    conn.commit()

criar_tabelas()

# ==========================================================
# 🔹 FUNÇÕES DE LOGIN / REGISTRO
# ==========================================================

def registrar_usuario(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?,?)", (usuario, senha))
        conn.commit()
        return True
    except:
        return False

def autenticar(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario=? AND senha=?", (usuario, senha))
    r = cursor.fetchone()
    return r[0] if r else None

# ==========================================================
# 🔥 CRUD de Transações — com DATA MANUAL incluída
# ==========================================================

def adicionar_transacao(user_id, tipo, valor, categoria, descricao, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO transacoes (usuario_id, tipo, valor, categoria, descricao, data)
    VALUES (?,?,?,?,?,?)
    """, (user_id, tipo, valor, categoria, descricao, data))
    conn.commit()

def listar_transacoes(user_id):
    conn = conectar()
    return pd.read_sql_query(f"SELECT * FROM transacoes WHERE usuario_id={user_id}", conn)

def excluir_transacao(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id=?", (id,))
    conn.commit()

def editar_transacao(id, valor, categoria, descricao, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE transacoes SET valor=?, categoria=?, descricao=?, data=? WHERE id=?",
                   (valor, categoria, descricao, data, id))
    conn.commit()

# ==========================================================
# 📊 DASHBOARD FINANCEIRO (Gráficos e Tabelas)
# ==========================================================

def dashboard(user_id):
    df = listar_transacoes(user_id)

    if df.empty:
        st.warning("Nenhuma transação registrada ainda.")
        return

    st.subheader("📌 Resumo Financeiro")
    receita = df[df["tipo"] == "receita"]["valor"].sum()
    despesa = df[df["tipo"] == "despesa"]["valor"].sum()
    saldo = receita - despesa

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Receitas", f"R$ {receita:.2f}")
    col2.metric("Total Despesas", f"R$ {despesa:.2f}")
    col3.metric("Saldo Atual", f"R$ {saldo:.2f}")

    st.subheader("📊 Histórico Completo")
    st.dataframe(df)

    df["data"] = pd.to_datetime(df["data"])
    df_group = df.groupby(["data","tipo"])["valor"].sum().reset_index()

    st.subheader("📈 Evolução Financeira")
    st.line_chart(df_group, x="data", y="valor", color="tipo")

    st.success("Dashboard carregado com sucesso.")

# ==========================================================
# 🔐 LOGIN / LOGOUT / REGISTRO
# ==========================================================

def interface_login():
    st.title("🔐 FinTrack Web — Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user_id = autenticar(usuario, senha)
        if user_id:
            st.session_state["usuario"] = usuario
            st.session_state["user_id"] = user_id
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.write("---")
    st.subheader("Ainda não tem conta?")
    if st.button("Criar Conta"):
        st.session_state["pagina"] = "registro"
        st.rerun()

def interface_registro():
    st.title("📝 Registrar Novo Usuário")

    usuario = st.text_input("Novo Usuário")
    senha = st.text_input("Defina uma Senha", type="password")

    if st.button("Registrar"):
        if registrar_usuario(usuario, senha):
            st.success("Conta criada com sucesso! Faça login.")
            st.session_state["pagina"] = "login"
        else:
            st.error("Nome de usuário já existe.")

    if st.button("Voltar"):
        st.session_state["pagina"] = "login"

# ==========================================================
# 🏛 INTERFACE PRINCIPAL — MENU DASHBOARD
# ==========================================================

def app_principal():

    st.title("💰 FINTRACK WEB — Dashboard Completo")

    menu = st.sidebar.radio("📌 Navegação", [
        "Dashboard Geral",
        "➕ Receita",
        "➖ Despesa",
        "📋 Transações",
        "✏ Editar",
        "🗑 Excluir",
        "🚪 Logout"
    ])

    user_id = st.session_state["user_id"]

    # ----------------- DASHBOARD -----------------
    if menu == "Dashboard Geral":
        dashboard(user_id)

    # ---------------- RECEITA ------------------
    if menu == "➕ Receita":
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        categoria = st.text_input("Categoria")
        descricao = st.text_area("Descrição")
        data = st.date_input("Data da Receita")

        if st.button("Salvar Receita"):
            adicionar_transacao(user_id,"receita",valor,categoria,descricao,str(data))
            st.success("Receita registrada com sucesso!")

    # ---------------- DESPESA ------------------
    if menu == "➖ Despesa":
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        categoria = st.text_input("Categoria")
        descricao = st.text_area("Descrição")
        data = st.date_input("Data da Despesa")

        if st.button("Salvar Despesa"):
            adicionar_transacao(user_id,"despesa",valor,categoria,descricao,str(data))
            st.success("Despesa registrada com sucesso!")

    # ---------------- LISTAR ------------------
    if menu == "📋 Transações":
        st.subheader("Movimentações Financeiras")
        df = listar_transacoes(user_id)
        st.dataframe(df)

    # ---------------- EDITAR ------------------
    if menu == "✏ Editar":
        df = listar_transacoes(user_id)

        if df.empty:
            st.warning("Nenhuma transação para editar.")
        else:
            id_select = st.number_input("ID da transação", min_value=1)
            if st.button("Carregar"):
                dado = df[df["id"]==id_select]
                if not dado.empty:
                    valor = st.number_input("Valor", value=float(dado["valor"].values[0]))
                    categoria = st.text_input("Categoria", dado["categoria"].values[0])
                    descricao = st.text_area("Descrição", dado["descricao"].values[0])
                    data = st.date_input("Data", date.fromisoformat(dado["data"].values[0]))

                    if st.button("Salvar Alterações"):
                        editar_transacao(id_select, valor, categoria, descricao, str(data))
                        st.success("Alterado com sucesso!")
                        st.rerun()
                else:
                    st.error("ID não encontrado.")

    # ---------------- EXCLUIR ------------------
    if menu == "🗑 Excluir":
        id_del = st.number_input("ID para excluir", min_value=1)
        if st.button("Deletar"):
            excluir_transacao(id_del)
            st.success("Removido!")
            st.rerun()

    # ---------------- LOGOUT ------------------
    if menu == "🚪 Logout":
        st.session_state.clear()
        st.rerun()

# ==========================================================
# ▶ EXECUÇÃO
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "login"

if "usuario" not in st.session_state:
    st.session_state["pagina"] = "login"

if st.session_state["pagina"] == "login":
    interface_login()

elif st.session_state["pagina"] == "registro":
    interface_registro()

else:
    app_principal()


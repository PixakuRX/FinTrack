import sqlite3
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ================================
#   BANCO DE DADOS
# ================================
def conectar():
    return sqlite3.connect("fintrack.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        categoria TEXT,
        descricao TEXT,
        data TEXT NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# ================================
#  AUTENTICAÇÃO / LOGIN / REGISTRO
# ================================
def registrar_user(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?,?)", (usuario, senha))
        conn.commit()
        return True
    except:
        return False

def login(usuario, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    result = cursor.fetchone()
    return result[0] if result else None


# ================================
#    CRUD FINANCEIRO (SQLite)
# ================================
def adicionar_transacao(user_id, tipo, valor, categoria, descricao):
    conn = conectar()
    cursor = conn.cursor()
    data = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
    INSERT INTO transacoes (usuario_id, tipo, valor, categoria, descricao, data)
    VALUES (?,?,?,?,?,?)
    """, (user_id, tipo, valor, categoria, descricao, data))
    conn.commit()

def listar_transacoes(user_id):
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM transacoes WHERE usuario_id = ?", conn, params=[user_id])
    return df

def editar_transacao(id, valor, categoria, descricao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE transacoes SET valor=?, categoria=?, descricao=? WHERE id=?
    """, (valor, categoria, descricao, id))
    conn.commit()

def deletar_transacao(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id=?", (id,))
    conn.commit()


# ================================
#   📊 Analytics
# ================================
def gerar_relatorio(user_id):
    df = listar_transacoes(user_id)
    if df.empty:
        return None, None

    total_gastos = df[df["tipo"]=="despesa"]["valor"].sum()
    total_receitas = df[df["tipo"]=="receita"]["valor"].sum()
    saldo = total_receitas - total_gastos

    return total_receitas, total_gastos, saldo

def prever_prox_mes(user_id):
    df = listar_transacoes(user_id)
    if df.empty:
        return "Dados insuficientes"

    ultimos = df.tail(3)["valor"].mean()
    return round(ultimos,2)

def recomenda_financeiro(user_id):
    receitas, gastos, saldo = gerar_relatorio(user_id)
    if saldo < 0:
        return "⚠ Você está gastando mais do que ganha! Corte despesas urgentes."
    elif saldo < receitas * 0.2:
        return "🟡 Bom controle, mas margem baixa. Tente guardar mais 10%."
    else:
        return "🟢 Excelente! Continue assim e invista o excedente."


# ================================
#           INTERFACE WEB
# ================================
st.title("💰 FINTRACK WEB — Controle Financeiro")

# LOGIN
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Criar Conta"])

    with tab1:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            uid = login(usuario, senha)
            if uid:
                st.session_state.user_id = uid
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")

    with tab2:
        new_user = st.text_input("Novo usuário")
        new_pass = st.text_input("Nova senha", type="password")
        if st.button("Registrar-se"):
            if registrar_user(new_user, new_pass):
                st.success("Conta criada com sucesso! Agora faça login.")
            else:
                st.error("Usuário já existe")

    st.stop()


# ================================
#        MENU PRINCIPAL (WEB)
# ================================
menu = st.sidebar.radio("Menu", [
    "➕ Adicionar Receita",
    "➖ Adicionar Despesa",
    "📋 Listar Transações",
    "📊 Analytics",
    "🔮 Previsão Próximo Mês",
    "💡 Recomendações",
    "🗑️ Excluir Transação",
    "🚪 Logout"
])

user_id = st.session_state.user_id

if menu == "➕ Adicionar Receita":
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    categoria = st.text_input("Categoria")
    descricao = st.text_area("Descrição")
    if st.button("Salvar Receita"):
        adicionar_transacao(user_id,"receita",valor,categoria,descricao)
        st.success("Receita registrada!")

if menu == "➖ Adicionar Despesa":
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    categoria = st.text_input("Categoria")
    descricao = st.text_area("Descrição")
    if st.button("Salvar Despesa"):
        adicionar_transacao(user_id,"despesa",valor,categoria,descricao)
        st.success("Despesa registrada!")

if menu == "📋 Listar Transações":
    df = listar_transacoes(user_id)
    st.dataframe(df)

if menu == "📊 Analytics":
    receitas, gastos, saldo = gerar_relatorio(user_id)
    st.write(f"📥 Total Receitas: **R$ {receitas:.2f}**")
    st.write(f"📤 Total Gastos: **R$ {gastos:.2f}**")
    st.write(f"💰 Saldo Final: **R$ {saldo:.2f}**")

if menu == "🔮 Previsão Próximo Mês":
    st.subheader("Previsão baseada nos últimos 3 meses:")
    st.write(f"📈 Próxima estimativa: **R$ {prever_prox_mes(user_id)}**")

if menu == "💡 Recomendações":
    st.subheader("Sugestão automatizada:")
    st.write(recomenda_financeiro(user_id))

if menu == "🗑️ Excluir Transação":
    df = listar_transacoes(user_id)
    id_del = st.selectbox("ID para excluir:", df["id"])
    if st.button("Excluir"):
        deletar_transacao(id_del)
        st.success("Excluído com sucesso.")
        st.rerun()

if menu == "🚪 Logout":
    st.session_state.user_id=None
    st.rerun()

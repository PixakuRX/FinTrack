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

    #  NOVA TABELA DE ORÇAMENTO (BUDGET)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orcamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        categoria TEXT NOT NULL,
        limite REAL NOT NULL,
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
    "📌 Orçamento (Budget)",   # NOVA FUNÇÃO
    "🗑️ Excluir Transação",
    "🚪 Logout"
])

user_id = st.session_state.user_id


# ------------------- RECEITA COM DATA -------------------
if menu == "➕ Adicionar Receita":
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    categoria = st.text_input("Categoria")
    descricao = st.text_area("Descrição")
    data = st.date_input("Data da transação", value=datetime.today()).strftime("%Y-%m-%d")

    if st.button("Salvar Receita"):
        adicionar_transacao(user_id,"receita",valor,categoria,descricao,data)
        st.success("Receita registrada!")


# ------------------- DESPESA COM DATA -------------------
if menu == "➖ Adicionar Despesa":
    valor = st.number_input("Valor", min_value=0.0, format="%.2f")
    categoria = st.text_input("Categoria")
    descricao = st.text_area("Descrição")
    data = st.date_input("Data da transação", value=datetime.today()).strftime("%Y-%m-%d")

    if st.button("Salvar Despesa"):
        adicionar_transacao(user_id,"despesa",valor,categoria,descricao,data)
        st.success("Despesa registrada!")


# LISTAR
if menu == "📋 Listar Transações":
    df = listar_transacoes(user_id)
    st.dataframe(df)

# =============================
#     📊 ANALYTICS 3.0
# =============================
if menu == "📊 Analytics":

    receitas, gastos, saldo = gerar_relatorio(user_id)

    st.header("📈 Visão Geral Financeira")

    col1, col2, col3 = st.columns(3)
    col1.metric("📥 Total de Receitas", f"R$ {receitas:.2f}")
    col2.metric("📤 Total de Gastos", f"R$ {gastos:.2f}")
    col3.metric("💰 Saldo Final", f"R$ {saldo:.2f}")

    st.divider()
    st.subheader("📊 Distribuição Geral")

    # =============================
    #  Pie: Receitas x Gastos
    # =============================
    import matplotlib.pyplot as plt

    fig1, ax1 = plt.subplots()
    valores = [receitas, gastos]
    labels = ["Receitas", "Gastos"]
    ax1.pie(valores, labels=labels, autopct="%1.1f%%")
    ax1.set_title("Receitas vs Gastos")
    st.pyplot(fig1)

    df = listar_transacoes(user_id)

    # =============================
    #  Pie: Gastos por categoria
    # =============================
    st.divider()
    st.subheader("🍽 Gastos por categoria")

    gastos_cat = df[df["tipo"]=="despesa"].groupby("categoria")["valor"].sum()

    if not gastos_cat.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie(gastos_cat.values, labels=gastos_cat.index, autopct="%1.1f%%")
        ax2.set_title("Distribuição dos Gastos")
        st.pyplot(fig2)
    else:
        st.info("Sem dados de gastos ainda.")

    # =============================
    #  Pie: Receitas por categoria
    # =============================
    st.divider()
    st.subheader("💵 Receitas por categoria")

    receitas_cat = df[df["tipo"]=="receita"].groupby("categoria")["valor"].sum()

    if not receitas_cat.empty:
        fig3, ax3 = plt.subplots()
        ax3.pie(receitas_cat.values, labels=receitas_cat.index, autopct="%1.1f%%")
        ax3.set_title("Distribuição das Receitas")
        st.pyplot(fig3)
    else:
        st.info("Sem dados de receitas ainda.")


# =============================
#     🔮 PREVISÃO DO PRÓXIMO MÊS
# =============================
if menu == "🔮 Previsão Próximo Mês":

    st.header("🔮 Projeção Financeira Mensal")

    previsao = prever_prox_mes(user_id)
    df = listar_transacoes(user_id)

    # Converter datas para datetime
    df["data"] = pd.to_datetime(df["data"], format="%Y-%m-%d", errors="coerce")

    # Agrupar últimos 3 meses
    df['mes'] = df['data'].dt.to_period("M").astype(str)
    ultimos = df.groupby('mes')['valor'].sum().tail(3)

    if len(ultimos) < 3:
        st.warning("⚠ São necessários pelo menos 3 meses de dados para previsão.")
    else:
        m1, m2, m3 = ultimos.iloc[-3], ultimos.iloc[-2], ultimos.iloc[-1]

        diff1 = m2 - m1
        diff2 = m3 - m2
        crescimento_medio = (diff1 + diff2) / 2
        tendencia = "📈 Crescimento" if crescimento_medio > 0 else "📉 Queda"

        colA, colB, colC = st.columns(3)
        colA.metric("📅 Mês -2", f"R$ {m1:.2f}")
        colB.metric("📅 Mês -1", f"R$ {m2:.2f}", f"{diff1:+.2f}")
        colC.metric("📅 Último mês", f"R$ {m3:.2f}", f"{diff2:+.2f}")

        st.divider()
        st.subheader("📊 Gráfico Cascata – Evolução até a Previsão")

        import matplotlib.pyplot as plt
        etapas = ["Mês -2", "Mês -1", "Último", "Previsão"]
        valores = [m1, diff1, diff2, previsao - m3]
        acumulado = [m1, m2, m3, previsao]

        fig, ax = plt.subplots(figsize=(6,4))
        cor = ["grey", "red" if diff1 < 0 else "green",
                      "red" if diff2 < 0 else "green",
                      "green" if previsao > m3 else "red"]

        ax.bar(etapas, valores, bottom=[0, m1, m2, m3], color=cor)
        ax.plot(etapas, acumulado, marker="o", linewidth=2)

        ax.set_title("Evolução dos últimos meses → previsão futura")
        st.pyplot(fig)

        st.divider()
        st.subheader("📌 Resultado Final")

        icone = "🟢" if previsao > m3 else "🔴"
        st.write(
            f"{icone} **Previsão para o próximo mês:**\n"
            f"💰 Estimativa aproximada: **R$ {previsao:.2f}**"
        )

        st.info(f"""
        Com base no histórico recente, a tendência atual indica **{tendencia.lower()}**
        com variação média de **R$ {crescimento_medio:.2f} por mês**.
        A projeção sugere que o próximo ciclo financeiro deve fechar próximo de:
        \n➡ **R$ {previsao:.2f}**
        """)



# RECOMENDAÇÕES
if menu == "💡 Recomendações":
    st.subheader("Sugestão automatizada:")
    st.write(recomenda_financeiro(user_id))

# =============================
#   🔥 MODULO DE ORÇAMENTO
# =============================
if menu == "📌 Orçamento (Budget)":

    st.header("📊 Controle de Orçamento por Categoria")

    conn = conectar()
    cursor = conn.cursor()

    # ====================
    # ➕ ADICIONAR NOVO
    # ====================
    categoria = st.text_input("Categoria")
    limite = st.number_input("Definir limite de gastos", min_value=0.0, format="%.2f")

    if st.button("Salvar Orçamento"):
        cursor.execute("INSERT INTO orcamentos (usuario_id, categoria, limite) VALUES (?,?,?)",
                       (user_id, categoria, limite))
        conn.commit()
        st.success("📌 Orçamento registrado!")


    st.divider()
    st.subheader("📄 Orçamentos Registrados")


    # ============================
    # 📥 LISTAR + EDITAR + EXCLUIR
    # ============================
    cursor.execute("SELECT id, categoria, limite FROM orcamentos WHERE usuario_id=?", (user_id,))
    orcamentos = cursor.fetchall()

    df = listar_transacoes(user_id)
    gastos_por_categoria = df[df["tipo"]=="despesa"].groupby("categoria")["valor"].sum()

    for oid, cat, limite in orcamentos:
        gasto = gastos_por_categoria.get(cat, 0)
        progresso = min(gasto / limite, 1)

        with st.expander(f"📌 {cat} — Limite: R$ {limite:.2f} | Usado: R$ {gasto:.2f}"):

            st.progress(progresso)

            if gasto > limite:
                st.error("🚨 Você ultrapassou o orçamento!")
            elif gasto > limite * 0.75:
                st.warning("⚠ Já atingiu 75% do limite!")
            else:
                st.success("🟢 Dentro do limite")

            # ===============================
            # ✏ ALTERAR ORÇAMENTO
            # ===============================
            st.write("### ✏ Editar limite do orçamento")
            novo_limite = st.number_input("Novo limite",
                                          min_value=0.0,
                                          value=float(limite),
                                          key=f"edit{oid}")

            if st.button("Salvar alteração", key=f"btn_edit{oid}"):
                cursor.execute("UPDATE orcamentos SET limite=? WHERE id=?", (novo_limite, oid))
                conn.commit()
                st.success("Limite alterado com sucesso!")
                st.rerun()


            st.write("---")

            # ===============================
            # 🗑 EXCLUIR ORÇAMENTO
            # ===============================
            if st.button("🗑 Excluir orçamento", key=f"del{oid}"):
                cursor.execute("DELETE FROM orcamentos WHERE id=?", (oid,))
                conn.commit()
                st.warning("Orçamento removido.")
                st.rerun()


# DELETAR
if menu == "🗑️ Excluir Transação":
    df = listar_transacoes(user_id)
    id_del = st.selectbox("ID para excluir:", df["id"])
    if st.button("Excluir"):
        deletar_transacao(id_del)
        st.success("Excluído com sucesso.")
        st.rerun()

# LOGOUT
if menu == "🚪 Logout":
    st.session_state.user_id=None
    st.rerun()





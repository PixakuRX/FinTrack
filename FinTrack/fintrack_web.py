# Port web (beta) FinTrack
# Requisitos: streamlit, pandas
# pip install streamlit pandas

import streamlit as st
import pandas as pd
from datetime import datetime
from fintrack import FinTrack  # usa sua classe existente

st.set_page_config(page_title="FinTrack Web (Beta 0,0012)", layout="wide")

# instância do sistema (usa o mesmo arquivo JSON)
sistema = FinTrack()

st.sidebar.title("FinTrack")
menu = st.sidebar.radio("Menu", [
    "➕ Adicionar Receita",
    "➖ Adicionar Despesa",
    "📋 Listar Transações",
    "📊 Analisar Gastos",
    "🔮 Previsão Próximo Mês",
    "💡 Recomendações",
    "📈 Dashboard Completo",
    "✏️ Editar Transação",
    "🗑️ Deletar Transação"
])

def transacoes_para_df(transacoes):
    if not transacoes:
        return pd.DataFrame(columns=['id','data','tipo','categoria','valor','descricao'])
    df = pd.DataFrame(transacoes)
    # garantia de colunas e formatação da data para exibição
    df['data'] = pd.to_datetime(df['data'], format='%Y-%m-%d')
    df = df[['id','data','tipo','categoria','valor','descricao']]
    df = df.sort_values(by='data', ascending=False)
    df['data'] = df['data'].dt.strftime('%d/%m/%Y')
    return df

st.title("📊 FinTrack — Versão Web Completa")

# ---------- ADICIONAR RECEITA ----------
if menu == "➕ Adicionar Receita":
    st.header("➕ Adicionar Receita")
    with st.form("form_receita", clear_on_submit=True):
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        categoria = st.text_input("Categoria", value="Salário")
        descricao = st.text_area("Descrição (opcional)", max_chars=200)
        data_input = st.date_input("Data", value=datetime.now().date())
        enviar = st.form_submit_button("Salvar receita")
    if enviar:
        data_str = data_input.strftime('%Y-%m-%d')
        try:
            # validar categoria com método da sua classe
            cat_valid, aviso = sistema.validar_categoria(categoria, 'receita')
            sistema.adicionar_transacao('receita', valor, cat_valid, descricao, data_str)
            st.success("✅ Receita adicionada com sucesso!")
            if aviso:
                st.info(aviso)
        except Exception as e:
            st.error(f"Erro ao adicionar: {e}")

# ---------- ADICIONAR DESPESA ----------
elif menu == "➖ Adicionar Despesa":
    st.header("➖ Adicionar Despesa")
    with st.form("form_despesa", clear_on_submit=True):
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f", key="val_desp")
        categoria = st.text_input("Categoria", value="Alimentação", key="cat_desp")
        descricao = st.text_area("Descrição (opcional)", max_chars=200, key="desc_desp")
        data_input = st.date_input("Data", value=datetime.now().date(), key="data_desp")
        enviar = st.form_submit_button("Salvar despesa")
    if enviar:
        data_str = data_input.strftime('%Y-%m-%d')
        try:
            cat_valid, aviso = sistema.validar_categoria(categoria, 'despesa')
            sistema.adicionar_transacao('despesa', valor, cat_valid, descricao, data_str)
            st.success("✅ Despesa adicionada com sucesso!")
            if aviso:
                st.info(aviso)
        except Exception as e:
            st.error(f"Erro ao adicionar: {e}")

# ---------- LISTAR TRANSAÇÕES ----------
elif menu == "📋 Listar Transações":
    st.header("📋 Listar Transações")
    col1, col2 = st.columns(2)
    with col1:
        mes = st.selectbox("Mês (ENTER para mês atual)", options=["Atual"] + [f"{i:02d}" for i in range(1,13)], index=0)
    with col2:
        ano = st.number_input("Ano (ENTER para ano atual)", min_value=2000, max_value=2100, value=datetime.now().year)
    # interpretar mês
    if mes == "Atual":
        mes_int = datetime.now().month
    else:
        mes_int = int(mes)
    transacoes = sistema.listar_transacoes(mes_int, int(ano))
    # listar_transacoes já imprime, mas aqui vamos mostrar em tabela
    df = transacoes_para_df(transacoes)
    st.dataframe(df, use_container_width=True)

# ---------- ANALISAR GASTOS ----------
elif menu == "📊 Analisar Gastos":
    st.header("📊 Analisar Gastos (Analytics)")
    mes = st.selectbox("Mês", options=["Atual"] + [f"{i:02d}" for i in range(1,13)], index=0, key="an_mes")
    ano = st.number_input("Ano", min_value=2000, max_value=2100, value=datetime.now().year, key="an_ano")
    mes_int = datetime.now().month if mes=="Atual" else int(mes)
    resultado = sistema.analisar_gastos(mes_int, int(ano))
    if resultado is None:
        st.info("Nenhuma transação para analisar.")
    else:
        st.write("**Receitas:**", f"R$ {resultado['receitas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.write("**Despesas:**", f"R$ {resultado['despesas']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.write("**Saldo:**", f"R$ {resultado['saldo']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        # mostrar breakdown por categoria
        if resultado['gastos_categoria']:
            gasto_cat = pd.DataFrame(list(resultado['gastos_categoria'].items()), columns=['Categoria','Valor'])
            gasto_cat['%'] = gasto_cat['Valor'] / resultado['despesas'] * 100
            st.subheader("Distribuição por categoria")
            st.dataframe(gasto_cat.sort_values('Valor', ascending=False), use_container_width=True)

# ---------- PREVISÃO PRÓXIMO MÊS ----------
elif menu == "🔮 Previsão Próximo Mês":
    st.header("🔮 Previsão para o Próximo Mês")
    previsao = sistema.prever_proximo_mes()
    if not previsao:
        st.info("Dados insuficientes para previsão (registre pelo menos 2 meses).")
    else:
        st.write(f"Receita prevista: R$ {previsao['receita_prevista']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.write(f"Despesa prevista: R$ {previsao['despesa_prevista']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.write(f"Saldo previsto: R$ {previsao['saldo_previsto']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))

# ---------- RECOMENDAÇÕES ----------
elif menu == "💡 Recomendações":
    st.header("💡 Recomendações Inteligentes")
    rec = sistema.gerar_recomendacoes()  # seu método já printa; também pode retornar
    st.info("Verifique o terminal do servidor (ou adapte gerar_recomendacoes para retornar dados).")

# ---------- DASHBOARD ----------
elif menu == "📈 Dashboard Completo":
    st.header("📈 Dashboard Completo")
    anal = sistema.analisar_gastos()
    if not anal:
        st.info("Nenhuma transação registrada.")
    else:
        receitas = anal['receitas']
        despesas = anal['despesas']
        saldo = anal['saldo']
        uso_orcamento = min((despesas / receitas) * 100, 100) if receitas>0 else 0
        st.metric("Receitas", f"R$ {receitas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.metric("Despesas", f"R$ {despesas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.metric("Saldo", f"R$ {saldo:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        st.progress(int(uso_orcamento))
        st.write(f"Uso do orçamento: {uso_orcamento:.1f}%")
        # mostrar top categorias
        if anal['gastos_categoria']:
            gasto_cat = pd.DataFrame(list(anal['gastos_categoria'].items()), columns=['Categoria','Valor'])
            st.subheader("Top categorias")
            st.table(gasto_cat.sort_values('Valor', ascending=False).head(10))

# ---------- EDITAR TRANSAÇÃO ----------
elif menu == "✏️ Editar Transação":
    st.header("✏️ Editar Transação")
    # pega todas as transações e mostra em tabela com id
    todas = sistema.transacoes
    if not todas:
        st.info("Nenhuma transação para editar.")
    else:
        df_all = transacoes_para_df(todas)
        st.dataframe(df_all, use_container_width=True)
        ids = [t['id'] for t in todas]
        escolha = st.selectbox("Escolha o ID da transação para editar", options=ids)
        trans = next((t for t in todas if t['id']==escolha), None)
        if trans:
            col1, col2 = st.columns(2)
            with col1:
                novo_valor = st.number_input("Valor (R$)", value=float(trans['valor']), format="%.2f")
                nova_categoria = st.text_input("Categoria", value=trans['categoria'])
            with col2:
                nova_desc = st.text_area("Descrição", value=trans['descricao'])
                nova_data = st.date_input("Data", value=datetime.strptime(trans['data'],'%Y-%m-%d').date())
            if st.button("Salvar alterações"):
                # aplica alterações sem usar a função interativa editar_transacao
                trans['valor'] = float(novo_valor)
                trans['categoria'] = nova_categoria
                trans['descricao'] = nova_desc
                trans['data'] = nova_data.strftime('%Y-%m-%d')
                sistema.salvar_dados()
                st.success("Transação atualizada com sucesso!")
                st.experimental_rerun()

# ---------- DELETAR TRANSAÇÃO ----------
elif menu == "🗑️ Deletar Transação":
    st.header("🗑️ Deletar Transação")
    todas = sistema.transacoes
    if not todas:
        st.info("Nenhuma transação para deletar.")
    else:
        df_all = transacoes_para_df(todas)
        st.dataframe(df_all, use_container_width=True)
        ids = [t['id'] for t in todas]
        escolha = st.selectbox("Escolha o ID da transação a deletar", options=ids, key="del_select")
        trans = next((t for t in todas if t['id']==escolha), None)
        if trans:
            st.write("Você selecionou:")
            st.write(f"ID: {trans['id']} — {trans['tipo'].upper()} — {trans['categoria']} — R$ {trans['valor']:.2f} — {trans['data']}")
            if st.button("Confirmar exclusão"):
                sistema.transacoes.remove(trans)
                sistema.salvar_dados()
                st.success("Transação deletada com sucesso!")
                st.experimental_rerun()

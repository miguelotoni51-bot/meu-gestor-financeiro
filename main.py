import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Gestor com Nuvem", layout="wide")

# Conectar ao Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para ler dados da planilha
def carregar_dados():
    return conn.read(ttl="10m") # Atualiza a cada 10 minutos ou ao forçar

# --- CÁLCULOS FINANCEIROS ---
def calcular_impostos(bruto):
    if bruto <= 1412: inss = bruto * 0.075
    elif bruto <= 2666.68: inss = (bruto * 0.09) - 21.18
    elif bruto <= 4000.03: inss = (bruto * 0.12) - 101.18
    else: inss = min((bruto * 0.14) - 181.18, 908.85)
    
    base_ir = bruto - inss
    if base_ir <= 2259.20: irrf = 0
    elif base_ir <= 2826.65: irrf = (base_ir * 0.075) - 169.44
    elif base_ir <= 3751.05: irrf = (base_ir * 0.15) - 381.44
    elif base_ir <= 4664.68: irrf = (base_ir * 0.225) - 662.77
    else: irrf = (base_ir * 0.275) - 896.00
    return round(inss, 2), round(irrf, 2)

# --- INTERFACE ---
st.title("💰 Gestor com Salvamento em Nuvem")

# Carregar despesas salvas
df_despesas = carregar_dados()

with st.sidebar:
    st.header("Renda e Fixo")
    salario_bruto = st.number_input("Salário Bruto", value=5000.0)
    moradia = st.number_input("Habitação", value=1200.0)
    
    st.divider()
    st.header("📝 Adicionar Nova Despesa")
    with st.form("form_gsheets"):
        novo_nome = st.text_input("Nome da conta")
        novo_valor = st.number_input("Valor R$", min_value=0.0)
        if st.form_submit_button("Salvar na Nuvem"):
            # Lógica para adicionar nova linha ao dataframe e atualizar planilha
            nova_linha = pd.DataFrame([{"nome": novo_nome, "valor": novo_valor}])
            updated_df = pd.concat([df_despesas, nova_linha], ignore_index=True)
            conn.update(data=updated_df)
            st.success("Salvo com sucesso!")
            st.rerun()

    st.divider()
    banco = st.selectbox("Banco", ["Sicoob", "Nubank", "Inter", "Itaú", "Bradesco"])
    aporte_mensal = st.number_input("Aporte Mensal", value=500.0)

# --- PROCESSAMENTO ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_extras = df_despesas['valor'].sum() if not df_despesas.empty else 0
total_despesas = moradia + total_extras
saldo_final = liquido - total_despesas - aporte_mensal

# --- EXIBIÇÃO ---
st.subheader("📌 Resumo")
col1, col2, col3 = st.columns(3)
col1.metric("Salário Líquido", f"R$ {liquido:.2f}")
col2.metric("Despesas Totais", f"R$ {total_despesas:.2f}")
col3.metric("Saldo Livre", f"R$ {saldo_final:.2f}")

if not df_despesas.empty:
    with st.expander("Ver lista de despesas salvas"):
        st.table(df_despesas)

st.divider()
# Gráfico de barras acumulativo
st.subheader(f"📊 Acúmulo no {banco}")
meses_range = list(range(1, 13))
acumulado = [aporte_mensal * m for m in meses_range] # Simplificado para exemplo
fig_col = px.bar(x=meses_range, y=acumulado, labels={'x':'Mês', 'y':'Total R$'})
st.plotly_chart(fig_col, use_container_width=True)

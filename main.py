import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor Financeiro", layout="wide")

# --- INICIALIZAÇÃO DA MEMÓRIA TEMPORÁRIA ---
if 'despesas_extras' not in st.session_state:
    st.session_state.despesas_extras = []

# --- FUNÇÕES DE CÁLCULO ---
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

def projetar_investimento(aporte, meses, banco):
    taxas = {
        "Nubank": 0.009, "Inter": 0.009, "Sicoob": 0.0085, "PicPay": 0.0092, 
        "Mercado Pago": 0.0092, "Itaú": 0.007, "Bradesco": 0.007, 
        "Santander": 0.007, "Banco do Brasil": 0.007, "Caixa": 0.005
    }
    taxa_mensal = taxas.get(banco, 0.007)
    acumulado = []
    for m in range(1, meses + 1):
        valor = aporte * (((1 + taxa_mensal)**m - 1) / taxa_mensal)
        acumulado.append(round(valor, 2))
    return acumulado

# --- INTERFACE LATERAL ---
with st.sidebar:
    st.header("💰 Renda")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0)
    
    st.divider()
    st.header("📝 Adicionar Despesa")
    with st.form("nova_despesa", clear_on_submit=True):
        nome_d = st.text_input("Nome da despesa (ex: Aluguel, Luz)")
        valor_d = st.number_input("Valor (R$)", min_value=0.0)
        adicionar = st.form_submit_button("Adicionar Tópico")
        
        if adicionar and nome_d:
            st.session_state.despesas_extras.append({"nome": nome_d, "valor": valor_d})
            st.rerun()

    if st.button("🗑️ Limpar Lista"):
        st.session_state.despesas_extras = []
        st.rerun()

    st.divider()
    st.header("📈 Investimento")
    banco = st.selectbox("Banco", ["Sicoob", "Nubank", "Inter", "PicPay", "Itaú", "Bradesco"])
    aporte_mensal = st.number_input("Aporte Mensal", value=500.0)
    meses_invest = st.slider("Meses", 1, 60, 12)

# --- PROCESSAMENTO ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_extras = sum(item['valor'] for item in st.session_state.despesas_extras)
saldo_final = liquido - total_extras - aporte_mensal
historico_inv = projetar_investimento(aporte_mensal, meses_invest, banco)

# --- EXIBIÇÃO PRINCIPAL ---
st.title(f"📊 Gestor Financeiro Pessoal")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário Líquido", f"R$ {liquido:.2f}")
c2.metric("Total de Gastos", f"R$ {total_extras:.2f}")
c3.metric("Saldo Livre", f"R$ {saldo_final:.2f}")
c4.metric("Total Acumulado", f"R$ {historico_inv[-1]:.2f}")

st.divider()

col_lista, col_graf = st.columns(2)

with col_lista:
    st.subheader("📋 Seus Tópicos de Despesas")
    if st.session_state.despesas_extras:
        df_view = pd.DataFrame(st.session_state.despesas_extras)
        st.table(df_view)
    else:
        st.info("Adicione despesas na barra lateral para começar.")

with col_graf:
    st.subheader(f"📊 Projeção de Acúmulo: {banco}")
    df_fig = pd.DataFrame({
        "Mês": list(range(1, meses_invest + 1)),
        "Valor Acumulado": historico_inv
    })
    fig = px.bar(df_fig, x="Mês", y="Valor Acumulado", color="Valor Acumulado", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

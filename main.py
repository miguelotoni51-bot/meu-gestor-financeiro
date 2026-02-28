import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor Financeiro Nuvem", layout="wide")

# --- CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lê os dados da planilha (cache de 2 segundos para atualizar rápido)
    df_despesas = conn.read(ttl=2)
except Exception as e:
    st.error("Erro ao conectar com a planilha. Verifique o link nos Secrets.")
    df_despesas = pd.DataFrame(columns=["nome", "valor"])

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
    st.header("💰 Minha Renda")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0)
    
    st.divider()
    st.header("📝 Adicionar Despesa")
    with st.form("nova_despesa", clear_on_submit=True):
        nome_d = st.text_input("Ex: Netflix, Internet...")
        valor_d = st.number_input("Valor (R$)", min_value=0.0)
        enviar = st.form_submit_button("Salvar na Nuvem")
        
        if enviar and nome_d:
            nova_linha = pd.DataFrame([{"nome": nome_d, "valor": valor_d}])
            df_atualizado = pd.concat([df_despesas, nova_linha], ignore_index=True)
            conn.update(data=df_atualizado)
            st.success("Salvo!")
            st.rerun()

    if st.button("🗑️ Limpar Tudo (Nuvem)"):
        df_reset = pd.DataFrame(columns=["nome", "valor"])
        conn.update(data=df_reset)
        st.rerun()

    st.divider()
    st.header("📈 Investimento")
    banco = st.selectbox("Banco", ["Sicoob", "Nubank", "Inter", "PicPay", "Itaú"])
    aporte = st.number_input("Aporte Mensal", value=500.0)
    meses = st.slider("Meses", 1, 60, 12)

# --- PROCESSAMENTO ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_extras = df_despesas["valor"].sum() if not df_despesas.empty else 0
saldo_final = liquido - total_extras - aporte
historico = projetar_investimento(aporte, meses, banco)

# --- VISUALIZAÇÃO ---
st.title(f"📊 Gestor Financeiro - {banco}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salário Líquido", f"R$ {liquido:.2f}")
c2.metric("Despesas Adicionais", f"R$ {total_extras:.2f}")
c3.metric("Saldo Livre", f"R$ {saldo_final:.2f}")
c4.metric("Total Acumulado", f"R$ {historico[-1]:.2f}")

st.divider()

col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📋 Lista de Despesas (Nuvem)")
    if not df_despesas.empty:
        st.dataframe(df_despesas, use_container_width=True)
    else:
        st.info("Nenhuma despesa salva.")

with col_dir:
    st.subheader(f"📊 Evolução do Investimento ({banco})")
    df_fig = pd.DataFrame({"Mês": list(range(1, meses+1)), "Valor": historico})
    fig = px.bar(df_fig, x="Mês", y="Valor", color="Valor", color_continuous_scale="Greens")
    st.plotly_chart(fig, use_container_width=True)

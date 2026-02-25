import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.express as px

# Configuração da IA (Pegando a chave de forma segura)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
except:
    st.error("Configure sua API KEY do Google nos Secrets do Streamlit!")

# --- FUNÇÕES DE CÁLCULO ---
def calcular_impostos(bruto):
    # INSS 2024/2025
    if bruto <= 1412: inss = bruto * 0.075
    elif bruto <= 2666.68: inss = (bruto * 0.09) - 21.18
    elif bruto <= 4000.03: inss = (bruto * 0.12) - 101.18
    else: inss = min((bruto * 0.14) - 181.18, 908.85) # Teto INSS
    
    # IRRF
    base_ir = bruto - inss
    if base_ir <= 2259.20: irrf = 0
    elif base_ir <= 2826.65: irrf = (base_ir * 0.075) - 169.44
    elif base_ir <= 3751.05: irrf = (base_ir * 0.15) - 381.44
    elif base_ir <= 4664.68: irrf = (base_ir * 0.225) - 662.77
    else: irrf = (base_ir * 0.275) - 896.00
    return round(inss, 2), round(irrf, 2)

# --- INTERFACE ---
st.set_page_config(page_title="IA Financeira", layout="wide")
st.title("🤖 Consultor Financeiro com IA")

with st.sidebar:
    st.header("Dados Financeiros")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0)
    banco = st.selectbox("Seu Banco de Investimento", 
                        ["Nubank", "Inter", "PicPay", "Mercado Pago", "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa"])
    aporte = st.number_input("Investimento Mensal (R$)", value=500.0)
    meses = st.slider("Prazo (Meses)", 1, 60, 12)

# Processamento
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf

# Layout de Colunas
c1, c2, c3 = st.columns(3)
c1.metric("Líquido", f"R$ {liquido:.2f}")
c2.metric("Impostos (Total)", f"R$ {v_inss + v_irrf:.2f}")
c3.metric("Banco Escolhido", banco)

# --- CHAMADA DA IA ---
if st.button("Pedir Análise da IA"):
    with st.spinner("A IA está analisando os impostos e o mercado..."):
        prompt = f"""
        Sou brasileiro, recebo R$ {salario_bruto} bruto. 
        Meus impostos são: INSS R$ {v_inss} e IRRF R$ {v_irrf}.
        Quero investir R$ {aporte} por mês no banco {banco} por {meses} meses.
        Com base na economia brasileira atual (SELIC e CDI):
        1. Analise se meu imposto está alto.
        2. Faça uma projeção de quanto terei no {banco} ao final de {meses} meses (considere as taxas médias desse banco).
        3. Dê uma dica curta de como economizar.
        Seja direto e use emojis.
        """
        response = model.generate_content(prompt)
        st.write("---")
        st.subheader("💡 Parecer da Inteligência Artificial")
        st.info(response.text)

# Gráfico simples
st.divider()
df = pd.DataFrame({
    "Categoria": ["Líquido", "INSS", "IRRF"],
    "Valor": [liquido, v_inss, v_irrf]
})
fig = px.bar(df, x="Categoria", y="Valor", color="Categoria", title="Composição do Salário Bruto")
st.plotly_chart(fig)

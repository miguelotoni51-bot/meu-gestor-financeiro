import streamlit as st
import pandas as pd
import plotly.express as px

# --- FUNÇÕES DE CÁLCULO ---
def calcular_impostos(bruto):
    # INSS 2024/2025 (Tabela Simplificada)
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

def projetar_investimento(aporte, meses, banco):
    # Taxas estimadas (CDI anual em ~11.25%)
    taxas = {
        "Nubank": 0.009, "Inter": 0.009, "PicPay": 0.0092, 
        "Mercado Pago": 0.0092, "Itaú": 0.007, "Bradesco": 0.007, 
        "Santander": 0.007, "Banco do Brasil": 0.007, "Caixa": 0.005
    }
    taxa_mensal = taxas.get(banco, 0.007)
    # Cálculo de Juros Compostos para aportes mensais
    total = aporte * (((1 + taxa_mensal)**meses - 1) / taxa_mensal)
    return round(total, 2)

# --- INTERFACE ---
st.set_page_config(page_title="Gestor Financeiro", layout="wide")
st.title("💰 Gestor Financeiro & Projeção")

with st.sidebar:
    st.header("Configurações")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0, step=100.0)
    banco = st.selectbox("Seu Banco de Investimento", 
                        ["Nubank", "Inter", "PicPay", "Mercado Pago", "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa"])
    aporte = st.number_input("Investimento Mensal (R$)", value=500.0, step=50.0)
    meses = st.slider("Prazo (Meses)", 1, 60, 12)

# Processamento de cálculos
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_investido = projetar_investimento(aporte, meses, banco)

# Exibição de Métricas
c1, c2, c3 = st.columns(3)
c1.metric("Salário Líquido", f"R$ {liquido:.2f}")
c2.metric("Total Impostos", f"R$ {v_inss + v_irrf:.2f}")
c3.metric(f"Projeção no {banco}", f"R$ {total_investido:.2f}")

st.divider()

# Gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("📊 Distribuição do Salário Bruto")
    df_pizza = pd.DataFrame({
        "Categoria": ["Líquido", "INSS", "IRRF"],
        "Valor": [liquido, v_inss, v_irrf]
    })
    fig_pizza = px.pie(df_pizza, values="Valor", names="Categoria", hole=0.4)
    st.plotly_chart(fig_pizza, use_container_width=True)

with col_graf2:
    st.subheader("📈 Crescimento do Investimento")
    # Criar histórico de crescimento
    historico = [projetar_investimento(aporte, m, banco) for m in range(1, meses + 1)]
    df_linha = pd.DataFrame({"Mês": list(range(1, meses + 1)), "Total Acumulado": historico})
    fig_linha = px.line(df_linha, x="Mês", y="Total Acumulado", markers=True)
    st.plotly_chart(fig_linha, use_container_width=True)

st.success(f"Dica: Investindo no {banco}, você terá aproximadamente R$ {total_investido:.2f} após {meses} meses.")

import streamlit as st
import pandas as pd
import plotly.express as px

# --- FUNÇÕES DE CÁLCULO ---
def calcular_impostos(bruto):
    # Tabela INSS 2024/2025
    if bruto <= 1412: inss = bruto * 0.075
    elif bruto <= 2666.68: inss = (bruto * 0.09) - 21.18
    elif bruto <= 4000.03: inss = (bruto * 0.12) - 101.18
    else: inss = min((bruto * 0.14) - 181.18, 908.85)
    
    # Tabela IRRF
    base_ir = bruto - inss
    if base_ir <= 2259.20: irrf = 0
    elif base_ir <= 2826.65: irrf = (base_ir * 0.075) - 169.44
    elif base_ir <= 3751.05: irrf = (base_ir * 0.15) - 381.44
    elif base_ir <= 4664.68: irrf = (base_ir * 0.225) - 662.77
    else: irrf = (base_ir * 0.275) - 896.00
    return round(inss, 2), round(irrf, 2)

def projetar_investimento(aporte, meses, banco):
    taxas = {
        "Nubank": 0.009, "Inter": 0.009, "PicPay": 0.0092, 
        "Mercado Pago": 0.0092, "Itaú": 0.007, "Bradesco": 0.007, 
        "Santander": 0.007, "Banco do Brasil": 0.007, "Caixa": 0.005
    }
    taxa_mensal = taxas.get(banco, 0.007)
    total = aporte * (((1 + taxa_mensal)**meses - 1) / taxa_mensal)
    return round(total, 2)

# --- INTERFACE ---
st.set_page_config(page_title="Gestor Financeiro Completo", layout="wide")
st.title("💰 Gestor Financeiro Pessoal")

# Barra Lateral (Inputs)
with st.sidebar:
    st.header("📥 Entradas de Valor")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0, step=100.0)
    
    st.divider()
    st.header("💳 Despesas Particulares")
    # Campos para despesas manuais
    moradia = st.number_input("Habitação/Aluguer (R$)", value=1200.0)
    alimentacao = st.number_input("Alimentação (R$)", value=800.0)
    outros_gastos = st.number_input("Outras Contas (Luz, Internet, Lazer) (R$)", value=500.0)
    
    st.divider()
    st.header("📈 Investimento")
    banco = st.selectbox("Banco para Investir", ["Nubank", "Inter", "PicPay", "Mercado Pago", "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa"])
    aporte_mensal = st.number_input("Valor do Investimento Mensal (R$)", value=500.0)
    meses = st.slider("Prazo (Meses)", 1, 60, 12)

# --- PROCESSAMENTO ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_despesas = moradia + alimentacao + outros_gastos
saldo_final = liquido - total_despesas - aporte_mensal
total_acumulado = projetar_investimento(aporte_mensal, meses, banco)

# --- EXIBIÇÃO DE MÉTRICAS ---
st.subheader("📌 Resumo do Mês")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Salário Líquido", f"R$ {liquido:.2f}")
m2.metric("Total Despesas", f"R$ {total_despesas:.2f}")
m3.metric("Investimento", f"R$ {aporte_mensal:.2f}")

if saldo_final >= 0:
    m4.metric("SALDO LIVRE FINAL", f"R$ {saldo_final:.2f}", delta="Sobrou!")
else:
    m4.metric("SALDO LIVRE FINAL", f"R$ {saldo_final:.2f}", delta="Défice", delta_color="inverse")

st.divider()

# --- GRÁFICOS ---
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Distribuição de Gastos")
    dados_pizza = {
        "Categoria": ["Saldo Livre", "Despesas Particulares", "Investimento", "Impostos"],
        "Valor": [max(0, saldo_final), total_despesas, aporte_mensal, v_inss + v_irrf]
    }
    df_p = pd.DataFrame(dados_pizza)
    fig_p = px.pie(df_p, values="Valor", names="Categoria", hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    st.subheader(f"📈 Futuro no {banco}")
    historico = [projetar_investimento(aporte_mensal, m, banco) for m in range(1, meses + 1)]
    df_l = pd.DataFrame({"Mês": list(range(1, meses + 1)), "Total": historico})
    fig_l = px.area(df_l, x="Mês", y="Total", title=f"Património após {meses} meses")
    st.plotly_chart(fig_l, use_container_width=True)

# --- MENSAGENS DE ALERTA ---
if saldo_final < 0:
    st.error(f"🚨 Atenção: As tuas despesas e investimentos superam o teu rendimento em R$ {abs(saldo_final):.2f}!")
elif saldo_final < (salario_bruto * 0.1):
    st.warning("💡 Dica: O teu saldo livre está baixo. Tenta reduzir as despesas particulares para aumentar a tua segurança.")
else:
    st.success(f"✅ Excelente gestão! Terás R$ {saldo_final:.2f} livres para usar como quiseres após todas as obrigações.")

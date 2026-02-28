import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor Financeiro Pró", layout="wide")

# --- INICIALIZAÇÃO DO ESTADO (Para não perder dados ao clicar) ---
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
    # Taxas aproximadas de CDB/Rendimento (Mensal)
    taxas = {
        "Nubank": 0.009, "Inter": 0.009, "PicPay": 0.0092, 
        "Mercado Pago": 0.0092, "Itaú": 0.007, "Bradesco": 0.007, 
        "Santander": 0.007, "Banco do Brasil": 0.007, "Caixa": 0.005,
        "Sicoob": 0.0085  # Adicionado Sicoob
    }
    taxa_mensal = taxas.get(banco, 0.007)
    # Lista de acúmulo mensal para o gráfico de colunas
    acumulado_mensal = []
    for m in range(1, meses + 1):
        valor = aporte * (((1 + taxa_mensal)**m - 1) / taxa_mensal)
        acumulado_mensal.append(round(valor, 2))
    return acumulado_mensal

# --- INTERFACE ---
st.title("💰 Gestor Financeiro com Memória de Sessão")

with st.sidebar:
    st.header("📥 Renda")
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0, step=100.0)
    
    st.divider()
    st.header("💳 Despesas Fixas")
    moradia = st.number_input("Habitação (R$)", value=1200.0)
    alimentacao = st.number_input("Alimentação (R$)", value=800.0)
    
    st.divider()
    st.header("📝 Outras Despesas (Tópicos)")
    # Sistema para adicionar despesas personalizadas
    with st.form("nova_despesa"):
        nome_d = st.text_input("Nome da Despesa (ex: Netflix)")
        valor_d = st.number_input("Valor (R$)", min_value=0.0)
        if st.form_submit_button("Adicionar Tópico"):
            if nome_d and valor_d > 0:
                st.session_state.despesas_extras.append({"nome": nome_d, "valor": valor_d})
    
    if st.session_state.despesas_extras:
        if st.button("Limpar Tópicos"):
            st.session_state.despesas_extras = []
            st.rerun()

    st.divider()
    st.header("📈 Investimento")
    banco = st.selectbox("Banco para Investir", 
                        ["Nubank", "Inter", "Sicoob", "PicPay", "Mercado Pago", "Itaú", "Bradesco", "Santander", "Banco do Brasil", "Caixa"])
    aporte_mensal = st.number_input("Aporte Mensal (R$)", value=500.0)
    meses = st.slider("Prazo (Meses)", 1, 60, 12)

# --- PROCESSAMENTO ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf

# Somar despesas fixas + tópicos extras
total_extras = sum(d['valor'] for d in st.session_state.despesas_extras)
total_despesas = moradia + alimentacao + total_extras

saldo_final = liquido - total_despesas - aporte_mensal
historico_investimento = projetar_investimento(aporte_mensal, meses, banco)
total_acumulado = historico_investimento[-1]

# --- EXIBIÇÃO ---
st.subheader("📌 Resumo Atual")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Salário Líquido", f"R$ {liquido:.2f}")
m2.metric("Total Despesas", f"R$ {total_despesas:.2f}")
m3.metric("Investimento", f"R$ {aporte_mensal:.2f}")
m4.metric("SALDO LIVRE", f"R$ {saldo_final:.2f}", delta="Livre" if saldo_final > 0 else "Déficit")

# Listagem dos tópicos criados
if st.session_state.despesas_extras:
    with st.expander("Ver Tópicos de Despesas Adicionais"):
        for d in st.session_state.despesas_extras:
            st.write(f"• **{d['nome']}**: R$ {d['valor']:.2f}")

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Composição de Gastos")
    dados_p = {
        "Categoria": ["Saldo Livre", "Despesas", "Investimento", "Impostos"],
        "Valor": [max(0, saldo_final), total_despesas, aporte_mensal, v_inss + v_irrf]
    }
    fig_p = px.pie(pd.DataFrame(dados_p), values="Valor", names="Categoria", hole=0.4)
    st.plotly_chart(fig_p, use_container_width=True)

with c2:
    st.subheader(f"📊 Acúmulo no {banco} (Mensal)")
    df_invest = pd.DataFrame({
        "Mês": list(range(1, meses + 1)),
        "Total Acumulado (R$)": historico_investimento
    })
    # Gráfico de COLUNAS como solicitado
    fig_col = px.bar(df_invest, x="Mês", y="Total Acumulado (R$)", 
                     text_auto='.2s', color="Total Acumulado (R$)",
                     color_continuous_scale="Viridis")
    st.plotly_chart(fig_col, use_container_width=True)

if saldo_final < 0:
    st.error(f"🚨 Orçamento estourado em R$ {abs(saldo_final):.2f}")

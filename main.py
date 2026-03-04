import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestor Financeiro Inteligente", layout="wide")

# --- INICIALIZAÇÃO DA MEMÓRIA ---
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
    salario_bruto = st.number_input("Salário Bruto (R$)", value=5000.0, step=100.0)
    
    st.divider()
    st.header("📝 Categorizar Despesa")
    with st.form("nova_despesa", clear_on_submit=True):
        categoria = st.selectbox("Categoria", ["🏠 Habitação", "🍎 Alimentação", "🚗 Transporte", "🎭 Lazer", "💊 Saúde", "🛠️ Outros"])
        nome_d = st.text_input("Descrição (ex: Aluguel, Ifood)")
        valor_d = st.number_input("Valor (R$)", min_value=0.0)
        adicionar = st.form_submit_button("Adicionar Despesa")
        
        if adicionar and nome_d:
            st.session_state.despesas_extras.append({"categoria": categoria, "nome": nome_d, "valor": valor_d})
            st.rerun()

    if st.button("🗑️ Limpar Tudo"):
        st.session_state.despesas_extras = []
        st.rerun()

    st.divider()
    st.header("📈 Plano de Investimento")
    banco = st.selectbox("Banco para Projeção", ["Sicoob", "Nubank", "Inter", "PicPay", "Itaú"])
    aporte_mensal = st.number_input("Quanto investir/mês", value=500.0)
    meses_invest = st.slider("Prazo em Meses", 1, 60, 12)

# --- PROCESSAMENTO DE DADOS ---
v_inss, v_irrf = calcular_impostos(salario_bruto)
liquido = salario_bruto - v_inss - v_irrf
total_despesas = sum(item['valor'] for item in st.session_state.despesas_extras)
saldo_final = liquido - total_despesas - aporte_mensal
historico_inv = projetar_investimento(aporte_mensal, meses_invest, banco)

# --- EXIBIÇÃO PRINCIPAL ---
st.title("🤖 Seu Consultor Financeiro Particular")

# Métricas de topo
c1, c2, c3, c4 = st.columns(4)
c1.metric("Renda Líquida", f"R$ {liquido:.2f}")
c2.metric("Gastos Cadastrados", f"R$ {total_despesas:.2f}")
c3.metric("Saldo Livre", f"R$ {saldo_final:.2f}")
c4.metric("Patrimônio Futuro", f"R$ {historico_inv[-1]:.2f}")

st.divider()

# --- DIAGNÓSTICO DE SAÚDE FINANCEIRA ---
st.subheader("💡 Diagnóstico de Saúde Financeira")
if liquido > 0:
    perc_gastos = (total_despesas / liquido) * 100
    if saldo_final < 0:
        st.error(f"🚨 **ALERTA:** Você está gastando mais do que recebe! Seu déficit é de R$ {abs(saldo_final):.2f}. Reveja seus gastos de 'Lazer' ou 'Outros'.")
    elif perc_gastos > 70:
        st.warning(f"⚠️ **CUIDADO:** Seus gastos fixos/variáveis ocupam {perc_gastos:.1f}% da sua renda. O ideal é que fiquem abaixo de 50% para sobrar para investimentos.")
    elif aporte_mensal > 0:
        st.success(f"✅ **PARABÉNS:** Você está destinando {(aporte_mensal/liquido)*100:.1f}% para o futuro. Sua gestão está sólida!")
else:
    st.info("Insira seu salário bruto para ver o diagnóstico.")

st.divider()

# --- GRÁFICOS E TABELAS ---
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📊 Onde está seu dinheiro?")
    if st.session_state.despesas_extras:
        df_pizza = pd.DataFrame(st.session_state.despesas_extras)
        # Agrupar por categoria para o gráfico
        df_grouped = df_pizza.groupby("categoria")["valor"].sum().reset_index()
        fig_pizza = px.pie(df_grouped, values="valor", names="categoria", hole=0.4, 
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pizza, use_container_width=True)
    else:
        st.info("Adicione despesas na lateral para ver a distribuição.")

with col_dir:
    st.subheader(f"📈 Acúmulo no {banco}")
    df_fig = pd.DataFrame({
        "Mês": list(range(1, meses_invest + 1)),
        "Valor Acumulado": historico_inv
    })
    fig_col = px.bar(df_fig, x="Mês", y="Valor Acumulado", color="Valor Acumulado", color_continuous_scale="Viridis")
    st.plotly_chart(fig_col, use_container_width=True)



[Image of 50-30-20 rule pie chart]


# Tabela detalhada no final
if st.session_state.despesas_extras:
    with st.expander("📄 Detalhamento das Despesas"):
        st.table(pd.DataFrame(st.session_state.despesas_extras))

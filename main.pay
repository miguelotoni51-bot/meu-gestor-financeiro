import streamlit as st

def calcular_inss(salario_bruto):
    # Tabela INSS 2024/2025
    faixas = [(1412.00, 0.075), (2666.68, 0.09), (4000.03, 0.12), (7786.02, 0.14)]
    inss = 0
    teto = 7786.02
    salario_base = min(salario_bruto, teto)
    
    anterior = 0
    for limite, taxa in faixas:
        if salario_base > limite:
            inss += (limite - anterior) * taxa
            anterior = limite
        else:
            inss += (salario_base - anterior) * taxa
            break
    return inss

def calcular_irrf(salario_base_ir):
    # Tabela IRRF (Com dedução simplificada inclusa na lógica)
    if salario_base_ir <= 2259.20:
        return 0
    elif salario_base_ir <= 2826.65:
        return (salario_base_ir * 0.075) - 169.44
    elif salario_base_ir <= 3751.05:
        return (salario_base_ir * 0.15) - 381.44
    elif salario_base_ir <= 4664.68:
        return (salario_base_ir * 0.225) - 662.77
    else:
        return (salario_base_ir * 0.275) - 896.00

# Interface do Usuário
st.title("💰 Meu Gestor Financeiro Pessoal")
st.sidebar.header("Configurações")

# 1. Entrada de Renda
salario_bruto = st.sidebar.number_input("Salário Bruto (R$)", min_value=0.0, value=5000.0)

# Cálculos de Impostos
valor_inss = calcular_inss(salario_bruto)
valor_irrf = calcular_irrf(salario_bruto - valor_inss)
salario_liquido_real = salario_bruto - valor_inss - valor_irrf

# 2. Despesas
st.subheader("📊 Gastos Mensais")
gastos = st.text_area("Descreva suas despesas (Ex: Aluguel: 1200, Internet: 100)", "Aluguel: 0\nAlimentação: 0")
total_despesas = st.number_input("Total das Despesas Fixas (R$)", min_value=0.0)

# 3. Investimentos
st.subheader("📈 Planejamento de Investimentos")
aporte_mensal = st.number_input("Quanto vai investir este mês? (R$)", min_value=0.0)
taxa_juros = st.slider("Taxa de juros anual esperada (%)", 0.0, 20.0, 10.0)

# Resumo Final
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Salário Líquido", f"R$ {salario_liquido_real:.2f}")
    st.caption(f"INSS: R$ {valor_inss:.2f} | IRRF: R$ {valor_irrf:.2f}")

with col2:
    sobra_caixa = salario_liquido_real - total_despesas - aporte_mensal
    st.metric("Sobra no Caixa", f"R$ {sobra_caixa:.2f}")

with col3:
    st.metric("Total Investido", f"R$ {aporte_mensal:.2f}")

if sobra_caixa < 0:
    st.error("Atenção: Suas despesas e investimentos superam seu salário líquido!")

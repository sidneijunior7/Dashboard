import pandas as pd
import streamlit as st

# Função para carregar e processar o arquivo CSV
def load_csv(file):
    try:
        df = pd.read_csv(file, encoding='utf-16', sep='\t')
    except UnicodeDecodeError:
        st.error("Error: Unable to decode the file with 'utf-16' encoding. Please check the file encoding.")
        st.stop()

    # Renomear as colunas
    df.rename(columns={'<DATE>': 'DATE', '<BALANCE>': 'BALANCE', '<EQUITY>': 'EQUITY'}, inplace=True)
    
    # Converter a coluna 'DATE' para datetime
    try:
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d %H:%M')
    except ValueError:
        st.error("Error: Date format is incorrect. Please check the date format in the file.")
        st.stop()

    return df

# Função de cálculo de métricas
def calculate_metrics(df):
    df['DD_MAX'] = df['BALANCE'].cummax()
    dd_max = df['DD_MAX']-df['BALANCE']
    
    metrics = {
        "Deposito": df['BALANCE'][0],
        "Lucro Bruto": (df['BALANCE'].iloc[-1]) - (df['BALANCE'][0]),
        "Lucro Máximo": df['BALANCE'].max() - df['BALANCE'][0],
        "Drawdown Relativo": df['BALANCE'].min() - df['BALANCE'][0],
        "Average Balance": df['BALANCE'].mean(),
        "Total Equity": df['EQUITY'].sum(),
        "Max Equity": df['EQUITY'].max(),
        "Min Equity": df['EQUITY'].min(),
        "Average Equity": df['EQUITY'].mean(),
        "Drawdown Maximo" : dd_max.max(),
        "Drawdown Medio" : dd_max.mean()
    }
    return metrics

#=========================================
# HEADER DO DASHBOARD
#=========================================
st.title("Painel de Controle de Investimentos")
st.subheader("Visão Geral")
st.write("""
Este painel apresenta métricas e gráficos importantes para monitorar o desempenho dos seus investimentos.
Aqui você encontrará informações sobre o balanço da conta, drawdown, e outras métricas relevantes.
""")
# Carregar o arquivo CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    df = load_csv(uploaded_file)
    #st.write("Visualização dos dados:", df.head())
    
# Adicionar um seletor de data
    st.subheader("Filtrar por Data")
    start_date = st.date_input("Data de Início", df['DATE'].min().date())
    end_date = st.date_input("Data de Término", df['DATE'].max().date())

    if start_date <= end_date:
        filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
        valor_inicial = filtered_df['BALANCE'].iloc[0]
        st.line_chart(filtered_df.set_index('DATE')['BALANCE'] - (valor_inicial))
    else:
        st.error("Erro: A data de início deve ser menor ou igual à data de término.")

    # Calcular métricas
    metrics = calculate_metrics(df)

    # Exibir métricas
    st.subheader("Métricas Calculadas")
    #for key, value in metrics.items():
    #    st.write(f"{key}: {value}")

    col1, col2 = st.columns(2);
    with col1:
        st.metric(label="Lucro: ", value=metrics['Lucro Bruto'])
        st.metric(label="Lucro Max: ", value=metrics['Lucro Máximo'])
    with col2:
        st.metric(label="Maior prejuízo: ", value=metrics['Drawdown Relativo'])
        st.metric(label="Drawdown Máximo: ", value=metrics['Drawdown Maximo'])
        
    # Plotar gráficos
    #st.subheader("Gráficos")
    #st.line_chart(df.set_index('DATE')['BALANCE'] - (df['BALANCE'][0]))

    

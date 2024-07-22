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
    
    metrics = {
        "Deposito": df['BALANCE'][0],
        "Lucro Bruto": (df['BALANCE'].iloc[-1]) - (df['BALANCE'][0]),
        "Max Balance": df['BALANCE'].max(),
        "Min Balance": df['BALANCE'].min(),
        "Average Balance": df['BALANCE'].mean(),
        "Total Equity": df['EQUITY'].sum(),
        "Max Equity": df['EQUITY'].max(),
        "Min Equity": df['EQUITY'].min(),
        "Average Equity": df['EQUITY'].mean()
    }
    return metrics

# Configuração do Streamlit
st.title("Trading Dashboard")

# Carregar o arquivo CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.write("Visualização dos dados:", df.head())

    # Calcular métricas
    metrics = calculate_metrics(df)

    # Exibir métricas
    st.subheader("Métricas Calculadas")
    for key, value in metrics.items():
        st.write(f"{key}: {value}")

    # Plotar gráficos
    st.subheader("Gráficos")
    st.line_chart(df.set_index('DATE')['BALANCE'])
    st.line_chart(df.set_index('DATE')['EQUITY'])

    # Adicionar um seletor de data
    st.subheader("Filtrar por Data")
    start_date = st.date_input("Data de Início", df['DATE'].min().date())
    end_date = st.date_input("Data de Término", df['DATE'].max().date())

    if start_date <= end_date:
        filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
        st.write(f"Dados filtrados de {start_date} a {end_date}", filtered_df)
        st.line_chart(filtered_df.set_index('DATE')['BALANCE'])
        st.line_chart(filtered_df.set_index('DATE')['EQUITY'])
    else:
        st.error("Erro: A data de início deve ser menor ou igual à data de término.")

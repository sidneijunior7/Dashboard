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

    
def calculate_metrics(df, start_date, end_date):
    # Converter as datas para datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrar o DataFrame com base nas datas selecionadas
    filtered_df = df[(df['DATE'] >= start_date) & (df['DATE'] <= end_date)]
    
    # Calcular o máximo acumulado e drawdown
    filtered_df['DD_MAX'] = filtered_df['BALANCE'].cummax()
    dd_max = filtered_df['DD_MAX'] - filtered_df['BALANCE']
    
    # Calcular as métricas
    metrics = {
        "Deposito": filtered_df['BALANCE'].iloc[0],
        "Lucro Bruto": filtered_df['BALANCE'].iloc[-1] - filtered_df['BALANCE'].iloc[0],
        "Lucro Máximo": filtered_df['BALANCE'].max() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Relativo": filtered_df['BALANCE'].min() - filtered_df['BALANCE'].iloc[0],
        "Drawdown Maximo": round(dd_max.max(),2),
        "Drawdown Medio": round(dd_max.mean(),2)
    }
    return metrics

#=========================================
# HEADER DO DASHBOARD
#=========================================
st.set_page_config(
    page_title="BackTest Tools for Traders",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Adicionar a sidebar
st.sidebar.title("Menu Lateral")

# Adicionar itens à sidebar
st.sidebar.header("Navegação")
selected_option = st.sidebar.radio("Escolha uma opção", ["Página Inicial", "Sobre", "Contato"])

if selected_option == "Página Inicial":
    st.title("Página Inicial")
    st.write("Bem-vindo à página inicial! Adicione conteúdo aqui.")
elif selected_option == "Sobre":
    st.title("Sobre")
    st.write("Esta é a seção Sobre. Adicione informações sobre o aplicativo ou a empresa aqui.")
elif selected_option == "Contato":
    st.title("Contato")
    st.write("Esta é a seção de Contato. Adicione informações de contato ou um formulário aqui.")

st.subheader("BackTest Tools")
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
    col01, col02 = st.columns(2)
    with col01:
        start_date = st.date_input("Data de Início", df['DATE'].min().date())
    with col02:
        end_date = st.date_input("Data de Término", df['DATE'].max().date())
    
    if st.button("Todo Histórico"):
        start_date = df['DATE'].min()
        end_date = df['DATE'].max()
         
    if start_date <= end_date:
        filtered_df = df[(df['DATE'] >= pd.to_datetime(start_date)) & (df['DATE'] <= pd.to_datetime(end_date))]
        valor_inicial = filtered_df['BALANCE'].iloc[0]
        st.line_chart(filtered_df.set_index('DATE')['BALANCE'] - (valor_inicial))
    else:
        st.error("Erro: A data de início deve ser menor ou igual à data de término.")

    # Calcular métricas
    metrics = calculate_metrics(df, start_date, end_date)

    # Exibir métricas
    st.subheader("Dados Históricos")
    #for key, value in metrics.items():
    #    st.write(f"{key}: {value}")

    col1, col2 = st.columns(2);
    with col1:
        st.metric(label="Lucro: ", value=metrics['Lucro Bruto'])
        st.metric(label="Lucro Max: ", value=metrics['Lucro Máximo'])
    with col2:
        st.metric(label="Drawdown Médio: ", value=metrics['Drawdown Medio'])
        st.metric(label="Drawdown Máximo: ", value=metrics['Drawdown Maximo'])
        
    # Plotar gráficos
    #st.subheader("Gráficos")
    #st.line_chart(df.set_index('DATE')['BALANCE'] - (df['BALANCE'][0]))

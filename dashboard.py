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
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
        
        /* Identificar o tema claro ou escuro */
        .dark-theme .logo img{
            content: url("https://academiadosinvestidores.com.br/wp-content/uploads/2024/07/watermark-e1720301832642.png") !important;
        }
        .light-theme .logo img{
            content: url("https://academiadosinvestidores.com.br/wp-content/uploads/2024/07/logo_header-e1720357655763.webp") !important;
        }
        /* Estilo geral do logotipo */
        .logo {
            width: 100%;
            display: flex;
            justify-content: center;
            padding: 10px 0;
        }
        
    </style>
    """,
    unsafe_allow_html=True
)



# Código para detectar o tema e aplicar a classe apropriada
st.markdown(
    """
   <script>
    const isDarkTheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const body = document.body;
    if (isDarkTheme) {
        body.classList.add('dark-theme');
    } else {
        body.classList.add('light-theme');
    }
    </script>
    """,
    unsafe_allow_html=True
)
# Adicionar o logotipo no topo
st.markdown(
    """
    <div class="logo">
        <img alt="Logotipo"></img>
    </div>
    """,
    unsafe_allow_html=True
)
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
   

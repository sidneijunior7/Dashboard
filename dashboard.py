import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from sqlalchemy import create_engine

# Funções para cálculos
def calculate_metrics(df):
    df['Monthly Returns'] = df['Capital'].pct_change()
    cagr = (df['Capital'].iloc[-1] / df['Capital'].iloc[0]) ** (1 / (len(df) / 12)) - 1
    monthly_returns = df.resample('M', on='Date')['Capital'].last().pct_change()
    recovery_factor = (monthly_returns.sum() / abs(monthly_returns[monthly_returns < 0].sum()))
    profit_factor = (monthly_returns[monthly_returns > 0].sum() / abs(monthly_returns[monthly_returns < 0].sum()))
    positive_months = (monthly_returns > 0).sum()
    negative_months = (monthly_returns < 0).sum()
    max_drawdown = abs(df['Drawdown'].max())
    adjusted_return = monthly_returns.mean() * (2 / max_drawdown) if max_drawdown != 0 else np.nan

    return {
        'CAGR': cagr,
        'Monthly Recovery Factor': recovery_factor,
        'Monthly Profit Factor': profit_factor,
        'Positive Months': positive_months,
        'Negative Months': negative_months,
        'Adjusted Monthly Return': adjusted_return
    }

def plot_capital_curve(df):
    fig, ax = plt.subplots()
    ax.plot(df['Date'], df['Capital'])
    ax.set_title('Capital Curve')
    ax.set_xlabel('Date')
    ax.set_ylabel('Capital')
    st.pyplot(fig)

def plot_annual_capital_curves(df):
    df['Year'] = df['Date'].dt.year
    fig = px.line(df, x='Date', y='Capital', color='Year', title='Annual Capital Curves')
    st.plotly_chart(fig)

# Streamlit UI
st.title('Daytrade Backtest Dashboard')

# Função para carregar e processar o arquivo CSV
def load_csv(file):
    # Tentar ler o arquivo com a codificação 'utf-8'
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        # Se falhar, tentar com a codificação 'latin1'
        try:
            df = pd.read_csv(file, encoding='latin1')
        except UnicodeDecodeError:
            st.error("Error: Unable to decode the file. Please check the file encoding.")
            st.stop()

    # Renomear as colunas
    df.rename(columns={'<DATE>': 'DATE', '<BALANCE>': 'BALANCE', '<EQUITY>': 'EQUITY'}, inplace=True)
    
    # Converter a coluna 'DATE' para datetime
    try:
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y.%m.%d %H.%M')
    except ValueError:
        st.error("Error: Date format is incorrect. Please check the date format in the file.")
        st.stop()

    return df

# Carregar o arquivo CSV
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    df = load_csv(uploaded_file)
    st.write("Data preview:", df.head())

    # Calculate metrics
    metrics = calculate_metrics(df)

    # Display metrics
    st.write("Metrics:")
    st.write(f"CAGR: {metrics['CAGR']:.2%}")
    st.write(f"Monthly Recovery Factor: {metrics['Monthly Recovery Factor']:.2f}")
    st.write(f"Monthly Profit Factor: {metrics['Monthly Profit Factor']:.2f}")
    st.write(f"Positive Months: {metrics['Positive Months']}")
    st.write(f"Negative Months: {metrics['Negative Months']}")
    st.write(f"Adjusted Monthly Return: {metrics['Adjusted Monthly Return']:.2%}")

    # Plot capital curve
    st.subheader('Capital Curve')
    plot_capital_curve(df)

    # Plot annual capital curves
    st.subheader('Annual Capital Curves')
    plot_annual_capital_curves(df)

    # Save metrics to database
    engine = create_engine('sqlite:///backtest_metrics.db')
    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_sql('metrics', engine, if_exists='append', index=False)
    st.success("Metrics saved to database.")

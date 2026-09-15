import streamlit as st
import pandas as pd

# Load processed metrics CSV
data = pd.read_csv('data/processed/stock_metrics_with_recommendations.csv')

st.title("Smart Investment Dashboard")

# Stock selection
stock_list = data['Symbol'].unique()
selected_stock = st.selectbox("Select a stock", stock_list)

# Filter selected stock
stock_data = data[data['Symbol'] == selected_stock]

st.subheader(f"Metrics for {selected_stock}")
st.write(stock_data)

st.subheader("Predicted Price")
st.write(stock_data['Next_Day_Price'].values[0])

st.subheader("Recommendation")
st.write(stock_data['Recommendation'].values[0])

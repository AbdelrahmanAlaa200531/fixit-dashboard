import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Page Config
st.set_page_config(page_title="FixIt Services - Profitability Dashboard", layout="wide", page_icon="🛠️")

st.title("🛠️ FixIt Services - Service Profitability & Retention Dashboard")
st.markdown("Track client engagement, detect churn risk, and analyze high-ROI home repair channels.")

# Load Data
@st.cache_data
def load_data():
    file_path = "data.xlsx"
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df['Service Category'] = df['Service Category'].fillna("Uncategorized")
        df['Date'] = pd.to_datetime(df['Date'])
        df['Profit'] = df['Revenue'] - df['Ad Spend']
        df['ROI (%)'] = ((df['Revenue'] - df['Ad Spend']) / df['Ad Spend'].replace(0, 1)) * 100
        return df
    raise FileNotFoundError("لم يتم العثور على ملف data.xlsx داخل المستودع.")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data file: {e}")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔍 Filter Options")

min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
date_range = st.sidebar.date_input("Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

client_types = st.sidebar.multiselect("Client Type", options=df['Client Type'].unique(), default=df['Client Type'].unique())
time_of_day = st.sidebar.multiselect("Time of Day", options=df['Time'].unique(), default=df['Time'].unique())

top_n = st.sidebar.slider("Top N Categories", min_value=5, max_value=50, value=15, step=5)

# Filter Data
filtered_df = df[
    (df['Client Type'].isin(client_types)) &
    (df['Time'].isin(time_of_day))
]

if len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df['Date'] >= start_d) & (filtered_df['Date'] <= end_d)]

if filtered_df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# Key Metrics (KPIs)
st.subheader("📌 Key Performance Indicators")
col1, col2, col3, col4, col5, col6 = st.columns(6)

total_rev = filtered_df['Revenue'].sum()
total_spend = filtered_df['Ad Spend'].sum()
total_profit = filtered_df['Profit'].sum()
total_conv = filtered_df['Conversions'].sum()
avg_roi = filtered_df['ROI (%)'].mean()
aov = total_rev / total_conv if total_conv > 0 else 0

col1.metric("Total Revenue", f"${total_rev:,.2f}")
col2.metric("Total Ad Spend", f"${total_spend:,.2f}")
col3.metric("Net Profit", f"${total_profit:,.2f}")
col4.metric("Avg ROI", f"{avg_roi:.1f}%")
col5.metric("Conversions", f"{total_conv:,}")
col6.metric("Avg Order Value", f"${aov:,.2f}")

st.markdown("---

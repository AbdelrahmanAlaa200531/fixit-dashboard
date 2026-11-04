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
    # التجربة بالاسمين لتفادي أي اختلاف في المسافات أو الشرطات
    files_to_check = [
        "FixIt Services_Data.xlsx",
        "FixIt_Services_Data.xlsx"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df['Service Category'] = df['Service Category'].fillna("Uncategorized")
            df['Date'] = pd.to_datetime(df['Date'])
            df['Profit'] = df['Revenue'] - df['Ad Spend']
            df['ROI (%)'] = ((df['Revenue'] - df['Ad Spend']) / df['Ad Spend'].replace(0, 1)) * 100
            return df
            
    raise FileNotFoundError("لم يتم العثور على ملف الإكسيل ببيانات FixIt داخل المستودع.")

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

st.markdown("---")

# Dashboard Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Service Profitability & High-ROI", 
    "👥 Client Retention & Churn Risk", 
    "👷 Operations & Technicians", 
    "📋 Raw Data & Export"
])

# Tab 1: Service Profitability
with tab1:
    c1, c2 = st.columns(2)
    
    top_services = filtered_df.groupby('Service Category')['Revenue'].sum().nlargest(top_n).reset_index()
    fig_services = px.bar(
        top_services, x='Revenue', y='Service Category', orientation='h',
        title=f"Top {top_n} Service Categories by Revenue",
        color='Revenue', color_continuous_scale='Blues'
    )
    fig_services.update_layout(yaxis={'categoryorder':'total ascending'})
    c1.plotly_chart(fig_services, use_container_width=True)

    fig_scatter = px.scatter(
        filtered_df, x='Ad Spend', y='Revenue', color='Client Type',
        size='Conversions', hover_data=['Service Category', 'Technician'],
        title="Ad Spend vs Revenue (High-ROI Channels Identification)"
    )
    c2.plotly_chart(fig_scatter, use_container_width=True)

# Tab 2: Client Retention
with tab2:
    c1, c2 = st.columns(2)
    
    client_summary = filtered_df.groupby('Client Type').agg(
        Revenue=('Revenue', 'sum'),
        Conversions=('Conversions', 'sum'),
        Jobs=('Revenue', 'count')
    ).reset_index()

    fig_pie = px.pie(client_summary, values='Revenue', names='Client Type', title="Revenue Share by Client Type", hole=0.4)
    c1.plotly_chart(fig_pie, use_container_width=True)

    fig_conv = px.bar(client_summary, x='Client Type', y='Conversions', color='Client Type', title="Total Conversions by Client Type")
    c2.plotly_chart(fig_conv, use_container_width=True)

# Tab 3: Operations & Technicians
with tab3:
    c1, c2 = st.columns(2)
    
    tech_summary = filtered_df.groupby('Technician')['Revenue'].sum().nlargest(10).reset_index()
    fig_tech = px.bar(tech_summary, x='Technician', y='Revenue', title="Top 10 Technicians by Revenue", color='Revenue')
    c1.plotly_chart(fig_tech, use_container_width=True)

    time_summary = filtered_df.groupby('Time')['Revenue'].sum().reset_index()
    fig_time = px.bar(time_summary, x='Time', y='Revenue', title="Revenue by Time of Day", color='Time')
    c2.plotly_chart(fig_time, use_container_width=True)

# Tab 4: Raw Data & Download
with tab4:
    st.subheader("Filtered Dataset View")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name="fixit_services_filtered_data.csv",
        mime="text/csv"
    )

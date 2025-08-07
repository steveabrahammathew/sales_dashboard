import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Superstore Sales Dashboard")

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("Superstore.csv", encoding='ISO-8859-1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month_name()
    return df

df = load_data()


# Sidebar filters
st.sidebar.header("Filter Data")
country = st.sidebar.multiselect("Select Country", df['Country'].unique())
category = st.sidebar.multiselect("Select Category", df['Category'].unique())
year = st.sidebar.multiselect("Select Year", df['Year'].unique())

# Apply filters
filtered_df = df.copy()
if country:
    filtered_df = filtered_df[filtered_df['Country'].isin(country)]
if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]
if year:
    filtered_df = filtered_df[filtered_df['Year'].isin(year)]


total_sales = round(filtered_df['Sales'].sum(), 2)
total_profit = round(filtered_df['Profit'].sum(), 2)
num_orders = filtered_df['Order ID'].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales ($)", f"{total_sales:,}")
col2.metric("Total Profit ($)", f"{total_profit:,}")
col3.metric("Number of Orders", num_orders)


# Sales by Category
cat_chart = px.bar(
    filtered_df.groupby('Category')['Sales'].sum().reset_index(),
    x='Category', y='Sales', title='Sales by Category'
)
st.plotly_chart(cat_chart, use_container_width=True)

# Profit by Region
region_chart = px.pie(
    filtered_df.groupby('Region')['Profit'].sum().reset_index(),
    names='Region', values='Profit', title='Profit by Region'
)
st.plotly_chart(region_chart, use_container_width=True)

# Sales Over Time
time_chart = px.line(
    filtered_df.groupby('Order Date')['Sales'].sum().reset_index(),
    x='Order Date', y='Sales', title='Sales Over Time'
)
st.plotly_chart(time_chart, use_container_width=True)

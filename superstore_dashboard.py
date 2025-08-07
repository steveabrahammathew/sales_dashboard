import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(layout="wide")
st.title("📈 Sales Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(df.head())

    # Identify date-like columns from object dtype columns
    possible_dates = []
    for col in df.select_dtypes(include=['object']).columns:
        try:
            converted = pd.to_datetime(df[col], errors='coerce')
            if converted.notna().sum() > 0:
                possible_dates.append(col)
        except:
            pass

    date_column = None
    if possible_dates:
        date_column = st.selectbox("Select Date Column (optional)", possible_dates)

    # Filters based on categorical columns
    st.sidebar.header("🔎 Filter Data")
    for col in df.select_dtypes(include=['object', 'category']).columns:
        unique_vals = df[col].dropna().unique()
        selected_vals = st.sidebar.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
        df = df[df[col].isin(selected_vals)]

    # Convert date column if selected
    if date_column:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
        df = df.dropna(subset=[date_column])
        df['Month'] = df[date_column].dt.to_period("M").astype(str)

    # Identify numeric columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if len(numeric_cols) >= 1:
        x_axis = st.selectbox("X-axis (Categorical)", df.select_dtypes(include=['object', 'category']).columns)
        y_axis = st.selectbox("Y-axis (Numeric)", numeric_cols)

        # Grouped bar chart
        st.subheader("📊 Bar Chart")
        bar_data = df.groupby(x_axis)[y_axis].sum().reset_index()
        bar_fig = px.bar(bar_data, x=x_axis, y=y_axis)
        st.plotly_chart(bar_fig, use_container_width=True)

        # Pie chart
        st.subheader("🥧 Pie Chart")
        pie_fig = px.pie(bar_data, names=x_axis, values=y_axis)
        st.plotly_chart(pie_fig, use_container_width=True)

        # Line chart over time
        if date_column:
            st.subheader("📈 Time Series Chart")
            time_data = df.groupby(date_column)[y_axis].sum().reset_index()
            time_fig = px.line(time_data, x=date_column, y=y_axis)
            st.plotly_chart(time_fig, use_container_width=True)
    else:
        st.warning("No numeric columns found in the dataset to plot charts.")

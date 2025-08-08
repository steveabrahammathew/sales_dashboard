import streamlit as st
import pandas as pd
import plotly.express as px
import chardet

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Dynamic Sales Dashboard",
    page_icon="💡",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
<style>
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    .st-emotion-cache-1y4p8pa {
        padding-top: 2rem;
    }
    .stMetric {
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)


# --- HELPER FUNCTIONS ---
@st.cache_data
def load_data(uploaded_file):
    """Detects encoding and loads CSV data, converting dates."""
    # Detect encoding
    raw_data = uploaded_file.getvalue()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    
    # Read CSV with detected encoding
    df = pd.read_csv(uploaded_file, encoding=encoding)
    
    # Attempt to convert object columns to datetime
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            pass # Ignore columns that can't be converted
    return df

def format_number(num):
    """Formats a number to be more readable (e.g., 1K, 1M)."""
    if pd.isna(num):
        return "$0"
    if num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num / 1_000:.2f}K"
    return f"${num:,.2f}"

# --- MAIN DASHBOARD LOGIC ---
st.title("💡 Sales Dashboard")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Upload & Configure")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    
    if uploaded_file:
        st.header("🎨 Theme Options")
        chart_theme = st.selectbox("Select Chart Theme", ["plotly_dark", "ggplot2", "seaborn", "simple_white"])

if not uploaded_file:
    st.info("Please upload a CSV file to begin analysis.")
    st.stop()

# --- DATA LOADING AND PREPARATION ---
try:
    df_original = load_data(uploaded_file)
    df = df_original.copy()
except Exception as e:
    st.error(f"Error reading or processing the file: {e}")
    st.stop()

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🔎 Filter Data")
    
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    if not numeric_cols:
        st.warning("No numeric data found in the file. Please upload a valid sales CSV.")
        st.stop()

    if date_cols:
        date_col = st.selectbox("Select Date Column", date_cols)
        min_date, max_date = df[date_col].min(), df[date_col].max()
        start_date, end_date = st.date_input(
            "Select Date Range",
            [min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
    else:
        date_col = None

    for col in categorical_cols:
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) > 1:
            selected_vals = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
            df = df[df[col].isin(selected_vals)]

# --- MAIN PANEL ---
if df.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

st.subheader("Dashboard Overview")

# --- KPI METRICS ---
main_metric = st.selectbox("Select Main Metric for KPIs", numeric_cols)
total_metric = df[main_metric].sum()
average_metric = df[main_metric].mean()
record_count = len(df)

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label=f"Total {main_metric}", value=format_number(total_metric))
kpi2.metric(label=f"Average {main_metric}", value=format_number(average_metric))
kpi3.metric(label="Total Records", value=f"{record_count:,}")

# --- CHARTS ---
st.subheader("Visualizations")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("##### Performance by Category")
    if categorical_cols:
        x_axis_bar = st.selectbox("Select Category", categorical_cols, key="bar")
        bar_data = df.groupby(x_axis_bar)[main_metric].sum().reset_index().sort_values(by=main_metric, ascending=False)
        bar_fig = px.bar(bar_data, x=x_axis_bar, y=main_metric, template=chart_theme)
        st.plotly_chart(bar_fig, use_container_width=True)
    else:
        st.info("No categorical columns available for bar chart.")

with chart_col2:
    st.markdown("##### Metric Distribution")
    if categorical_cols:
        x_axis_pie = st.selectbox("Select Category", categorical_cols, key="pie")
        pie_data = df.groupby(x_axis_pie)[main_metric].sum().reset_index()
        pie_fig = px.pie(pie_data, names=x_axis_pie, values=main_metric, template=chart_theme, hole=0.4)
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("No categorical columns available for pie chart.")

if date_col:
    st.markdown("##### Metric Over Time")
    time_data = df.set_index(date_col).resample('M')[main_metric].sum().reset_index()
    time_fig = px.line(time_data, x=date_col, y=main_metric, template=chart_theme, markers=True)
    st.plotly_chart(time_fig, use_container_width=True)

with st.expander("📄 View Filtered Data"):
    st.dataframe(df)

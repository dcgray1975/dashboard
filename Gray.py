import streamlit as st
import pandas as pd
import os
import plotly.express as px
import matplotlib as mpl
import warnings

warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Page setup
st.set_page_config(page_title="COVID-19 Dashboard for Liberia", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: COVID-19 Dashboard for Liberia")
st.markdown("**Prepared by David C. Gray, PhD**")
st.markdown("---")

# File uploader
f1 = st.file_uploader(":file_folder: Upload Excel file", type=(["csv", "xlsx", "xls"]))

if f1 is not None:
    filename = f1.name
    st.write(filename)
    df = pd.read_csv(f1, encoding = "ISO-8859-1")
else:
    os.chdir(r"C:\Users\Admin\Desktop\LoanDashboard")
    df = pd.read_csv("Extracted_COVID-19_Data1.csv", encoding = "ISO-8859-1")
    
col1, col2, = st.columns(2)
df["Year"] = pd.to_datetime(df["Year"], format="%Y").dt.year  # Use %Y for 4-digit year
df["Month"] = pd.to_datetime(df["Month"], format="%B").dt.month  # Use %B if month names, or %m if numbers

with col1:
    year1 = st.selectbox("Select Year", df["Year"].unique(), index=0)

with col2:
    month1 = st.selectbox("Select Month", df["Month"].unique(), index=0)

# Create sidebar headers
# Normalize columns
df.columns = df.columns.str.strip().str.lower().str.replace(r'[^a-z0-9 ]', '', regex=True)
# Debug print
st.write("Normalized columns:", df.columns.tolist())

st.sidebar.header("Choose your filter: ")
County = st.sidebar.multiselect(
    "Select County",
    options=df["county"].unique()
)

if not County:
    df2 = df.copy()
else:
    df2 = df[df["county"].isin(County)]

# Group data by county and sum total covid cases
category_df = df2.groupby("county", as_index=False)["total covid cases"].sum()

with col1:
    st.subheader("Total COVID-19 Cases by County")
    fig = px.bar(category_df, x="county", y="total covid cases")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Total COVID-19 Cases by Month")
    fig = px.pie(df2, values="total covid cases", names="month", hole=0.5)
    fig.update_traces(textinfo='percent+label', textposition="outside")
    fig.update_layout(title_text="Total COVID-19 Cases by Month")
    st.plotly_chart(fig, use_container_width=True)

    # create downloan button
df.columns = df.columns.str.strip().str.lower()

# Example filtered_df (replace with actual filtering logic if needed)
filtered_df = df.copy()

# Prepare category_df (you can adjust grouping as needed)
# Example: group by some 'category' column if it exists
if 'category' in df.columns:
    category_df = filtered_df.groupby(by="category", as_index=False)["total covid cases"].sum()
else:
    st.warning("No 'category' column found. Using entire dataframe instead.")
    category_df = filtered_df.copy()

# Prepare df2: group by county
if 'county' in df.columns:
    df2 = filtered_df.groupby(by="county", as_index=False)["total covid cases"].sum()
else:
    st.error("No 'county' column found in dataframe.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    with st.expander("Category Summary"):
        st.write(category_df.style.background_gradient(axis=None, cmap="Blues"))
        
        csv = category_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download Category Data",
            data=csv,
            file_name="category_df.csv",
            mime="text/csv",
            help="Click here to download the category summary as a CSV file"
        )

with col2:
    with st.expander("County Summary"):
        st.write(df2.style.background_gradient(axis=None, cmap="Oranges"))
        
        csv2 = df2.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="Download County Data",
            data=csv2,
            file_name="county_df.csv",
            mime="text/csv",
            help="Click here to download the county summary as a CSV file"
        )

# Create time series plot
required_cols = ['county', 'month', 'year', 'total covid cases']
missing_cols = [col for col in required_cols if col not in df.columns]

df['date'] = pd.to_datetime(df["year"].astype(str) + '-' + df["month"].astype(str), errors='coerce')

df = df.dropna(subset=['date'])

time_series_df = df.groupby(['county', 'date'], as_index=False)['total covid cases'].sum()

fig = px.line(
    time_series_df,
    x='date',
    y='total covid cases',
    color='county',
    title='COVID-19 Cases Over Time by County',
    markers=True
)

fig.update_layout(
    xaxis_title='Month',
    yaxis_title='Total COVID-19 Cases',
    legend_title='County'
)

st.plotly_chart(fig, use_container_width=True)

# Performed Statistics
# Define target columns
target_cols = [
    "total covid cases", "total deaths", "covid tests conducted",
    "partial lockdown", "curfew", "full lockdown",
    "closing of border", "closing of airspace"
]

# Sidebar Header
st.sidebar.header(" County Statistics Summary for COVID-19")

# (Optional) filter by county if column exists
if 'county' in df.columns:
    counties = df['county'].unique().tolist()
    selected_counties = st.sidebar.multiselect("Select Counties", counties, default=counties)
    filtered_df = df[df['county'].isin(selected_counties)]
else:
    st.sidebar.warning("'county' column not found. No filtering applied.")
    filtered_df = df.copy()

# Check required columns
missing_cols = [col for col in target_cols if col not in filtered_df.columns]
if missing_cols:
    st.error(f"Missing columns in data: {missing_cols}")
    st.stop()

# Compute statistics
sum_values = filtered_df[target_cols].sum().to_frame(name='Sum')
mean_values = filtered_df[target_cols].mean().to_frame(name='Mean')
median_values = filtered_df[target_cols].median().to_frame(name='Median')
min_values = filtered_df[target_cols].min().to_frame(name='Min')
max_values = filtered_df[target_cols].max().to_frame(name='Max')

# Main page headers and stats
st.subheader("Total (Sum) of COVID-19 Metrics")
st.write(sum_values.T.style.background_gradient(cmap='Blues', axis=None))

st.subheader("Mean of COVID-19 Metrics")
st.write(mean_values.T.style.background_gradient(cmap='Greens', axis=None))

st.subheader("Median of COVID-19 Metrics")
st.write(median_values.T.style.background_gradient(cmap='Purples', axis=None))

st.subheader("Minimum of COVID-19 Metrics")
st.write(min_values.T.style.background_gradient(cmap='Oranges', axis=None))

st.subheader("Maximum of COVID-19 Metrics")
st.write(max_values.T.style.background_gradient(cmap='Reds', axis=None))

# Create Time series plot for total unmber of dealth by county


required_cols = ['county', 'month', 'year', 'total deaths']
missing_cols = [col for col in required_cols if col not in df.columns]

df['date'] = pd.to_datetime(df["year"].astype(str) + '-' + df["month"].astype(str), errors='coerce')

df = df.dropna(subset=['date'])

time_series_df = df.groupby(['county', 'date'], as_index=False)['total deaths'].sum()

fig = px.line(
    time_series_df,
    x='date',
    y='total deaths',
    color='county',
    title='Total Number of COVID-19 Deaths Over Time by County',
    markers=True
)

fig.update_layout(
    xaxis_title='Month',
    yaxis_title='total deaths',
    legend_title='County'
)

st.plotly_chart(fig, use_container_width=True)

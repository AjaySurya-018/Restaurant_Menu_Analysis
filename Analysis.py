import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# Database connection and initialization
def init_db():
    conn = sqlite3.connect("restaurant_menu.db")  # SQLite database file
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS menu_data (
        RestaurantID TEXT,
        MenuCategory TEXT,
        MenuItem TEXT,
        Ingredients TEXT,
        Price REAL,
        Profitability TEXT
    )
    """)
    conn.commit()

    # Check if data is already present
    cursor.execute("SELECT COUNT(*) FROM menu_data")
    if cursor.fetchone()[0] == 0:
        # Load data from Excel and insert it into SQLite
        excel_data = pd.read_excel("data/maindata.xlsx")  # Update the path as needed
        excel_data.to_sql("menu_data", conn, if_exists="append", index=False)
    conn.close()

# Fetch data from database
@st.cache_data
def fetch_data():
    conn = sqlite3.connect("restaurant_menu.db")
    df = pd.read_sql_query("SELECT * FROM menu_data", conn)
    conn.close()
    return df

# Preprocessing data
def preprocess_data(df):
    df = df.drop_duplicates()
    df = df.dropna()
    return df

# Function for pie plot
def pie_plot(df, col):
    palette_color = sns.color_palette('Set2')
    fig, ax = plt.subplots(figsize=(6, 6))
    df[col].value_counts().plot.pie(autopct='%1.0f%%', colors=palette_color, ax=ax)
    ax.set_title(f'Pie Plot of {col}')
    return fig

# Function for bar plot
def bar_plot(df, x, hue=None, horizontal=False, title=""):
    plt.figure(figsize=(12, 6))
    if horizontal:
        sns.countplot(data=df, y=x, hue=hue, palette='Set2', order=df[x].value_counts().index)
    else:
        sns.countplot(data=df, x=x, hue=hue, palette='Set2', order=df[x].value_counts().index)
    plt.title(title)
    st.pyplot(plt)

# Initialize database
init_db()

# Streamlit UI
# Streamlit app with working dropdown
st.title("Restaurant Menu Optimization Analysis")

# Step 1: Load and Preprocess Data
st.write("### Step 1: Dataset Description")
data = fetch_data()
st.write("#### Raw Data (First 10 Rows):")
st.dataframe(data.head(10))

st.write("#### Dataset Attributes")
st.write("""
- *RestaurantID:* Identifier of the restaurant.
- *MenuCategory:* Category of the menu item (Appetizers, Main Course, Desserts, Beverages).
- *MenuItem:* Name of the menu item.
- *Ingredients:* List of ingredients used in the menu item.
- *Price:* Price of the menu item in dollars.
- *Profitability:* Target variable indicating menu item profitability (High/Medium/Low).
""")

# Preprocess Data
data = preprocess_data(data)
st.write("#### Cleaned Data Summary:")
st.write(data.describe())

# Step 2: Statistical Analysis
st.write("### Step 2: Statistical Analysis")

# Analysis Dropdown with a unique key
analysis_options = [
    "Pie Plot of Restaurants", "Pie Plot of Menu Category",
    "Pie Plot of Profitability", "Bar Plot of Menu Category",
    "Bar Plot of Menu Items", "Menu Category with Restaurant ID",
    "Relation between Price and Profitability", "Price Distribution",
    "Price Range of Menu Categories"
]
selected_analysis = st.selectbox(
    "Choose Analysis", 
    analysis_options, 
    key="analysis_dropdown_key"  # Unique key
)

# Analysis Logic Based on Selection
if selected_analysis == "Pie Plot of Restaurants":
    st.write("### Pie Plot of Restaurant Analysis")
    st.pyplot(pie_plot(data, 'RestaurantID'))

elif selected_analysis == "Pie Plot of Menu Category":
    st.write("### Pie Plot of Menu Category")
    st.pyplot(pie_plot(data, 'MenuCategory'))

elif selected_analysis == "Pie Plot of Profitability":
    st.write("### Pie Plot of Profitability")
    st.pyplot(pie_plot(data, 'Profitability'))

elif selected_analysis == "Bar Plot of Menu Category":
    st.write("### Bar Plot of Menu Category")
    plt.figure(figsize=(10, 5))
    sns.countplot(data=data, x='MenuCategory', order=data['MenuCategory'].value_counts().index)
    plt.title('Bar Plot of Menu Category')
    st.pyplot(plt)

elif selected_analysis == "Bar Plot of Menu Items":
    st.write("### Bar Plot of Menu Items")
    plt.figure(figsize=(14, 7))
    sns.countplot(data=data, y='MenuItem', order=data['MenuItem'].value_counts().index)
    plt.title('Bar Plot of Menu Items')
    st.pyplot(plt)

elif selected_analysis == "Menu Category with Restaurant ID":
    st.write("### Menu Category with Restaurant ID")
    plt.figure(figsize=(15, 6))
    sns.countplot(x='MenuCategory', order=data['MenuCategory'].value_counts().index, data=data, hue='RestaurantID', palette='Dark2')
    plt.title('Distribution of Menu Category with Restaurant ID')
    st.pyplot(plt)

elif selected_analysis == "Relation between Price and Profitability":
    st.write("### Relation between Price and Profitability")
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=data, x='MenuCategory', y='Price', hue='Profitability', palette='coolwarm')
    plt.title('Relation between Item Price & Profitability')
    st.pyplot(plt)

elif selected_analysis == "Price Distribution":
    st.write("### Price Distribution of Menu Items")
    plt.figure(figsize=(10, 6))
    sns.histplot(data=data, x='Price', kde=True, color='purple')
    plt.title('Price Distribution of Menu Items')
    st.pyplot(plt)

elif selected_analysis == "Price Range of Menu Categories":
    st.write("### Price Range of Menu Categories")
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=data, x='MenuCategory', y='Price', palette='viridis')
    plt.title('Price Ranges of Menu Categories')
    st.pyplot(plt)

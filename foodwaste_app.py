#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

DB_PATH = "foodwaste.db"

# ------------------------
# Helper functions
# ------------------------
def get_connection():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA foreign_keys = ON;")
    return con

def run_query(query, params=None):
    con = get_connection()
    df = pd.read_sql_query(query, con, params=params or {})
    con.close()
    return df

def run_execute(query, params=None):
    con = get_connection()
    cur = con.cursor()
    cur.execute(query, params or [])
    con.commit()
    con.close()

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="Food Waste Management", layout="wide")
st.title("🍲 Local Food Wastage Management System")

menu = ["Home", "EDA", "Listings", "Claims", "Add Data", "Predictions"]
choice = st.sidebar.selectbox("Navigation", menu)

# ------------------------
# Home
# ------------------------
if choice == "Home":
    st.subheader("Welcome 👋")
    st.write("This is an interactive dashboard to manage **food providers, receivers, listings, and claims**.")
    st.info("Use the sidebar to navigate.")

# ------------------------
# EDA
# ------------------------
elif choice == "EDA":
    st.subheader("📊 Exploratory Data Analysis")

    # Providers by City
    df = run_query("SELECT City, COUNT(*) AS cnt FROM providers GROUP BY City ORDER BY cnt DESC LIMIT 10")
    st.bar_chart(df.set_index("City")["cnt"])

    # Claims by Status
    df2 = run_query("SELECT Status, COUNT(*) AS cnt FROM claims GROUP BY Status")
    fig, ax = plt.subplots()
    df2.plot(kind="pie", y="cnt", labels=df2["Status"], autopct='%1.1f%%', ax=ax)
    st.pyplot(fig)

    # Food Types
    df3 = run_query("SELECT Food_Type, COUNT(*) AS cnt FROM food_listings GROUP BY Food_Type")
    st.bar_chart(df3.set_index("Food_Type")["cnt"])

# ------------------------
# Listings
# ------------------------
elif choice == "Listings":
    st.subheader("📦 Food Listings")
    data = run_query("SELECT * FROM food_listings LIMIT 50")
    st.dataframe(data)

# ------------------------
# Claims
# ------------------------
elif choice == "Claims":
    st.subheader("📑 Claims Data")
    data = run_query("""
        SELECT c.Claim_ID, f.Food_Name, r.Name AS Receiver, c.Status, c.Timestamp
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
        ORDER BY c.Claim_ID DESC LIMIT 50
    """)
    st.dataframe(data)

# ------------------------
# Add Data
# ------------------------
elif choice == "Add Data":
    st.subheader("➕ Add New Food Listing")

    with st.form("add_form"):
        food_name = st.text_input("Food Name")
        qty = st.number_input("Quantity", min_value=1, step=1)
        expiry = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1, step=1)
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        location = st.text_input("Location")

        submitted = st.form_submit_button("Add Listing")
        if submitted:
            run_execute("""
                INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (food_name, qty, expiry, provider_id, "Supermarket", location, food_type, meal_type))
            st.success("✅ New listing added!")

# ------------------------
# Predictions (Optional ML Integration)
# ------------------------
elif choice == "Predictions":
    st.subheader("🔮 Predictions Module")
    st.info("This is a placeholder for ML predictions (e.g., predict claim success, food demand).")
    st.write("➡️ Later, you can train a model in Jupyter, save it as `.pkl`, and load it here.")


# In[ ]:





import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime
from google.oauth2.service_account import Credentials

# --- CONFIG ---
st.set_page_config(page_title="My Wallet", page_icon="💸")

CATEGORIES = ["Food 🍔", "Transport 🚗", "School 📚", "Bills 💡", "Shopping 🛍️", "Leisure 🍿", "Other 🤷"]

# --- CONNECT TO GOOGLE SHEETS ---
def get_google_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Make sure this matches your secrets file exactly!
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open("Daily Expenses")

try:
    sheet = get_google_sheet()
    
    # 1. SETUP EXPENSES TAB
    try: 
        ws = sheet.worksheet("Expenses")
    except: 
        ws = sheet.add_worksheet(title="Expenses", rows=1000, cols=4)
        ws.append_row(["Date", "Category", "Item", "Amount"])
        
    # 2. SETUP SAVINGS TAB (This is the part you were missing!)
    try: 
        ws_savings = sheet.worksheet("Savings")
    except:
        ws_savings = sheet.add_worksheet(title="Savings", rows=1000, cols=3)
        ws_savings.append_row(["Date", "Memo", "Amount"])
        
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- SIDEBAR MENU ---
st.sidebar.title("My Wallet")
# The names here match the 'if' statements below exactly
page = st.sidebar.radio("Go to", ["Log Expenses", "Add Savings", "Dashboard"])

# --- PAGE 1: LOG EXPENSES ---
if page == "Log Expenses":
    st.header("💸 Log Expense")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: date = st.date_input("Date")
        with col2: cat = st.selectbox("Category", CATEGORIES)
        item = st.text_input("Description")
        amount = st.number_input("Amount (P)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Save Expense"):
            if amount > 0:
                ws.append_row([str(date), cat, item, amount])
                st.toast(f"✅ Spent P{amount} on {item}")

# --- PAGE 2: ADD SAVINGS ---
elif page == "Add Savings":
    st.header("💰 Piggy Bank")
    st.info("Pay yourself first! 🐷")
    
    with st.form("savings_form", clear_on_submit=True):
        date = st.date_input("Date")
        memo = st.text_input("Memo (e.g., Weekly Goal)")
        amount = st.number_input("Amount (P)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Deposit Savings"):
            if amount > 0:
                ws_savings.append_row([str(date), memo, amount])
                st.balloons()
                st.toast(f"✅ Saved P{amount}!")

# --- PAGE 3: DASHBOARD ---
elif page == "Dashboard":
    st.header("📊 Financial Snapshot")
    
    if st.button("Refresh Data"):
        st.cache_data.clear()

    # FETCH DATA
    df_exp = pd.DataFrame(ws.get_all_records())
    df_sav = pd.DataFrame(ws_savings.get_all_records())

   # CALCULATIONS
    total_spent = 0  # <--- This is the safety line!
    if not df_exp.empty:
        df_exp["Amount"] = pd.to_numeric(df_exp["Amount"], errors='coerce').fillna(0.0)
        total_spent = df_exp["Amount"].sum()
        
    total_saved = 0  # <--- This is the safety line!
    if not df_sav.empty:
        df_sav["Amount"] = pd.to_numeric(df_sav["Amount"], errors='coerce').fillna(0.0)
        total_saved = df_sav["Amount"].sum()
    # CHARTS
    if not df_exp.empty:
        st.subheader("Where is my money going?")
        fig = px.pie(df_exp, values='Amount', names='Category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    if not df_sav.empty:
        st.subheader("Recent Savings")
        st.dataframe(df_sav.tail(5).iloc[::-1], hide_index=True, use_container_width=True)

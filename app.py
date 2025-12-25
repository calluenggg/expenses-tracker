import streamlit as st
import gspread
import pandas as pd
import plotly.express as px
from datetime import datetime
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="My Wallet")

CATEGORIES = ["FOOD", "TRANSPORTATION", "SHOPPING", "BILLS", "GYM", "DATES", "MISCELLANEOUS"]

def get_google_sheet():
  scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
  creds_dict = st.secrets["gcp_service_accounts"]
  creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
  client = gspread.authorize(creds)
  return client.open("Daily Expenses")

try:
  sheet = get_google_sheet()
  
  try: ws = sheet.worksheet("Expenses")
  except:
    ws = sheet.add_worksheet(title="Expenses", rows = 1000, cols = 4)
    ws.append_row(["Date", "Category", "Item", "Ampount"])

  try: ws = sheet.worksheet("Savings")
  except:
    ws = sheet.add_worksheet(title="Savings", rows = 1000, cols = 3)
    ws.append_row(["Date", "Memo", "Amount"])

except Exception as e:
  st.error(f"Connection Error: {e}")

st.sidebar.title("My Wallet")
page = st.side.radio("Go to", ["Log Expenses", "Add Savings", "Dashboard"])

if page == "Log Expense":
    st.header("Log Expense")
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1: date = st.date_input("Date")
        with col2: cat = st.selectbox("Category", CATEGORIES)
        item = st.text_input("Description")
        amount = st.number_input("Amount (Pesos)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Save Expense"):
            if amount > 0:
                ws.append_row([str(date), cat, item, amount])
                st.toast(f"✅ Spent {amount} Pesos on {item}")

elif page == "Add Savings":
    st.header("Piggy Bank")
    st.info("Pay yourself first!")
    
    with st.form("savings_form", clear_on_submit=True):
        date = st.date_input("Date")
        memo = st.text_input("Memo (e.g., Weekly Goal, Bday Gift)")
        amount = st.number_input("Amount to Save (P)", min_value=0.0, step=50.0)
        
        if st.form_submit_button("Deposit Savings"):
            if amount > 0:
                ws_savings.append_row([str(date), memo, amount])
                st.balloons()  # Fun animation!
                st.toast(f"✅ Saved P{amount}!")

elif page == "📊 Dashboard":
    st.header("📊 Financial Snapshot")
    
    # Refresh Button
    if st.button("Refresh Data"):
        st.cache_data.clear()

    # FETCH DATA
    df_exp = pd.DataFrame(ws.get_all_records())
    df_sav = pd.DataFrame(ws_savings.get_all_records())

    # CALCULATIONS
    total_spent = 0
    if not df_exp.empty:
        df_exp["Amount"] = pd.to_numeric(df_exp["Amount"])
        total_spent = df_exp["Amount"].sum()
        
    total_saved = 0
    if not df_sav.empty:
        df_sav["Amount"] = pd.to_numeric(df_sav["Amount"])
        total_saved = df_sav["Amount"].sum()

    # SHOW SCORECARD
    col1, col2 = st.columns(2)
    col1.metric("💸 Total Spent", f"P{total_spent:,.2f}")
    col2.metric("💰 Total Saved", f"P{total_saved:,.2f}", delta="Keep it up!")
    
    st.divider()

    # SHOW CHARTS
    if not df_exp.empty:
        st.subheader("Spending Breakdown")
        fig = px.pie(df_exp, values='Amount', names='Category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    
    if not df_sav.empty:
        st.subheader("Recent Savings")
        st.dataframe(df_sav.tail(5).iloc[::-1], hide_index=True, use_container_width=True)

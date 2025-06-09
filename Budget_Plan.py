import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Budget Dashboard", layout="wide")

st.title("📊 Interactive Budget Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        budget_df = pd.read_excel(uploaded_file, sheet_name="🎯Budget Plan - 1st Year", engine='openpyxl')
        bep_df = pd.read_excel(uploaded_file, sheet_name="Break-Even Point", engine='openpyxl')

        st.subheader("Budget Overview")
        budget_summary = budget_df.groupby("Quarter")["Budget"].sum().reset_index()
        fig_budget = px.bar(budget_summary, x="Quarter", y="Budget", color="Quarter", text_auto=True)
        st.plotly_chart(fig_budget, use_container_width=True)



        st.subheader("📘 Budget by Sector")
        chart_type = st.radio("Choose chart type:", ["Pie Chart", "Bar Chart"], horizontal=True)
        sector_summary = budget_df.groupby("Main Task")["Budget"].sum().reset_index()
        if chart_type == "Pie Chart":
            fig_sector = px.pie(sector_summary, names="Main Task", values="Budget", title="Budget Allocation by Main Task")
        else:
            fig_sector = px.bar(sector_summary, x="Main Task", y="Budget", color="Main Task", title="Budget by Main Task")
            
        st.plotly_chart(fig_sector, use_container_width=True)

        

        st.subheader("📈 Profit Trend")
        profit_summary = bep_df[["Quarter", "Profit"]]
        fig_profit = px.line(profit_summary, x="Quarter", y="Profit", markers=True)
        st.plotly_chart(fig_profit, use_container_width=True)

        

        st.subheader("⚖️ ROI Analysis")
        total_revenue = (bep_df["Units Sold"] * bep_df["Unit Cost"]).sum()
        total_cost = bep_df["Total Cost"].sum()
        total_profit = bep_df["Profit"].sum()
        roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", f"€{total_revenue:,.2f}")
        col2.metric("Total Cost", f"€{total_cost:,.2f}")
        col3.metric("Total Profit", f"€{total_profit:,.2f}")
        col4.metric("ROI", f"{roi*100:.2f}%")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("Upload a valid Excel file to get started.")








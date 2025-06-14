import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Budget Dashboard", layout="wide")

st.title("📊 Interactive Budget Dashboard")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    try:
        # --- Year Selector ---
        st.subheader("📅 Select Budget Year")
        selected_year = st.radio("Choose a year:", [2025, 2026], horizontal=True)

        # Map year to corresponding sheet name
        budget_sheet_map = {
            2025: "🎯Budget Plan - 1st Year",
            2026: "🎯Budget Plan - 2nd Year"
        }

        selected_budget_sheet = budget_sheet_map[selected_year]

        # Load dynamic budget sheet based on selected year
        budget_df = pd.read_excel(uploaded_file, sheet_name=selected_budget_sheet, engine='openpyxl')

        # Load break-even point once (assumed to be year-agnostic or first-year)
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

        # --- Budget Summary from Excel Sheet ---
        st.subheader("📘 Detailed Budget Summary")

        try:
            # Load the summary sheet
            summary_df = pd.read_excel(uploaded_file, sheet_name="Detailed Budget Summary", engine='openpyxl')

            # 🧮 Checkbox Filters
            st.markdown("### 🧮 Filter Options")

            all_quarters = sorted(summary_df["Quarter"].dropna().unique())
            select_all_quarters = st.checkbox("Select All Quarters", value=True, key="q_all")
            selected_quarters = all_quarters if select_all_quarters else [
                q for q in all_quarters if st.checkbox(q, key=f"q_{q}")
            ]

            all_tasks = sorted(summary_df["Main Task"].dropna().unique())
            select_all_tasks = st.checkbox("Select All Tasks", value=True, key="t_all")
            selected_tasks = all_tasks if select_all_tasks else [
                t for t in all_tasks if st.checkbox(t, key=f"t_{t}")
            ]

            # Apply filters
            filtered_df = summary_df[
                summary_df["Quarter"].isin(selected_quarters) &
                summary_df["Main Task"].isin(selected_tasks)
            ]

            # 🧾 Show filtered table
            st.dataframe(filtered_df.style.format({
                "Estimated Budget (€)": "€{:,.2f}",
                "Paid Amount (€)": "€{:,.2f}",
                "Old Estimated Budget (€)": "€{:,.2f}"
            }))

            # 📊 Budget Comparison Bar Chart
            st.subheader("📊 Budget Comparison by Quarter & Main Task")

            melted = filtered_df.melt(
                id_vars=["Quarter", "Main Task"],
                value_vars=["Estimated Budget (€)", "Paid Amount (€)", "Old Estimated Budget (€)"],
                var_name="Budget Type",
                value_name="Amount (€)"
            )

            fig_summary = px.bar(
                melted,
                x="Main Task",
                y="Amount (€)",
                color="Budget Type",
                barmode="group",
                facet_col="Quarter",
                title="Estimated vs Paid vs Old Budget",
                color_discrete_map={
                    "Estimated Budget (€)": "#1f77b4",
                    "Paid Amount (€)": "#2ca02c",
                    "Old Estimated Budget (€)": "#d62728"
                },
                height=600
            )
            fig_summary.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_summary, use_container_width=True)

            # 📌 Summary Metrics
            st.subheader("📌 Total Budget Summary")
            total_est = filtered_df["Estimated Budget (€)"].sum()
            total_paid = filtered_df["Paid Amount (€)"].sum()
            total_old = filtered_df["Old Estimated Budget (€)"].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Estimated Budget", f"€{total_est:,.2f}")
            col2.metric("Paid Amount", f"€{total_paid:,.2f}")
            col3.metric("Old Estimated Budget", f"€{total_old:,.2f}")

        except Exception as e:
            st.warning(f"⚠️ Could not load 'Detailed Budget Summary' sheet: {e}")


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

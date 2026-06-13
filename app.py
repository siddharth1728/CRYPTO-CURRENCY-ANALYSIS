import streamlit as st
import pandas as pd
import plotly.express as px 

from crypto_api import get_top_coins, get_coin_history
from indicators import add_moving_average, add_rsi
from portfolio import calculate_portfolio_value
from predictor import predict_next_price

# 1. Page Configuration & Custom Styling
st.set_page_config(
    page_title="Institutional Crypto Analytics Platform",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
.metric-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}
h1 {
    text-align: center;
    color: #1E3A8A;
    margin-bottom: 2rem;
}
h2, h3 {
    color: #1F2937;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Institutional Crypto Analytics Platform")

# Fetch Core Global Market Data
data = get_top_coins()

if data:
    df = pd.DataFrame(data)

    # 2. Sidebar Navigation Hub
    st.sidebar.header("🎯 Navigation Hub")
    page = st.sidebar.radio(
        "Select Workspace",
        ["📊 Market Dashboard", "💼 Portfolio Manager", "🤖 AI Price Predictor"]
    )
    
    st.sidebar.divider()

    # ==========================================
    # WORKSPACE 1: MARKET DASHBOARD
    # ==========================================
    if page == "📊 Market Dashboard":
        st.header("📊 Live Market Intelligence")
        
        # Sidebar Filter only shown on Dashboard
        st.sidebar.subheader("🔍 Filter Data")
        coin_search = st.sidebar.text_input("Search Assets", placeholder="e.g. Bitcoin")

        if coin_search:
            display_df = df[df["name"].str.contains(coin_search, case=False)]
        else:
            display_df = df

        # Global High-Level Market Stats
        total_market_cap = display_df["market_cap"].sum()
        top_coin = display_df.loc[display_df["market_cap"].idxmax(), "name"]
        best_gainer = display_df.loc[display_df["price_change_percentage_24h"].idxmax(), "name"]

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Total Displayed Cap", f"${total_market_cap:,.0f}")
        col2.metric("👑 Market Dominant Asset", top_coin)
        col3.metric("🚀 Top 24H Alpha Gainer", best_gainer)

        st.divider()

        # Market Movers Subsection
        st.subheader("🔥 Momentum Drivers")
        top_gainers = display_df.sort_values(by="price_change_percentage_24h", ascending=False).head(5)
        top_losers = display_df.sort_values(by="price_change_percentage_24h", ascending=True).head(5)

        col_gainer, col_loser = st.columns(2)
        with col_gainer:
            st.success("Top Gainers")
            st.dataframe(top_gainers[["name", "current_price", "price_change_percentage_24h"]], use_container_width=True)
        with col_loser:
            st.error("Top Losers")
            st.dataframe(top_losers[["name", "current_price", "price_change_percentage_24h"]], use_container_width=True)
            
        st.divider()

        # Pricing Table & Chart Analytics Grouping
        st.subheader("📈 Institutional Asset Screener & Charts")
        
        selected_coin = st.selectbox("Select Asset for Deep Technical Analysis", df["id"].tolist())
        selected_days = st.selectbox("Select Technical Evaluation Window", [7, 30, 60, 90, 180, 365], index=1)
        
        history = get_coin_history(selected_coin, selected_days)
        
        if history:
            chart_df = pd.DataFrame(history["prices"], columns=["timestamp", "price"])
            chart_df["timestamp"] = pd.to_datetime(chart_df["timestamp"], unit="ms")
            
            # Technical Indicators
            chart_df = add_moving_average(chart_df)
            chart_df = add_rsi(chart_df)

            fig = px.line(
                chart_df,
                x="timestamp",
                y=["price", "MA_7"],
                title=f"{selected_coin.upper()} Master Price Chart (USD) + 7-Day MA"
            )
            st.plotly_chart(fig, use_container_width=True)

            # RSI Evaluation Card
            latest_rsi = chart_df["RSI"].iloc[-1]
            st.metric("Relative Strength Index (RSI 14)", f"{latest_rsi:.2f}")

            if latest_rsi > 70:
                st.error("🔴 Market Condition: Overbought (Distributive Risk Zone)")
            elif latest_rsi < 30:
                st.success("🟢 Market Condition: Oversold (Accumulation Opportunity Zone)")
            else:
                st.info("🟡 Market Condition: Neutral Momentum")

    # ==========================================
    # WORKSPACE 2: PORTFOLIO MANAGER
    # ==========================================
    elif page == "💼 Portfolio Manager":
        st.header("💼 Multi-Asset Portfolio Suite")
        
        st.subheader("⚙️ Update Holdings")
        portfolio = {}
        
        # Generates clean layout inputs side-by-side for assets
        col_inputs = st.columns(3)
        assets_to_track = ["bitcoin", "ethereum", "solana"]
        for idx, coin in enumerate(assets_to_track):
            with col_inputs[idx]:
                qty = st.number_input(
                    f"{coin.title()} Balance",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key=f"portfolio_{coin}"
                )
                portfolio[coin] = qty

        portfolio_data = []
        total_value = 0

        for coin, qty in portfolio.items():
            coin_row = df[df["id"] == coin]
            if not coin_row.empty:
                price = coin_row["current_price"].values[0]
                value = calculate_portfolio_value(price, qty)
                total_value += value

                if qty > 0:
                    portfolio_data.append({
                        "Coin": coin.title(),
                        "Quantity": qty,
                        "Price": price,
                        "Value": value
                    })

        portfolio_df = pd.DataFrame(portfolio_data)

        if not portfolio_df.empty:
            portfolio_df["Allocation %"] = (portfolio_df["Value"] / portfolio_df["Value"].sum() * 100).round(2)

            st.divider()
            st.subheader("📊 Capital Performance Overview")
            
            # Metric Analytics Cards
            col_m1, col_m2, col_m3 = st.columns(3)
            largest_holding = portfolio_df.loc[portfolio_df["Value"].idxmax(), "Coin"]
            best_performer = portfolio_df.loc[portfolio_df["Price"].idxmax(), "Coin"]

            col_m1.metric("💰 Aggregate Balance Value", f"${total_value:,.2f}")
            col_m2.metric("🏆 Primary Core Holding", largest_holding)
            col_m3.metric("📈 Premium Priced Asset", best_performer)

            st.divider()
            
            # Asset Table and Donut Visualization
            st.dataframe(portfolio_df, use_container_width=True)

            # Report Download Action Button
            csv_report = portfolio_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Export Portfolio Audit Report (CSV)",
                data=csv_report,
                file_name="digital_assets_portfolio_report.csv",
                mime="text/csv"
            )

            st.divider()

            pie_fig = px.pie(
                portfolio_df,
                values="Value",
                names="Coin",
                hole=0.4,
                title="Capital Weight Allocation Profile"
            )
            st.plotly_chart(pie_fig, use_container_width=True)

            # Algorithmic Insights
            st.subheader("💡 Strategic Allocation Insights")
            top_asset = portfolio_df.loc[portfolio_df["Value"].idxmax(), "Coin"]
            allocation = portfolio_df["Allocation %"].max()
            st.info(f"Strategic Notice: Your capital footprint shows a high concentration in **{top_asset}**, representing **{allocation:.2f}%** of your active global allocation.")
        else:
            st.info("No active assets identified. Please enter tracking quantities above to compile your audit board.")

    # ==========================================
    # WORKSPACE 3: AI PRICE PREDICTOR
    # ==========================================
    elif page == "🤖 AI Price Predictor":
        st.header("🤖 Machine Learning Pricing Intelligence")
        st.caption("Powered by Scikit-Learn Linear Regression Models")

        selected_ai_coin = st.selectbox("Choose Target Asset for ML Engine Evaluation", df["id"].tolist(), key="ai_coin")
        ai_days = st.selectbox("Select Training Model Data Range", [30, 60, 90, 180, 365], index=2, key="ai_days")

        ai_history = get_coin_history(selected_ai_coin, ai_days)

        if ai_history:
            ai_chart_df = pd.DataFrame(ai_history["prices"], columns=["timestamp", "price"])
            predicted_price = predict_next_price(ai_chart_df)
            ai_current_price = ai_chart_df["price"].iloc[-1]
            
            prediction_change = ((predicted_price - ai_current_price) / ai_current_price) * 100

            st.divider()
            
            col_p1, col_p2 = st.columns(2)
            col_p1.metric("Predicted Next Session Target Price", f"${predicted_price:,.2f}")
            col_p2.metric("Projected Lineal Trend Target Delta", f"{prediction_change:.2f}%")

            if predicted_price > ai_current_price:
                st.success(f"🟢 Predictive Forecast Signal: STRATEGIC BUY — Model indicates linear continuation momentum on {selected_ai_coin.upper()}.")
            elif predicted_price < ai_current_price:
                st.error(f"🔴 Predictive Forecast Signal: STRATEGIC LIQUIDATE/SELL — Model implies down-sloping structural resistance ahead on {selected_ai_coin.upper()}.")
            else:
                st.info("🟡 Predictive Forecast Signal: NEUTRAL HOLD — Flat mathematical delta expected over next session interval.")

    # 3. System Universal Premium Footer Terminal
    st.divider()
    st.caption("🔒 Analytics Core Terminal Framework | Built securely utilizing Python, Streamlit, Plotly, & Scikit-Learn Engine Protocols 🚀")

else:
    st.error("Terminal Interruption: Unable to securely connect to external pricing services.")
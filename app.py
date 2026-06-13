import streamlit as st
import pandas as pd
import plotly.express as px 

from crypto_api import get_top_coins, get_coin_history
from indicators import add_moving_average, add_rsi
from portfolio import calculate_portfolio_value
from predictor import predict_next_price

st.set_page_config(
    page_title="Crypto Analyzer",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 AI Cryptocurrency Analyzer")

data = get_top_coins()

if data:

    df = pd.DataFrame(data)

    st.sidebar.header("Search")

    coin_search = st.sidebar.text_input(
        "Search Cryptocurrency"
    )

    if coin_search:
        df = df[
            df["name"].str.contains(
                coin_search,
                case=False
            )
        ]

    total_market_cap = df["market_cap"].sum()

    top_coin = df.loc[
        df["market_cap"].idxmax(),
        "name"
    ]

    best_gainer = df.loc[
        df["price_change_percentage_24h"].idxmax(),
        "name"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💰 Total Market Cap",
        f"${total_market_cap:,.0f}"
    )

    col2.metric(
        "👑 Largest Coin",
        top_coin
    )

    col3.metric(
        "🚀 Top Gainer (24H)",
        best_gainer
    )

    st.divider()
    st.divider()

    st.subheader("🔥 Market Movers")

    top_gainers = df.sort_values(
        by="price_change_percentage_24h",
        ascending=False
    ).head(5)

    top_losers = df.sort_values(
        by="price_change_percentage_24h",
        ascending=True
    ).head(5)

    col1, col2 = st.columns(2)

    with col1:
        st.success("Top Gainers")
        st.dataframe(
            top_gainers[
                [
                    "name",
                    "current_price",
                    "price_change_percentage_24h"
                ]
            ],
            use_container_width=True
        )

    with col2:
        st.error("Top Losers")
        st.dataframe(
            top_losers[
                [
                    "name",
                    "current_price",
                    "price_change_percentage_24h"
                ]
            ],
            use_container_width=True
        )
        
    st.subheader("Top 20 Cryptocurrencies")

    display_df = df[
        [
            "name",
            "symbol",
            "current_price",
            "market_cap",
            "price_change_percentage_24h"
        ]
    ]

    st.dataframe(
        display_df,
        use_container_width=True
    )

    st.divider()

    st.subheader("📈 Price Analysis")

    selected_coin = st.selectbox(
        "Select Cryptocurrency",
        df["id"].tolist()
    )

    selected_days = st.selectbox(
        "Select Time Range",
        [7, 30, 60, 90, 180, 365],
        index=1
    )
    
    history = get_coin_history(
        selected_coin,
        selected_days
    )
    
    if history:
        prices = history["prices"]

        chart_df = pd.DataFrame(
            prices,
            columns=[
                "timestamp",
                "price"
            ]
        )
        
        chart_df["timestamp"] = pd.to_datetime(
            chart_df["timestamp"],
            unit="ms"
        )
        
        chart_df = add_moving_average(chart_df)
        chart_df = add_rsi(chart_df)

        fig = px.line(
            chart_df,
            x="timestamp",
            y=["price", "MA_7"],
            title=f"{selected_coin.upper()} Price History + MA(7)"
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            legend_title="Legend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # --- RSI Section ---
        latest_rsi = chart_df["RSI"].iloc[-1]

        st.metric(
            "RSI (14)",
            f"{latest_rsi:.2f}"
        )

        if latest_rsi > 70:
            st.error("🔴 Overbought Zone")
        elif latest_rsi < 30:
            st.success("🟢 Oversold Zone")
        else:
            st.info("🟡 Neutral Zone")

        st.divider()

        # --- NEW: AI Price Prediction Section ---
        st.subheader("🤖 AI Price Prediction")
        
        predicted_price = predict_next_price(chart_df)
        
        # Grab the latest actual price from our chart dataframe
        ai_current_price = chart_df["price"].iloc[-1]
        
        prediction_change = (
            (predicted_price - ai_current_price)
            / ai_current_price
            * 100
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Predicted Next Price",
            f"${predicted_price:,.2f}"
        )

        col2.metric(
            "Expected Change",
            f"{prediction_change:.2f}%"
        )

        if predicted_price > ai_current_price:
            st.success("🟢 AI Signal: BUY")
        elif predicted_price < ai_current_price:
            st.error("🔴 AI Signal: SELL")
        else:
            st.info("🟡 AI Signal: HOLD")
        
        st.divider()
        # ----------------------------------------
        
        # --- MULTI-COIN PORTFOLIO MANAGER ---
        st.subheader("📊 Multi-Coin Portfolio")
        
        portfolio = {}

        for coin in ["bitcoin", "ethereum", "solana"]:
            qty = st.number_input(
                f"{coin.title()} Quantity",
                min_value=0.0,
                value=0.0,
                step=0.1,
                key=coin
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
                    portfolio_data.append(
                        {
                            "Coin": coin.title(),
                            "Quantity": qty,
                            "Price": price,
                            "Value": value
                        }
                    )

        portfolio_df = pd.DataFrame(portfolio_data)

        if not portfolio_df.empty:
            portfolio_df["Allocation %"] = (
                portfolio_df["Value"]
                / portfolio_df["Value"].sum()
                * 100
            ).round(2)

            col1, col2, col3 = st.columns(3)

            largest_holding = portfolio_df.loc[
                portfolio_df["Value"].idxmax(),
                "Coin"
            ]

            largest_value = portfolio_df["Value"].max()

            best_performer = portfolio_df.loc[
                portfolio_df["Price"].idxmax(),
                "Coin"
            ]

            col1.metric(
                "💰 Total Portfolio Value",
                f"${total_value:,.2f}"
            )

            col2.metric(
                "🏆 Largest Holding",
                largest_holding
            )

            col3.metric(
                "📈 Highest Priced Coin",
                best_performer
            )

            st.divider()

            st.dataframe(
                portfolio_df,
                use_container_width=True
            )

            pie_fig = px.pie(
                portfolio_df,
                values="Value",
                names="Coin",
                hole=0.4,
                title="Portfolio Allocation"
            )

            st.plotly_chart(
                pie_fig,
                use_container_width=True
            )

            st.subheader("📊 Portfolio Insights")

            top_asset = portfolio_df.loc[
                portfolio_df["Value"].idxmax(),
                "Coin"
            ]

            allocation = portfolio_df["Allocation %"].max()

            st.info(
                f"Your largest position is {top_asset} "
                f"with {allocation:.2f}% allocation."
            )
        else:
            st.info("Enter quantities above to generate your portfolio dashboard!")
else:
    st.error("Failed to fetch cryptocurrency data.")
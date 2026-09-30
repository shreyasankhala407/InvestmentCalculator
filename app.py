# ============================================================
# INVESTMENT CALCULATOR
# Beginner-friendly Streamlit Application
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Investment Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 650;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .disclaimer {
        font-size: 13px;
        color: #6b7280;
        padding: 15px;
        border-top: 1px solid #ddd;
        margin-top: 30px;
    }

    [data-testid="stMetricValue"] {
        font-size: 26px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CURRENCY FORMATTING
# ============================================================

def format_inr(value):
    """
    Convert a number into Indian currency format.

    Example:
    1250000 -> ₹12,50,000
    """

    value = float(value)

    sign = "-" if value < 0 else ""
    value = abs(value)

    if value.is_integer():
        number = str(int(value))
    else:
        number = f"{value:,.2f}"

    if "." in number:
        integer_part, decimal_part = number.split(".")
    else:
        integer_part = number
        decimal_part = ""

    integer_part = integer_part.replace(",", "")

    if len(integer_part) <= 3:
        indian_number = integer_part
    else:

        last_three = integer_part[-3:]
        remaining = integer_part[:-3]

        groups = []

        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            groups.insert(0, remaining)

        indian_number = ",".join(groups) + "," + last_three

    if decimal_part:
        return f"{sign}₹{indian_number}.{decimal_part}"

    return f"{sign}₹{indian_number}"


# ============================================================
# COMMON VALIDATION
# ============================================================

def validate_common_inputs(amount, rate, years):

    valid = True

    if amount < 0:
        st.error(
            "Investment amount must be greater than or equal to ₹0."
        )
        valid = False

    if rate < 0:
        st.error(
            "Expected return cannot be negative."
        )
        valid = False

    if years <= 0:
        st.error(
            "Investment period must be greater than 0."
        )
        valid = False

    return valid


# ============================================================
# SIP CALCULATOR
# ============================================================

def calculate_sip(monthly_investment, annual_rate, years):

    months = int(years * 12)

    monthly_rate = annual_rate / 100 / 12

    total_invested = monthly_investment * months

    if monthly_rate == 0:

        future_value = total_invested

    else:

        future_value = (
            monthly_investment
            * (
                ((1 + monthly_rate) ** months - 1)
                / monthly_rate
            )
            * (1 + monthly_rate)
        )

    estimated_returns = future_value - total_invested

    yearly_data = []

    for year in range(1, int(years) + 1):

        month_count = year * 12

        if monthly_rate == 0:

            value = monthly_investment * month_count

        else:

            value = (
                monthly_investment
                * (
                    ((1 + monthly_rate) ** month_count - 1)
                    / monthly_rate
                )
                * (1 + monthly_rate)
            )

        invested = monthly_investment * month_count

        returns = value - invested

        yearly_data.append({
            "Year": year,
            "Total Investment": invested,
            "Portfolio Value": value,
            "Estimated Returns": returns
        })

    df = pd.DataFrame(yearly_data)

    return (
        total_invested,
        estimated_returns,
        future_value,
        df
    )


# ============================================================
# LUMP SUM CALCULATOR
# ============================================================

def calculate_lumpsum(initial_investment, annual_rate, years):

    future_value = initial_investment * (
        1 + annual_rate / 100
    ) ** years

    estimated_returns = future_value - initial_investment

    yearly_data = []

    for year in range(1, int(years) + 1):

        value = initial_investment * (
            1 + annual_rate / 100
        ) ** year

        returns = value - initial_investment

        yearly_data.append({
            "Year": year,
            "Initial Investment": initial_investment,
            "Portfolio Value": value,
            "Estimated Returns": returns
        })

    df = pd.DataFrame(yearly_data)

    return (
        initial_investment,
        estimated_returns,
        future_value,
        df
    )


# ============================================================
# STEP-UP SIP CALCULATOR
# ============================================================

def calculate_stepup_sip(
    initial_monthly_sip,
    step_up_percentage,
    annual_rate,
    years
):

    monthly_rate = annual_rate / 100 / 12

    current_sip = initial_monthly_sip

    total_invested = 0

    portfolio_value = 0

    yearly_data = []

    for year in range(1, int(years) + 1):

        yearly_investment = current_sip * 12

        for month in range(12):

            total_invested += current_sip

            portfolio_value = (
                portfolio_value * (1 + monthly_rate)
                + current_sip
            )

        yearly_data.append({
            "Year": year,
            "Monthly SIP": current_sip,
            "Annual Investment": yearly_investment,
            "Total Investment": total_invested,
            "Portfolio Value": portfolio_value,
            "Estimated Returns":
                portfolio_value - total_invested
        })

        current_sip *= (
            1 + step_up_percentage / 100
        )

    df = pd.DataFrame(yearly_data)

    final_value = portfolio_value

    estimated_returns = (
        final_value - total_invested
    )

    return (
        total_invested,
        estimated_returns,
        final_value,
        df
    )


# ============================================================
# GOAL-BASED INVESTMENT CALCULATOR
# ============================================================

def calculate_goal_based(
    goal_amount,
    years,
    annual_rate
):

    annual_rate_decimal = annual_rate / 100

    monthly_rate = annual_rate_decimal / 12

    months = int(years * 12)

    # --------------------------------------------------------
    # Required Lump Sum
    # --------------------------------------------------------

    if annual_rate_decimal == 0:

        required_lumpsum = goal_amount

    else:

        required_lumpsum = (
            goal_amount /
            (
                (1 + annual_rate_decimal)
                ** years
            )
        )

    # --------------------------------------------------------
    # Required Monthly SIP
    # --------------------------------------------------------

    if monthly_rate == 0:

        required_sip = goal_amount / months

    else:

        sip_factor = (
            (
                (1 + monthly_rate) ** months - 1
            )
            / monthly_rate
        ) * (1 + monthly_rate)

        required_sip = (
            goal_amount / sip_factor
        )

    return (
        required_sip,
        required_lumpsum
    )


# ============================================================
# INVESTMENT COMPARISON
# ============================================================

def calculate_comparison(
    investment_a,
    return_a,
    years_a,
    investment_b,
    return_b,
    years_b
):

    future_a = investment_a * (
        1 + return_a / 100
    ) ** years_a

    future_b = investment_b * (
        1 + return_b / 100
    ) ** years_b

    difference = abs(
        future_a - future_b
    )

    if future_a > future_b:

        winner = "Option A"

    elif future_b > future_a:

        winner = "Option B"

    else:

        winner = "Both options are equal"

    comparison_df = pd.DataFrame({
        "Option": [
            "Option A",
            "Option B"
        ],
        "Future Value": [
            future_a,
            future_b
        ]
    })

    return (
        future_a,
        future_b,
        difference,
        winner,
        comparison_df
    )


# ============================================================
# CHART FUNCTIONS
# ============================================================

def create_growth_chart(
    df,
    investment_column,
    value_column
):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df[investment_column],
            mode="lines+markers",
            name="Total Investment",
            hovertemplate=(
                "Year %{x}"
                "<br>Investment ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df[value_column],
            mode="lines+markers",
            name="Portfolio Value",
            hovertemplate=(
                "Year %{x}"
                "<br>Value ₹%{y:,.0f}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title="Investment Growth Over Time",
        xaxis_title="Year",
        yaxis_title="Amount (₹)",
        hovermode="x unified",
        template="plotly_white"
    )

    return fig


def create_principal_returns_chart(
    principal,
    returns,
    title
):

    fig = go.Figure(
        data=[
            go.Bar(
                x=[
                    "Principal",
                    "Estimated Returns"
                ],
                y=[
                    principal,
                    returns
                ],
                text=[
                    format_inr(principal),
                    format_inr(returns)
                ],
                textposition="auto"
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title="Component",
        yaxis_title="Amount (₹)",
        template="plotly_white"
    )

    return fig


def create_comparison_chart(
    comparison_df
):

    fig = px.bar(
        comparison_df,
        x="Option",
        y="Future Value",
        text="Future Value",
        title="Investment Comparison"
    )

    fig.update_traces(
        texttemplate="₹%{text:,.0f}",
        textposition="outside"
    )

    fig.update_layout(
        yaxis_title="Future Value (₹)",
        xaxis_title="Investment Option",
        template="plotly_white"
    )

    return fig


# ============================================================
# CSV DOWNLOAD FUNCTION
# ============================================================

def download_csv(
    df,
    filename
):

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Year-wise Data",
        data=csv_data,
        file_name=filename,
        mime="text/csv"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    'Investment Calculator'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Plan your investments and estimate your future wealth.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

st.sidebar.title(
    "📊 Investment Calculator"
)

page = st.sidebar.radio(
    "Select Calculator",
    [
        "🏠 Dashboard",
        "💰 SIP Calculator",
        "💵 Lump Sum Calculator",
        "📈 Step-Up SIP Calculator",
        "🎯 Goal-Based Investment",
        "📊 Investment Comparison"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "💡 Tip: Try different return rates and investment "
    "periods to understand how compounding affects your wealth."
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">'
        'Welcome to the Investment Calculator'
        '</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        This application helps you estimate the future value
        of your investments using different investment strategies.
        """
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "💰 SIP",
            "Monthly Investing"
        )

    with col2:

        st.metric(
            "💵 Lump Sum",
            "One-Time Investing"
        )

    with col3:

        st.metric(
            "📈 Step-Up SIP",
            "Increasing SIP"
        )

    st.markdown("---")

    st.subheader(
        "Available Calculators"
    )

    feature_data = pd.DataFrame({
        "Calculator": [
            "SIP Calculator",
            "Lump Sum Calculator",
            "Step-Up SIP Calculator",
            "Goal-Based Investment",
            "Investment Comparison"
        ],
        "Purpose": [
            "Estimate wealth created through monthly investments.",
            "Estimate growth of a one-time investment.",
            "Calculate wealth when SIP increases every year.",
            "Calculate investment required to achieve a financial goal.",
            "Compare two different investment strategies."
        ]
    })

    st.dataframe(
        feature_data,
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Select a calculator from the sidebar to begin."
    )


# ============================================================
# SIP CALCULATOR
# ============================================================

elif page == "💰 SIP Calculator":

    st.markdown(
        '<div class="section-title">'
        '💰 SIP Calculator'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        monthly_investment = st.number_input(
            "Monthly Investment (₹)",
            min_value=0.0,
            value=5000.0,
            step=500.0
        )

    with col2:

        annual_rate = st.number_input(
            "Expected Annual Return (%)",
            min_value=0.0,
            value=12.0,
            step=0.5
        )

    with col3:

        years = st.number_input(
            "Investment Period (Years)",
            min_value=1,
            value=10,
            step=1
        )

    if st.button(
        "🔄 Reset SIP Calculator"
    ):

        st.rerun()

    if validate_common_inputs(
        monthly_investment,
        annual_rate,
        years
    ):

        (
            total_invested,
            returns,
            future_value,
            df
        ) = calculate_sip(
            monthly_investment,
            annual_rate,
            years
        )

        st.markdown(
            "### 📌 Investment Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Amount Invested",
                format_inr(total_invested)
            )

        with col2:

            st.metric(
                "Estimated Returns",
                format_inr(returns)
            )

        with col3:

            st.metric(
                "Future Value",
                format_inr(future_value)
            )

        st.markdown("---")

        st.plotly_chart(
            create_growth_chart(
                df,
                "Total Investment",
                "Portfolio Value"
            ),
            use_container_width=True
        )

        col1, col2 = st.columns(2)

        with col1:

            st.plotly_chart(
                create_principal_returns_chart(
                    total_invested,
                    returns,
                    "Principal vs Estimated Returns"
                ),
                use_container_width=True
            )

        with col2:

            st.dataframe(
                df.style.format({
                    "Total Investment": "₹{:,.0f}",
                    "Portfolio Value": "₹{:,.0f}",
                    "Estimated Returns": "₹{:,.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )

        download_csv(
            df,
            "sip_yearwise_calculation.csv"
        )

        with st.expander(
            "📚 How is SIP calculated?"
        ):

            st.markdown(
                """
                ### SIP Future Value Formula

                **FV = P × [((1 + r)ⁿ - 1) / r] × (1 + r)**

                Where:

                - **FV** = Future Value
                - **P** = Monthly SIP investment
                - **r** = Monthly rate of return
                - **n** = Number of monthly investments

                The annual expected return is converted into a
                monthly return by dividing it by 12.
                """
            )


# ============================================================
# LUMP SUM CALCULATOR
# ============================================================

elif page == "💵 Lump Sum Calculator":

    st.markdown(
        '<div class="section-title">'
        '💵 Lump Sum Calculator'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        initial_investment = st.number_input(
            "Initial Investment (₹)",
            min_value=0.0,
            value=100000.0,
            step=5000.0
        )

    with col2:

        annual_rate = st.number_input(
            "Expected Annual Return (%)",
            min_value=0.0,
            value=12.0,
            step=0.5
        )

    with col3:

        years = st.number_input(
            "Investment Period (Years)",
            min_value=1,
            value=10,
            step=1
        )

    if st.button(
        "🔄 Reset Lump Sum Calculator"
    ):

        st.rerun()

    if validate_common_inputs(
        initial_investment,
        annual_rate,
        years
    ):

        (
            principal,
            returns,
            future_value,
            df
        ) = calculate_lumpsum(
            initial_investment,
            annual_rate,
            years
        )

        st.markdown(
            "### 📌 Investment Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Initial Investment",
                format_inr(principal)
            )

        with col2:

            st.metric(
                "Estimated Returns",
                format_inr(returns)
            )

        with col3:

            st.metric(
                "Future Value",
                format_inr(future_value)
            )

        st.markdown("---")

        st.plotly_chart(
            create_growth_chart(
                df,
                "Initial Investment",
                "Portfolio Value"
            ),
            use_container_width=True
        )

        st.plotly_chart(
            create_principal_returns_chart(
                principal,
                returns,
                "Initial Investment vs Estimated Returns"
            ),
            use_container_width=True
        )

        st.subheader(
            "📅 Year-wise Growth"
        )

        st.dataframe(
            df.style.format({
                "Initial Investment": "₹{:,.0f}",
                "Portfolio Value": "₹{:,.0f}",
                "Estimated Returns": "₹{:,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        download_csv(
            df,
            "lump_sum_yearwise_calculation.csv"
        )

        with st.expander(
            "📚 How is Lump Sum calculated?"
        ):

            st.markdown(
                """
                ### Lump Sum Future Value Formula

                **FV = P × (1 + r)ⁿ**

                Where:

                - **FV** = Future Value
                - **P** = Initial Investment
                - **r** = Annual rate of return
                - **n** = Number of years

                This calculation demonstrates the effect of
                compound growth on a one-time investment.
                """
            )


# ============================================================
# STEP-UP SIP CALCULATOR
# ============================================================

elif page == "📈 Step-Up SIP Calculator":

    st.markdown(
        '<div class="section-title">'
        '📈 Step-Up SIP Calculator'
        '</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        initial_sip = st.number_input(
            "Initial Monthly SIP (₹)",
            min_value=0.0,
            value=5000.0,
            step=500.0
        )

        step_up = st.number_input(
            "Annual Step-Up Percentage (%)",
            min_value=0.0,
            value=10.0,
            step=1.0
        )

    with col2:

        annual_rate = st.number_input(
            "Expected Annual Return (%)",
            min_value=0.0,
            value=12.0,
            step=0.5
        )

        years = st.number_input(
            "Investment Period (Years)",
            min_value=1,
            value=10,
            step=1
        )

    if st.button(
        "🔄 Reset Step-Up SIP Calculator"
    ):

        st.rerun()

    if initial_sip < 0:

        st.error(
            "Initial SIP must be greater than or equal to ₹0."
        )

    elif step_up < 0:

        st.error(
            "Step-up percentage cannot be negative."
        )

    elif annual_rate < 0:

        st.error(
            "Expected return cannot be negative."
        )

    elif years <= 0:

        st.error(
            "Investment period must be greater than 0."
        )

    else:

        (
            total_invested,
            returns,
            future_value,
            df
        ) = calculate_stepup_sip(
            initial_sip,
            step_up,
            annual_rate,
            years
        )

        st.markdown(
            "### 📌 Investment Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Amount Invested",
                format_inr(total_invested)
            )

        with col2:

            st.metric(
                "Total Estimated Returns",
                format_inr(returns)
            )

        with col3:

            st.metric(
                "Final Portfolio Value",
                format_inr(future_value)
            )

        st.markdown("---")

        st.subheader(
            "📅 Year-wise SIP"
        )

        st.dataframe(
            df.style.format({
                "Monthly SIP": "₹{:,.0f}",
                "Annual Investment": "₹{:,.0f}",
                "Total Investment": "₹{:,.0f}",
                "Portfolio Value": "₹{:,.0f}",
                "Estimated Returns": "₹{:,.0f}"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.subheader(
            "📊 Portfolio Growth"
        )

        st.plotly_chart(
            create_growth_chart(
                df,
                "Total Investment",
                "Portfolio Value"
            ),
            use_container_width=True
        )

        fig_sip = px.bar(
            df,
            x="Year",
            y="Monthly SIP",
            title="Monthly SIP Amount by Year"
        )

        fig_sip.update_layout(
            xaxis_title="Year",
            yaxis_title="Monthly SIP (₹)",
            template="plotly_white"
        )

        st.plotly_chart(
            fig_sip,
            use_container_width=True
        )

        download_csv(
            df,
            "stepup_sip_yearwise_calculation.csv"
        )

        with st.expander(
            "📚 How does Step-Up SIP work?"
        ):

            st.markdown(
                """
                A Step-Up SIP increases the monthly investment
                every year.

                Example with a ₹5,000 SIP and 10% annual step-up:

                | Year | Monthly SIP |
                |---|---:|
                | 1 | ₹5,000 |
                | 2 | ₹5,500 |
                | 3 | ₹6,050 |
                | 4 | ₹6,655 |

                The calculator compounds each monthly contribution
                while increasing the SIP every year.
                """
            )


# ============================================================
# GOAL-BASED INVESTMENT
# ============================================================

elif page == "🎯 Goal-Based Investment":

    st.markdown(
        '<div class="section-title">'
        '🎯 Goal-Based Investment'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # INPUTS
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        goal_amount = st.number_input(
            "Financial Goal Amount (₹)",
            min_value=0.0,
            value=1000000.0,
            step=10000.0
        )

    with col2:

        years = st.number_input(
            "Investment Period (Years)",
            min_value=1,
            value=10,
            step=1
        )

    with col3:

        annual_rate = st.number_input(
            "Expected Annual Return (%)",
            min_value=0.0,
            value=12.0,
            step=0.5
        )

    if st.button(
        "🔄 Reset Goal Calculator"
    ):

        st.rerun()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if goal_amount <= 0:

        st.error(
            "Goal amount must be greater than ₹0."
        )

    elif annual_rate < 0:

        st.error(
            "Expected return cannot be negative."
        )

    elif years <= 0:

        st.error(
            "Investment period must be greater than 0."
        )

    else:

        (
            required_sip,
            required_lumpsum
        ) = calculate_goal_based(
            goal_amount,
            years,
            annual_rate
        )

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        st.markdown(
            "### 📌 Goal Investment Summary"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Financial Goal",
                format_inr(goal_amount)
            )

        with col2:

            st.metric(
                "Required Monthly SIP",
                format_inr(required_sip)
            )

        with col3:

            st.metric(
                "Required Lump Sum",
                format_inr(required_lumpsum)
            )

        st.markdown("---")

        # ----------------------------------------------------
        # GOAL CHART
        # ----------------------------------------------------

        goal_df = pd.DataFrame({
            "Investment Method": [
                "Monthly SIP",
                "Lump Sum"
            ],
            "Required Investment": [
                required_sip,
                required_lumpsum
            ]
        })

        fig = px.bar(
            goal_df,
            x="Investment Method",
            y="Required Investment",
            text="Required Investment",
            title="Investment Required to Achieve Your Goal"
        )

        fig.update_traces(
            texttemplate="₹%{text:,.0f}",
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Investment Method",
            yaxis_title="Amount (₹)",
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # CALCULATION EXPLANATION
        # ----------------------------------------------------

        with st.expander(
            "📚 How is the Goal-Based Calculation done?"
        ):

            st.markdown(
                """
                ### Goal-Based Investment Calculation

                This calculator determines how much you need to
                invest to achieve your financial goal based on:

                - **Financial Goal Amount**
                - **Investment Period**
                - **Expected Annual Return**

                #### Required Monthly SIP

                The calculator determines the monthly SIP required
                to accumulate the target amount by the end of the
                selected investment period.

                #### Required Lump Sum

                The calculator determines the amount that needs to
                be invested today as a one-time investment to
                potentially reach the target amount.

                The calculation assumes that the expected return
                remains constant throughout the investment period.
                """
            )


# ============================================================
# INVESTMENT COMPARISON
# ============================================================

elif page == "📊 Investment Comparison":

    st.markdown(
        '<div class="section-title">'
        '📊 Investment Comparison'
        '</div>',
        unsafe_allow_html=True
    )

    option_a, option_b = st.columns(2)

    # --------------------------------------------------------
    # OPTION A
    # --------------------------------------------------------

    with option_a:

        st.subheader(
            "🅰️ Option A"
        )

        investment_a = st.number_input(
            "Investment Amount - Option A (₹)",
            min_value=0.0,
            value=100000.0,
            step=5000.0
        )

        return_a = st.number_input(
            "Expected Return - Option A (%)",
            min_value=0.0,
            value=10.0,
            step=0.5
        )

        years_a = st.number_input(
            "Investment Period - Option A (Years)",
            min_value=1,
            value=10,
            step=1
        )

    # --------------------------------------------------------
    # OPTION B
    # --------------------------------------------------------

    with option_b:

        st.subheader(
            "🅱️ Option B"
        )

        investment_b = st.number_input(
            "Investment Amount - Option B (₹)",
            min_value=0.0,
            value=100000.0,
            step=5000.0
        )

        return_b = st.number_input(
            "Expected Return - Option B (%)",
            min_value=0.0,
            value=12.0,
            step=0.5
        )

        years_b = st.number_input(
            "Investment Period - Option B (Years)",
            min_value=1,
            value=10,
            step=1
        )

    if st.button(
        "🔄 Reset Comparison"
    ):

        st.rerun()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    valid = True

    if investment_a < 0 or investment_b < 0:

        st.error(
            "Investment amounts must be greater than or equal to ₹0."
        )

        valid = False

    if return_a < 0 or return_b < 0:

        st.error(
            "Return rates cannot be negative."
        )

        valid = False

    if years_a <= 0 or years_b <= 0:

        st.error(
            "Investment periods must be greater than 0."
        )

        valid = False

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    if valid:

        (
            future_a,
            future_b,
            difference,
            winner,
            comparison_df
        ) = calculate_comparison(
            investment_a,
            return_a,
            years_a,
            investment_b,
            return_b,
            years_b
        )

        st.markdown(
            "### 📌 Comparison Results"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Future Value - Option A",
                format_inr(future_a)
            )

        with col2:

            st.metric(
                "Future Value - Option B",
                format_inr(future_b)
            )

        with col3:

            st.metric(
                "Difference",
                format_inr(difference)
            )

        if winner == "Option A":

            st.success(
                "🏆 Option A generates the higher estimated wealth."
            )

        elif winner == "Option B":

            st.success(
                "🏆 Option B generates the higher estimated wealth."
            )

        else:

            st.info(
                "Both options generate the same estimated future value."
            )

        st.markdown("---")

        st.plotly_chart(
            create_comparison_chart(
                comparison_df
            ),
            use_container_width=True
        )

        comparison_display = comparison_df.copy()

        comparison_display[
            "Future Value"
        ] = comparison_display[
            "Future Value"
        ].apply(format_inr)

        st.dataframe(
            comparison_display,
            use_container_width=True,
            hide_index=True
        )

        download_csv(
            comparison_df,
            "investment_comparison.csv"
        )

        with st.expander(
            "📚 How does the comparison work?"
        ):

            st.markdown(
                """
                Each option is calculated using the compound
                interest formula:

                **FV = P × (1 + r)ⁿ**

                The calculated future values are then compared.

                The option with the higher estimated future value
                is displayed as the winner.

                Remember that a higher expected return can involve
                different levels of investment risk. Therefore,
                this calculator should not be the only basis for
                an investment decision.
                """
            )


# ============================================================
# DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">

    <b>Disclaimer:</b> These calculations are estimates based on
    the assumptions entered by the user. Actual investment returns
    may vary. This calculator does not constitute investment advice.

    </div>
    """,
    unsafe_allow_html=True
)
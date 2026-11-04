from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="FixIt Services | Performance Dashboard",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data.csv"
PALETTE = ["#2563EB", "#10B981", "#F59E0B", "#8B5CF6", "#EF4444"]


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Ad Spend", "Conversions", "Revenue"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Client Type"] = df["Client Type"].fillna("Unknown")
    df["Time"] = df["Time"].fillna("Unknown")
    return df.dropna(subset=["Date"])


def money(value):
    return f"${value:,.0f}"


df = load_data()
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #F5F7FB; }
    [data-testid="stSidebar"] { background: #101B36; }
    [data-testid="stSidebar"] * { color: #F4F7FF; }
    .hero { background: linear-gradient(115deg,#14264C 0%,#2458B8 100%); padding: 1.45rem 1.7rem;
      border-radius: 18px; color: white; margin: .2rem 0 1rem 0; }
    .hero h1 { color: white; margin: 0 0 .25rem 0; font-size: 2rem; }
    .hero p { color: #DCE8FF; margin: 0; font-size: .98rem; }
    .metric-note { color:#68758E; font-size:.78rem; margin-top:-.55rem; }
    .section-label { color:#1B2B4D; font-size:1.16rem; font-weight:700; padding:.2rem 0 .3rem; }
    .small-note { color:#61708A; font-size:.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>🛠️ FixIt Services</h1>
      <p>Service performance, customer mix, and advertising efficiency</p>
    </div>
    """,
    unsafe_allow_html=True,
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
with st.sidebar:
    st.markdown("## Dashboard filters")
    st.caption("Choose a reporting window and customer/time segments.")
    selected_dates = st.date_input(
        "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )
    times = sorted(df["Time"].dropna().unique().tolist())
    selected_times = st.multiselect("Time of day", times, default=times)
    client_types = sorted(df["Client Type"].dropna().unique().tolist())
    selected_clients = st.multiselect("Client type", client_types, default=client_types)
    st.divider()
    st.caption("Source: FixIt Services_Data.xlsx · 2,000 source records")

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
else:
    start_date = end_date = selected_dates[0]
filtered = df[
    df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
    & df["Time"].isin(selected_times)
    & df["Client Type"].isin(selected_clients)
].copy()

if filtered.empty:
    st.warning("No records match these filters. Adjust the selections in the sidebar.")
    st.stop()

revenue = filtered["Revenue"].sum()
ad_spend = filtered["Ad Spend"].sum()
conversions = filtered["Conversions"].sum()
roas = revenue / ad_spend if ad_spend else 0
returning_share = filtered["Client Type"].isin(["Returning", "Loyal"]).mean()
revenue_less_ads = revenue - ad_spend

st.markdown('<div class="section-label">Performance snapshot</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue", money(revenue))
k2.metric("Ad spend", money(ad_spend))
k3.metric("Ad ROAS", f"{roas:.2f}×")
k4.metric("Conversions", f"{conversions:,.0f}")
k5.metric("Returning + loyal", f"{returning_share:.1%}")
st.markdown(
    '<p class="metric-note">ROAS = revenue ÷ ad spend. Revenue less ad spend is not net profit; operating and service costs are not in the source.</p>',
    unsafe_allow_html=True,
)

left, right = st.columns([1.55, 1])
with left:
    st.markdown('<div class="section-label">Revenue and ad spend over time</div>', unsafe_allow_html=True)
    monthly = filtered.assign(Month=filtered["Date"].dt.to_period("M").dt.to_timestamp()).groupby("Month", as_index=False)[["Revenue", "Ad Spend"]].sum()
    monthly_long = monthly.melt(id_vars="Month", var_name="Measure", value_name="Amount")
    fig = px.line(monthly_long, x="Month", y="Amount", color="Measure", markers=True,
                  color_discrete_map={"Revenue": PALETTE[0], "Ad Spend": PALETTE[2]})
    fig.update_layout(margin=dict(l=8, r=8, t=12, b=8), height=330, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                      legend_title_text="", hovermode="x unified")
    fig.update_yaxes(title="USD", gridcolor="#E9EDF5", zeroline=False)
    fig.update_xaxes(title="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-label">Customer mix</div>', unsafe_allow_html=True)
    mix = filtered.groupby("Client Type", as_index=False).size().rename(columns={"size": "Records"})
    fig = px.pie(mix, names="Client Type", values="Records", hole=.62,
                 color="Client Type", color_discrete_map={"Loyal": PALETTE[1], "Returning": PALETTE[0], "New": PALETTE[2]})
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=8, r=8, t=12, b=8), height=330, paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-label">Performance by time of day</div>', unsafe_allow_html=True)
time_perf = filtered.groupby("Time", as_index=False).agg(
    Revenue=("Revenue", "sum"), Ad_Spend=("Ad Spend", "sum"),
    Conversions=("Conversions", "sum"), Records=("Date", "count")
)
time_perf["ROAS"] = time_perf.apply(lambda r: r["Revenue"] / r["Ad_Spend"] if r["Ad_Spend"] else 0, axis=1)
order = [x for x in ["Morning", "Afternoon", "Evening", "Night"] if x in time_perf["Time"].tolist()]
time_perf["Time"] = pd.Categorical(time_perf["Time"], categories=order, ordered=True)
time_perf = time_perf.sort_values("Time")
t1, t2 = st.columns([1.25, 1])
with t1:
    fig = px.bar(time_perf, x="Time", y=["Revenue", "Ad_Spend"], barmode="group",
                 color_discrete_map={"Revenue": PALETTE[0], "Ad_Spend": PALETTE[2]})
    fig.update_layout(margin=dict(l=8, r=8, t=12, b=8), height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
                      legend_title_text="", yaxis_title="USD", xaxis_title="")
    fig.update_yaxes(gridcolor="#E9EDF5", zeroline=False)
    st.plotly_chart(fig, use_container_width=True)
with t2:
    st.dataframe(
        time_perf[["Time", "Records", "Conversions", "Revenue", "Ad_Spend", "ROAS"]]
        .rename(columns={"Ad_Spend": "Ad spend", "ROAS": "ROAS"})
        .style.format({"Revenue": "${:,.2f}", "Ad spend": "${:,.2f}", "ROAS": "{:.2f}×", "Conversions": "{:,.0f}"}),
        use_container_width=True, hide_index=True,
    )

st.markdown('<div class="section-label">What this dataset can and cannot tell us</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"**Retention proxy:** {returning_share:.1%} of filtered records are tagged Returning or Loyal. This is a segment mix, not a measured retention or churn rate.")
with c2:
    st.info(f"**Revenue less ad spend:** {money(revenue_less_ads)}. Service delivery, labor, materials, and overhead costs are missing, so net profit and service profitability cannot be calculated.")
with c3:
    st.info("**Channel ROI:** unavailable. There is no marketing-channel field. Time of day is shown as an operational segment and must not be interpreted as a channel.")

with st.expander("Data quality and interpretation"):
    unique_categories = filtered["Service Category"].nunique()
    st.write(
        f"The source contains {len(filtered):,} records in the selected view. It has no client ID or visit history, so individual engagement and churn risk cannot be measured. "
        f"It has {unique_categories:,} distinct Service Category labels in this view; review these source labels before using category-level decisions. "
        "The dashboard uses the supplied Client Type label as a descriptive customer-mix proxy."
    )

st.markdown("---")
with st.expander("View filtered records"):
    st.dataframe(filtered.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    st.download_button("Download filtered CSV", filtered.to_csv(index=False).encode("utf-8-sig"),
                       file_name="fixit_filtered_data.csv", mime="text/csv")
st.caption("FixIt Services · Performance dashboard · Built with Streamlit")

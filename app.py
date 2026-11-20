"""Streamlit dashboard for the restaurant tips dataset used in tips.ipynb.

Run with:  streamlit run app.py
"""

import altair as alt
import pandas as pd
import streamlit as st

import tips_analysis as ta

st.set_page_config(page_title="Restaurant Tips Explorer", page_icon="💵", layout="wide")
METRICS = {"tip": "Tip ($)", "tip_pct": "Tip (% of bill)", "total_bill": "Total bill ($)"}
GROUPS = {"sex": "Sex", "smoker": "Smoker", "day": "Day", "time": "Time", "size": "Party size"}


@st.cache_data
def get_data() -> pd.DataFrame:
    return ta.load_tips()


def p_text(p: float) -> str:
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


try:
    df_all = get_data()
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.title("💵 Restaurant Tips Explorer")
st.caption("Interactive analysis of the Seaborn *tips* dataset: 244 restaurant bills recorded by one waiter.")

with st.sidebar:
    st.header("Filters")
    pick = {c: st.multiselect(GROUPS[c], ta.ORDER[c], default=ta.ORDER[c]) for c in ["day", "time", "sex", "smoker"]}
    size = st.slider("Party size", int(df_all["size"].min()), int(df_all["size"].max()),
                     (int(df_all["size"].min()), int(df_all["size"].max())))

df = df_all[df_all["size"].between(*size)]
for c, vals in pick.items():
    df = df[df[c].isin(vals)]
if df.empty:
    st.warning("No meals match the current filters. Widen the filters in the sidebar.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Meals", len(df))
k2.metric("Average bill", f"${df['total_bill'].mean():.2f}")
k3.metric("Average tip", f"${df['tip'].mean():.2f}")
k4.metric("Average tip rate", f"{df['tip_pct'].mean():.1f}%")

tab_q, tab_rel, tab_cmp, tab_dist, tab_data = st.tabs(
    ["❓ Notebook questions", "📈 Bill vs. tip", "⚖️ Compare groups", "📊 Distributions", "🗂️ Data"])

# ---------------- Notebook questions ----------------
with tab_q:
    st.caption("The three questions asked in the notebook, answered from the currently filtered data.")
    rel = ta.bill_tip_relationship(df)
    sex = ta.compare_groups(df, "sex", "tip")
    sex_pct = ta.compare_groups(df, "sex", "tip_pct")
    size_cmp = ta.compare_groups(df, "size", "tip")

    st.subheader("1. Does the tip increase with the total bill?")
    if rel:
        st.write(f"Correlation r = **{rel['r']:.2f}** ({p_text(rel['p'])}). On average each extra $10 on the bill "
                 f"adds **${rel['slope'] * 10:.2f}** to the tip.")
    else:
        st.write("Not enough meals in the filter.")

    st.subheader("2. Which gender tips more?")
    s = df.groupby("sex", observed=True)[["tip", "tip_pct"]].mean()
    if sex and sex_pct and len(s) == 2:
        st.write(f"Average tip: Male **${s.loc['Male', 'tip']:.2f}**, Female **${s.loc['Female', 'tip']:.2f}** "
                 f"({sex['test']}, {p_text(sex['p'])}). As a share of the bill: Male **{s.loc['Male', 'tip_pct']:.1f}%**, "
                 f"Female **{s.loc['Female', 'tip_pct']:.1f}%** ({p_text(sex_pct['p'])}).")
        if sex["p"] >= 0.05:
            st.info("The difference in average tip is not statistically significant (p ≥ 0.05), and men's larger "
                    "tips mostly follow their larger bills.")
    else:
        st.write("Select both sexes to compare.")

    st.subheader("3. Does the party size affect the tip?")
    if size_cmp:
        st.write(f"{size_cmp['test']}: {p_text(size_cmp['p'])}. Larger parties leave larger tips in dollars because "
                 "their bills are larger. Compare *Tip (% of bill)* by party size in **Compare groups**.")
    st.altair_chart(alt.Chart(ta.group_summary(df, "size", "tip")).mark_bar(color="#2a9d8f").encode(
        x=alt.X("size:O", title="Party size"), y=alt.Y("mean:Q", title="Average tip ($)"),
        tooltip=["size", alt.Tooltip("mean:Q", format="$.2f"), "n"]).properties(height=240), width="stretch")

# ---------------- Bill vs tip ----------------
with tab_rel:
    color = st.selectbox("Colour points by", list(GROUPS), format_func=GROUPS.get, index=3)
    pts = alt.Chart(df).mark_circle(size=60, opacity=0.7).encode(
        x=alt.X("total_bill:Q", title="Total bill ($)"), y=alt.Y("tip:Q", title="Tip ($)"),
        color=alt.Color(f"{color}:N", title=GROUPS[color]),
        tooltip=["total_bill", "tip", alt.Tooltip("tip_pct:Q", format=".1f", title="tip %"), "sex", "smoker", "day", "time", "size"])
    line = pts.transform_regression("total_bill", "tip").mark_line(color="black", strokeDash=[5, 4])
    st.altair_chart((pts + line).properties(height=420), width="stretch")
    if rel:
        st.caption(f"Dashed line: least-squares fit, tip ≈ {rel['intercept']:.2f} + {rel['slope']:.3f} × bill (r = {rel['r']:.2f}).")

# ---------------- Compare groups ----------------
with tab_cmp:
    c1, c2 = st.columns(2)
    by = c1.selectbox("Group by", list(GROUPS), format_func=GROUPS.get)
    metric = c2.selectbox("Measure", list(METRICS), format_func=METRICS.get, index=1)
    summ = ta.group_summary(df, by, metric)
    base = alt.Chart(summ).encode(x=alt.X(f"{by}:N", title=GROUPS[by], sort=ta.ORDER.get(by)))
    bars = base.mark_bar(color="#2a9d8f").encode(y=alt.Y("mean:Q", title=f"Average {METRICS[metric].lower()}"),
                                                  tooltip=[by, alt.Tooltip("mean:Q", format=".2f"), "n"])
    err = base.mark_errorbar(color="black").encode(y=alt.Y("low:Q", title=f"Average {METRICS[metric].lower()}"), y2="high:Q")
    st.altair_chart((bars + err).properties(height=360), width="stretch")
    res = ta.compare_groups(df, by, metric)
    if res:
        verdict = "a statistically significant difference" if res["p"] < 0.05 else "no statistically significant difference"
        st.write(f"**{res['test']}:** {p_text(res['p'])} — {verdict} at the 5% level. Error bars show 95% confidence intervals.")
    else:
        st.caption("Need at least two groups with two or more meals to run a test.")

# ---------------- Distributions ----------------
with tab_dist:
    m = st.radio("Variable", list(METRICS), format_func=METRICS.get, horizontal=True)
    a, b = st.columns(2)
    a.altair_chart(alt.Chart(df).mark_bar(color="#2a9d8f").encode(
        x=alt.X(f"{m}:Q", bin=alt.Bin(maxbins=30), title=METRICS[m]), y=alt.Y("count()", title="Meals")
    ).properties(title="Histogram", height=300), width="stretch")
    b.altair_chart(alt.Chart(df).mark_boxplot(extent=1.5).encode(
        x=alt.X(f"{m}:Q", title=METRICS[m]), y=alt.Y("day:N", sort=ta.ORDER["day"], title=None)
    ).properties(title="By day", height=300), width="stretch")
    corr = df[["total_bill", "tip", "size"]].corr().round(2).reset_index().melt("index")
    heat = alt.Chart(corr).encode(x=alt.X("index:N", title=None), y=alt.Y("variable:N", title=None))
    st.altair_chart((heat.mark_rect().encode(color=alt.Color("value:Q", scale=alt.Scale(scheme="redblue", domain=[-1, 1]),
                                                             title="r"))
                     + heat.mark_text().encode(text="value:Q")).properties(title="Correlation", height=220, width=320))

# ---------------- Data ----------------
with tab_data:
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button("Download filtered data (CSV)", df.to_csv(index=False), "tips_filtered.csv", "text/csv")

# import streamlit as st
# import pandas as pd
# import numpy as np
# import requests
# import plotly.express as px
# from datetime import datetime

# BACKEND_URL = "http://127.0.0.1:8000"

# # -----------------------
# # PAGE CONFIG
# # -----------------------
# st.set_page_config(
#     page_title="Vendor Decision Intelligence Lab",
#     layout="wide"
# )

# # -----------------------
# # SESSION STATE
# # -----------------------
# if "analysis" not in st.session_state:
#     st.session_state.analysis = None
# if "messages" not in st.session_state:
#     st.session_state.messages = []

# # -----------------------
# # HEADER
# # -----------------------
# st.title("Vendor Decision Intelligence Lab")
# st.caption(
#     "This system does **not** recommend vendors. "
#     "It helps you surface assumptions, risks, and trade-offs before decisions."
# )

# st.divider()

# # -----------------------
# # SIDEBAR – UPLOAD
# # -----------------------
# with st.sidebar:
#     st.header("Upload vendor documents")

#     files = st.file_uploader(
#         "CSV / Excel / PDF",
#         type=["csv", "xlsx", "pdf"],
#         accept_multiple_files=True
#     )

#     if st.button("Analyze") and files:
#         with st.spinner("Analyzing documents..."):
#             payload = [("files", (f.name, f.read(), f.type)) for f in files]
#             r = requests.post(f"{BACKEND_URL}/analyze", files=payload)

#             if r.status_code == 200:
#                 st.session_state.analysis = r.json()
#                 st.session_state.messages = []
#                 st.success("Analysis ready")
#             else:
#                 st.error("Analysis failed")

#     if st.button("Reset"):
#         st.session_state.analysis = None
#         st.session_state.messages = []
#         st.rerun()

# # -----------------------
# # LANDING PAGE
# # -----------------------
# if not st.session_state.analysis:
#     st.markdown("""
#     ### How this helps

#     1. Upload vendor quotes or BOMs  
#     2. Review extracted facts  
#     3. Examine assumptions, risks, and trade-offs  
#     4. Ask “what if” questions before negotiation  

#     This tool supports **decision quality**, not decision authority.
#     """)
#     st.stop()

# # -----------------------
# # DATA
# # -----------------------
# result = st.session_state.analysis
# vendor_data = result.get("vendor_data", [])
# analysis = result.get("analysis", {})

# # -----------------------
# # HELPERS
# # -----------------------
# def coerce_numeric(df):
#     for c in df.columns:
#         df[c] = pd.to_numeric(df[c], errors="ignore")
#     return df


# def extract_comparable_df(vendor_data):
#     dfs = {}

#     for item in vendor_data:
#         if item["type"] in ["csv", "excel"] and "sample" in item:
#             df = pd.DataFrame(item["sample"])
#             df = coerce_numeric(df)
#             dfs[item["filename"]] = df

#     if len(dfs) < 2:
#         return None

#     numeric_sets = [
#         set(df.select_dtypes(include="number").columns)
#         for df in dfs.values()
#     ]

#     common_numeric = set.intersection(*numeric_sets)
#     if not common_numeric:
#         return None

#     frames = []
#     for vendor, df in dfs.items():
#         subset = df[list(common_numeric)].copy()
#         subset["_vendor"] = vendor
#         frames.append(subset)

#     return pd.concat(frames, ignore_index=True)


# def plot_comparison(df, metric):
#     counts = df.groupby("_vendor")[metric].count()

#     if counts.min() < 3:
#         agg = df.groupby("_vendor")[metric].mean().reset_index()
#         fig = px.bar(
#             agg,
#             x="_vendor",
#             y=metric,
#             title=f"{metric} (mean per vendor)"
#         )
#     else:
#         fig = px.box(
#             df,
#             x="_vendor",
#             y=metric,
#             title=f"{metric} distribution by vendor"
#         )

#     return fig


# # -----------------------
# # TABS
# # -----------------------
# tabs = st.tabs([
#     "Vendor Facts",
#     "Insights",
#     "Comparisons",
#     "Assumptions & Gaps",
#     "Trade-offs & Risks",
#     "Guided Exploration"
# ])

# # -----------------------
# # TAB 1 – VENDOR FACTS
# # -----------------------
# with tabs[0]:
#     st.header("Vendor facts")

#     for item in vendor_data:
#         with st.expander(item["filename"], expanded=False):

#             if item["type"] in ["csv", "excel"] and "sample" in item:
#                 df = pd.DataFrame(item["sample"])
#                 df = coerce_numeric(df)

#                 st.dataframe(df, use_container_width=True)

#                 numeric_cols = df.select_dtypes(include="number").columns.tolist()
#                 if numeric_cols:
#                     col = st.selectbox(
#                         "Visualize field",
#                         numeric_cols,
#                         key=f"{item['filename']}_field"
#                     )
#                     fig = px.histogram(df, x=col, title=f"{col} distribution")
#                     st.plotly_chart(fig, use_container_width=True)

#             elif item["type"] == "pdf":
#                 st.text_area(
#                     "Extracted text",
#                     item.get("text_preview", "No extractable text"),
#                     height=200
#                 )

# # -----------------------
# # TAB 2 – INSIGHTS
# # -----------------------
# with tabs[1]:
#     st.header("What stands out")

#     insights = analysis.get("insights", [])
#     if insights:
#         for i in insights:
#             st.info(i)
#     else:
#         st.write("No insights generated.")

# # -----------------------
# # TAB 3 – COMPARISONS
# # -----------------------
# with tabs[2]:
#     st.header("Comparable metrics")

#     comp_df = extract_comparable_df(vendor_data)

#     if comp_df is not None:
#         st.dataframe(comp_df, use_container_width=True)

#         metric = st.selectbox(
#             "Compare vendors on",
#             [c for c in comp_df.columns if c != "_vendor"]
#         )

#         fig = plot_comparison(comp_df, metric)
#         st.plotly_chart(fig, use_container_width=True)
#     else:
#         st.info(
#             "No common numeric metrics found across vendors. "
#             "Any comparison would require assumptions."
#         )

# # -----------------------
# # TAB 4 – ASSUMPTIONS & GAPS
# # -----------------------
# with tabs[3]:
#     col1, col2 = st.columns(2)

#     with col1:
#         st.subheader("Assumptions")
#         for a in analysis.get("assumptions", []):
#             st.warning(a)

#     with col2:
#         st.subheader("Missing information")
#         for m in analysis.get("missing_information", []):
#             st.error(m)

# # -----------------------
# # TAB 5 – TRADE-OFFS & RISKS
# # -----------------------
# with tabs[4]:
#     st.header("Trade-offs and risks")

#     for t in analysis.get("tradeoffs", []):
#         st.markdown(f"- **Trade-off:** {t}")

#     for r in analysis.get("risks", []):
#         st.markdown(f"- **Risk:** {r}")

# # -----------------------
# # TAB 6 – GUIDED EXPLORATION
# # -----------------------
# with tabs[5]:
#     st.header("Guided exploration")

#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     q = st.chat_input("Ask about risks, assumptions, or trade-offs")

#     if q:
#         st.session_state.messages.append({"role": "user", "content": q})

#         r = requests.post(f"{BACKEND_URL}/chat", json={"question": q})
#         reply = r.json().get("reply", "No response")

#         st.session_state.messages.append({"role": "assistant", "content": reply})
#         st.rerun()

# # -----------------------
# # FOOTER
# # -----------------------
# st.divider()
# # st.caption("Decision intelligence supports clarity — not automation.")

##app.py(frontend-streamlit)
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os

BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL environment variable is not set")
    st.stop()


# BACKEND_URL = "http://127.0.0.1:8000"

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Vendor Decision Intelligence Lab",
    layout="wide"
)

# -----------------------
# SESSION STATE
# -----------------------
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------
# HEADER
# -----------------------
st.title("Vendor Decision Intelligence Lab")
st.caption(
    "This system does **not** recommend vendors. "
    "It helps surface facts, assumptions, risks, and trade-offs before decisions."
)
st.divider()

# -----------------------
# SIDEBAR – UPLOAD
# -----------------------
with st.sidebar:
    st.header("Upload vendor documents")

    files = st.file_uploader(
        "CSV / Excel / PDF",
        type=["csv", "xlsx", "pdf"],
        accept_multiple_files=True
    )

    if st.button("Analyze") and files:
        with st.spinner("Analyzing documents..."):
            payload = [("files", (f.name, f.read(), f.type)) for f in files]
            r = requests.post(f"{BACKEND_URL}/analyze", files=payload)

            if r.status_code == 200:
                st.session_state.analysis = r.json()
                st.session_state.messages = []
                st.success("Analysis ready")
            else:
                st.error("Analysis failed")

    if st.button("Reset"):
        st.session_state.analysis = None
        st.session_state.messages = []
        st.rerun()

# -----------------------
# LANDING PAGE
# -----------------------
if not st.session_state.analysis:
    st.markdown("""
    ### How this helps

    1. Upload vendor quotes or BOMs  
    2. Extract **facts** from documents  
    3. Examine assumptions, risks, and trade-offs  
    4. Ask “what if” questions before negotiation  

    This tool supports **decision quality**, not decision authority.
    """)
    st.stop()

# -----------------------
# DATA
# -----------------------
result = st.session_state.analysis
facts = result.get("facts", [])
analysis = result.get("analysis", {})
vendor_data = result.get("vendor_data", [])

# -----------------------
# HELPERS
# -----------------------
def plot_facts_dashboard(facts):
    charts = []

    df = pd.DataFrame(facts)
    if df.empty:
        return charts

    # only numeric values
    df["value_numeric"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value_numeric"])

    for attr in df["attribute"].unique():
        subset = df[df["attribute"] == attr]

        if subset["entity_name"].nunique() < 2:
            continue

        fig = px.bar(
            subset,
            x="entity_name",
            y="value_numeric",
            title=f"{attr.replace('_', ' ').title()} by Vendor",
            labels={
                "entity_name": "Vendor",
                "value_numeric": attr.replace("_", " ").title()
            }
        )

        charts.append(fig)

    return charts

# -----------------------
# TABS
# -----------------------
tabs = st.tabs([
    "Dashboard",
    "Facts",
    "Insights",
    "Assumptions & Gaps",
    "Trade-offs & Risks",
    "Guided Exploration",
    "Source Documents"
])

# -----------------------
# TAB 1 – DASHBOARD
# -----------------------
with tabs[0]:
    st.header("Decision dashboard")
    st.caption(
        "Charts are generated from **extracted facts**, "
        "not directly from documents."
    )

    if not facts:
        st.info("No structured facts available for visualization.")
    else:
        charts = plot_facts_dashboard(facts)

        if not charts:
            st.info(
                "Facts were extracted, but not enough comparable numeric "
                "information is available to plot."
            )
        else:
            for fig in charts:
                st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TAB 2 – FACTS
# -----------------------
with tabs[1]:
    st.header("Extracted facts")

    if not facts:
        st.info("No facts extracted.")
    else:
        st.dataframe(pd.DataFrame(facts), use_container_width=True)

# -----------------------
# TAB 3 – INSIGHTS
# -----------------------
with tabs[2]:
    st.header("What stands out")

    insights = analysis.get("insights", [])
    if insights:
        for i in insights:
            st.info(i)
    else:
        st.write("No insights generated.")

# -----------------------
# TAB 4 – ASSUMPTIONS & GAPS
# -----------------------
with tabs[3]:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Assumptions")
        for a in analysis.get("assumptions", []):
            st.warning(a)

    with col2:
        st.subheader("Missing information")
        for m in analysis.get("missing_information", []):
            st.error(m)

# -----------------------
# TAB 5 – TRADE-OFFS & RISKS
# -----------------------
with tabs[4]:
    st.header("Trade-offs and risks")

    for t in analysis.get("tradeoffs", []):
        st.markdown(f"- **Trade-off:** {t}")

    for r in analysis.get("risks", []):
        st.markdown(f"- **Risk:** {r}")

# -----------------------
# TAB 6 – GUIDED EXPLORATION
# -----------------------
with tabs[5]:
    st.header("Guided exploration")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    q = st.chat_input("Ask about risks, assumptions, or trade-offs")

    if q:
        st.session_state.messages.append({"role": "user", "content": q})

        r = requests.post(f"{BACKEND_URL}/chat", json={"question": q})
        reply = r.json().get("reply", "No response")

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# -----------------------
# TAB 7 – SOURCE DOCUMENTS
# -----------------------
with tabs[6]:
    st.header("Source documents")

    for item in vendor_data:
        with st.expander(item.get("filename", "Document")):
            if item.get("type") == "pdf":
                st.text_area(
                    "Extracted text",
                    item.get("text_preview", "No extractable text"),
                    height=200
                )
            else:
                if "sample" in item:
                    st.dataframe(
                        pd.DataFrame(item["sample"]),
                        use_container_width=True
                    )

# -----------------------
# FOOTER
# -----------------------
st.divider()

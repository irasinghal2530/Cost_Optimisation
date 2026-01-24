##app.py
# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import requests
# import os
# from dotenv import load_dotenv

# # -----------------------
# # Load env
# # -----------------------
# load_dotenv()
# BACKEND_URL = os.getenv("BACKEND_URL")

# if not BACKEND_URL:
#     st.error("BACKEND_URL is not set in environment variables.")
#     st.stop()

# # -----------------------
# # Page config
# # -----------------------
# st.set_page_config(
#     page_title="Vendor Decision Intelligence Lab",
#     layout="wide"
# )

# # -----------------------
# # Session state
# # -----------------------
# st.session_state.setdefault("analysis", None)
# st.session_state.setdefault("messages", [])
# st.session_state.setdefault("analysis_in_flight", False)
# st.session_state.setdefault("chat_in_flight", False)

# # -----------------------
# # Header
# # -----------------------
# st.title("Vendor Decision Intelligence Lab")
# st.caption(
#     "This system does **not** recommend vendors. "
#     "It surfaces facts, assumptions, risks, and trade-offs."
# )
# st.divider()

# # -----------------------
# # Sidebar – Upload
# # -----------------------
# with st.sidebar:
#     st.header("Upload vendor documents")

#     files = st.file_uploader(
#         "CSV / Excel / PDF",
#         type=["csv", "xlsx", "pdf"],
#         accept_multiple_files=True
#     )

#     analyze_clicked = st.button(
#         "Analyze",
#         disabled=st.session_state.analysis_in_flight or not files
#     )

#     if analyze_clicked:
#         st.session_state.analysis_in_flight = True

#         with st.spinner("Analyzing documents..."):
#             try:
#                 payload = [("files", (f.name, f.read(), f.type)) for f in files]

#                 r = requests.post(
#                     f"{BACKEND_URL}/analyze",
#                     files=payload,
#                     timeout=60
#                 )

#                 if r.status_code == 200:
#                     st.session_state.analysis = r.json()
#                     st.session_state.messages = []

#                     # ✅ Seed the chat for smooth UX
#                     st.session_state.messages.append({
#                         "role": "assistant",
#                         "content": (
#                             "I’ve reviewed the uploaded documents. "
#                             "I can help you explore risks, assumptions, and trade-offs "
#                             "without recommending any vendor. "
#                             "What would you like to examine first?"
#                         )
#                     })

#                     st.success("Analysis ready")
#                 else:
#                     st.error(f"Analysis failed ({r.status_code})")

#             except Exception as e:
#                 st.error(f"Backend error: {e}")

#             finally:
#                 st.session_state.analysis_in_flight = False

#     if st.button("Reset"):
#         st.session_state.analysis = None
#         st.session_state.messages = []
#         st.session_state.analysis_in_flight = False
#         st.session_state.chat_in_flight = False

# # -----------------------
# # Landing page
# # -----------------------
# if not st.session_state.analysis:
#     st.markdown("""
#     ### How this helps
#     1. Upload vendor documents  
#     2. Extract structured facts  
#     3. Surface assumptions, risks, and trade-offs  
#     4. Ask decision-quality questions
#     """)
#     st.stop()

# # -----------------------
# # Extract data
# # -----------------------
# result = st.session_state.analysis
# facts = result.get("facts", [])
# analysis = result.get("analysis", {})
# vendor_data = result.get("vendor_data", [])

# # -----------------------
# # Helper: unwrap LLM output
# # -----------------------
# def extract_text(item):
#     if isinstance(item, dict):
#         return next(iter(item.values()))
#     return item

# # -----------------------
# # Helper: plots
# # -----------------------
# def plot_facts_dashboard(facts):
#     df = pd.DataFrame(facts)
#     if df.empty:
#         return []

#     df["value_numeric"] = pd.to_numeric(df["value"], errors="coerce")
#     df = df.dropna(subset=["value_numeric"])

#     charts = []
#     for attr in df["attribute"].unique():
#         subset = df[df["attribute"] == attr]
#         if subset["entity_name"].nunique() < 2:
#             continue

#         charts.append(
#             px.bar(
#                 subset,
#                 x="entity_name",
#                 y="value_numeric",
#                 title=f"{attr.replace('_',' ').title()} by Vendor",
#                 labels={
#                     "entity_name": "Vendor",
#                     "value_numeric": attr.replace("_", " ").title()
#                 }
#             )
#         )
#     return charts

# # -----------------------
# # Tabs
# # -----------------------
# tabs = st.tabs([
#     "Dashboard",
#     "Facts",
#     "Insights",
#     "Assumptions & Gaps",
#     "Trade-offs & Risks",
#     "Guided Exploration",
#     "Source Documents"
# ])

# # -----------------------
# # Dashboard
# # -----------------------
# with tabs[0]:
#     st.header("Decision dashboard")
#     charts = plot_facts_dashboard(facts)
#     if not charts:
#         st.info("Not enough comparable numeric data to plot.")
#     else:
#         for fig in charts:
#             st.plotly_chart(fig, use_container_width=True)

# # -----------------------
# # Facts
# # -----------------------
# with tabs[1]:
#     st.header("Extracted facts")
#     if facts:
#         st.dataframe(pd.DataFrame(facts), use_container_width=True)
#     else:
#         st.info("No structured facts extracted.")

# # -----------------------
# # Insights
# # -----------------------
# with tabs[2]:
#     st.header("What stands out")
#     for i in analysis.get("insights", []):
#         st.info(extract_text(i))

# # -----------------------
# # Assumptions & Gaps
# # -----------------------
# with tabs[3]:
#     col1, col2 = st.columns(2)
#     with col1:
#         st.subheader("Assumptions")
#         for a in analysis.get("assumptions", []):
#             st.warning(extract_text(a))
#     with col2:
#         st.subheader("Missing information")
#         for m in analysis.get("missing_information", []):
#             st.error(extract_text(m))

# # -----------------------
# # Trade-offs & Risks
# # -----------------------
# with tabs[4]:
#     st.header("Trade-offs and risks")
#     for t in analysis.get("tradeoffs", []):
#         st.markdown(f"- **Trade-off:** {extract_text(t)}")
#     for r in analysis.get("risks", []):
#         st.markdown(f"- **Risk:** {extract_text(r)}")

# # -----------------------
# # Guided Exploration (CHAT)
# # -----------------------
# with tabs[5]:
#     st.header("Guided exploration")

#     for msg in st.session_state.messages:
#         with st.chat_message(msg["role"]):
#             st.markdown(msg["content"])

#     q = st.chat_input("Ask about risks, assumptions, or trade-offs")

#     if q and not st.session_state.chat_in_flight:
#         st.session_state.chat_in_flight = True

#         try:
#             r = requests.post(
#                 f"{BACKEND_URL}/chat",
#                 json={
#                     "question": q,
#                     # ✅ lighter, faster context
#                     "context": {
#                         "facts": facts,
#                         "analysis": analysis
#                     }
#                 },
#                 timeout=45
#             )

#             reply = (
#                 r.json().get("reply", "No response")
#                 if r.status_code == 200
#                 else f"Backend error ({r.status_code})"
#             )

#             st.session_state.messages.extend([
#                 {"role": "user", "content": q},
#                 {"role": "assistant", "content": reply}
#             ])

#         except Exception as e:
#             st.error(f"Chat failed: {e}")

#         finally:
#             st.session_state.chat_in_flight = False

# # -----------------------
# # Source Documents
# # -----------------------
# with tabs[6]:
#     st.header("Source documents")
#     for item in vendor_data:
#         with st.expander(item.get("filename", "Document")):
#             if item.get("type") == "pdf":
#                 st.text_area(
#                     "Extracted text",
#                     item.get("text_preview", ""),
#                     height=200
#                 )
#             elif "sample" in item:
#                 st.dataframe(
#                     pd.DataFrame(item["sample"]),
#                     use_container_width=True
#                 )

# st.divider()


##app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv

# -----------------------
# Load env
# -----------------------
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL")

if not BACKEND_URL:
    st.error("BACKEND_URL is not set in environment variables.")
    st.stop()

# -----------------------
# Page config
# -----------------------
st.set_page_config(
    page_title="Vendor Decision Intelligence Lab",
    layout="wide"
)

# -----------------------
# Session state
# -----------------------
st.session_state.setdefault("analysis", None)
st.session_state.setdefault("messages", [])
st.session_state.setdefault("analysis_in_flight", False)
st.session_state.setdefault("chat_in_flight", False)

# -----------------------
# Header
# -----------------------
st.title("Vendor Decision Intelligence Lab")
st.caption(
    "This system does **not** recommend vendors. "
    "It surfaces facts, assumptions, risks, and trade-offs."
)
st.divider()

# -----------------------
# Sidebar – Upload
# -----------------------
with st.sidebar:
    st.header("Upload vendor documents")

    files = st.file_uploader(
        "CSV / Excel / PDF",
        type=["csv", "xlsx", "pdf"],
        accept_multiple_files=True
    )

    analyze_clicked = st.button(
        "Analyze",
        disabled=st.session_state.analysis_in_flight or not files
    )

    if analyze_clicked:
        st.session_state.analysis_in_flight = True

        with st.spinner("Analyzing documents..."):
            try:
                payload = [("files", (f.name, f.read(), f.type)) for f in files]

                r = requests.post(
                    f"{BACKEND_URL}/analyze",
                    files=payload,
                    timeout=60
                )

                if r.status_code == 200:
                    st.session_state.analysis = r.json()
                    st.session_state.messages = []

                    # ✅ Seed chat (prevents cold start)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": (
                            "I’ve reviewed the uploaded documents. "
                            "I can help you explore risks, assumptions, and trade-offs "
                            "without recommending vendors. "
                            "What would you like to examine first?"
                        )
                    })

                    st.success("Analysis ready")
                else:
                    st.error(f"Analysis failed ({r.status_code})")

            except Exception as e:
                st.error(f"Backend error: {e}")

            finally:
                st.session_state.analysis_in_flight = False

    if st.button("Reset"):
        st.session_state.analysis = None
        st.session_state.messages = []
        st.session_state.analysis_in_flight = False
        st.session_state.chat_in_flight = False

# -----------------------
# Landing page
# -----------------------
if not st.session_state.analysis:
    st.markdown("""
    ### How this helps
    1. Upload vendor documents  
    2. Extract structured facts  
    3. Surface assumptions, risks, and trade-offs  
    4. Ask decision-quality questions
    """)
    st.stop()

# -----------------------
# Extract data
# -----------------------
result = st.session_state.analysis
facts = result.get("facts", [])
analysis = result.get("analysis", {})
vendor_data = result.get("vendor_data", [])

# -----------------------
# Helper: unwrap LLM output
# -----------------------
def extract_text(item):
    if isinstance(item, dict):
        return next(iter(item.values()))
    return item

# -----------------------
# Helper: plots
# -----------------------
def plot_facts_dashboard(facts):
    df = pd.DataFrame(facts)
    if df.empty:
        return []

    df["value_numeric"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value_numeric"])

    charts = []
    for attr in df["attribute"].unique():
        subset = df[df["attribute"] == attr]
        if subset["entity_name"].nunique() < 2:
            continue

        charts.append(
            px.bar(
                subset,
                x="entity_name",
                y="value_numeric",
                title=f"{attr.replace('_',' ').title()} by Vendor",
                labels={
                    "entity_name": "Vendor",
                    "value_numeric": attr.replace("_", " ").title()
                }
            )
        )
    return charts

# -----------------------
# Tabs
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
# Dashboard
# -----------------------
with tabs[0]:
    st.header("Decision dashboard")
    charts = plot_facts_dashboard(facts)

    if not charts:
        st.info("Not enough comparable numeric data to plot.")
    else:
        for fig in charts:
            st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Facts
# -----------------------
with tabs[1]:
    st.header("Extracted facts")
    if facts:
        st.dataframe(pd.DataFrame(facts), use_container_width=True)
    else:
        st.info("No structured facts extracted.")

# -----------------------
# Insights
# -----------------------
with tabs[2]:
    st.header("What stands out")
    for i in analysis.get("insights", []):
        st.info(extract_text(i))

# -----------------------
# Assumptions & Gaps
# -----------------------
with tabs[3]:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Assumptions")
        for a in analysis.get("assumptions", []):
            st.warning(extract_text(a))
    with col2:
        st.subheader("Missing information")
        for m in analysis.get("missing_information", []):
            st.error(extract_text(m))

# -----------------------
# Trade-offs & Risks
# -----------------------
with tabs[4]:
    st.header("Trade-offs and risks")
    for t in analysis.get("tradeoffs", []):
        st.markdown(f"- **Trade-off:** {extract_text(t)}")
    for r in analysis.get("risks", []):
        st.markdown(f"- **Risk:** {extract_text(r)}")

# -----------------------
# Guided Exploration (CHAT)
# -----------------------
with tabs[5]:
    st.header("Guided exploration")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    q = st.chat_input("Ask about risks, assumptions, or trade-offs")

    if q and not st.session_state.chat_in_flight:
        st.session_state.chat_in_flight = True

        # ✅ DISTILLED CONTEXT (prevents overload & lag)
        chat_context = {
            "facts": facts,
            "insights": analysis.get("insights", []),
            "assumptions": analysis.get("assumptions", []),
            "risks": analysis.get("risks", []),
            "tradeoffs": analysis.get("tradeoffs", [])
        }

        try:
            r = requests.post(
                f"{BACKEND_URL}/chat",
                json={
                    "question": (
                        f"{q}\n\n"
                        "Answer crisply in 4–6 bullet points. "
                        "If the question is ambiguous, ask one clarifying question."
                    ),
                    "context": chat_context
                },
                timeout=45
            )

            reply = (
                r.json().get("reply", "No response")
                if r.status_code == 200
                else f"Backend error ({r.status_code})"
            )

            st.session_state.messages.extend([
                {"role": "user", "content": q},
                {"role": "assistant", "content": reply}
            ])

            # ✅ FIXES ONE-QUESTION LAG
            st.rerun()

        except Exception as e:
            st.error(f"Chat failed: {e}")

        finally:
            st.session_state.chat_in_flight = False

# -----------------------
# Source Documents
# -----------------------
with tabs[6]:
    st.header("Source documents")
    for item in vendor_data:
        with st.expander(item.get("filename", "Document")):
            if item.get("type") == "pdf":
                st.text_area(
                    "Extracted text",
                    item.get("text_preview", ""),
                    height=200
                )
            elif "sample" in item:
                st.dataframe(
                    pd.DataFrame(item["sample"]),
                    use_container_width=True
                )

st.divider()

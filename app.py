from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from supabase import Client, create_client


st.set_page_config(
    page_title="FocusLab | Student Digital Habits",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLORS = {
    "navy": "#16324F",
    "teal": "#246A73",
    "orange": "#E39B55",
    "ink": "#243447",
    "muted": "#617386",
    "surface": "#FFFFFF",
    "border": "#DCE6ED",
}


def apply_styles() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(180deg, #F2F6FA 0%, #FFFFFF 48%);
            color: {COLORS["ink"]};
        }}
        .block-container {{
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}
        .hero {{
            background: linear-gradient(120deg, {COLORS["navy"]}, {COLORS["teal"]});
            padding: 2rem 2.1rem;
            border-radius: 20px;
            color: #FFFFFF;
            margin-bottom: 1.25rem;
        }}
        .hero h1 {{ color: #FFFFFF; margin: 0 0 .45rem 0; }}
        .hero p {{ color: #E5F3F4; margin: 0; font-size: 1.05rem; }}
        div[data-testid="stForm"] {{
            background: {COLORS["surface"]};
            border: 1px solid {COLORS["border"]};
            padding: 1.35rem;
            border-radius: 16px;
        }}
        div[data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid {COLORS["border"]};
            padding: 1rem;
            border-radius: 14px;
        }}
        div[data-testid="stFormSubmitButton"] button,
        .stButton button[kind="primary"] {{
            background: {COLORS["teal"]};
            border-color: {COLORS["teal"]};
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_supabase_credentials() -> tuple[str, str]:
    """Read public client credentials from Streamlit secrets."""
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = (
        st.secrets.get("SUPABASE_ANON_KEY", "")
        or st.secrets.get("SUPABASE_KEY", "")
    ).strip()

    if not url or not key:
        raise RuntimeError(
            "Supabase credentials are missing. Add SUPABASE_URL and "
            "SUPABASE_ANON_KEY to Streamlit secrets."
        )

    return url, key


@st.cache_resource
def get_supabase(url: str, key: str) -> Client:
    return create_client(url, key)


@st.cache_data(ttl=30, show_spinner=False)
def load_stats(url: str, key: str) -> dict[str, Any]:
    """Load aggregated statistics only; individual submissions stay private."""
    response = get_supabase(url, key).rpc("get_survey_stats").execute()
    data = response.data

    if isinstance(data, list) and data:
        data = data[0]

    if not isinstance(data, dict):
        raise RuntimeError("The statistics function returned an unexpected response.")

    return data


def make_count_frame(values: Any, label_name: str) -> pd.DataFrame:
    if not isinstance(values, dict):
        values = {}
    frame = pd.DataFrame(
        [{"Answer": str(label), "Responses": int(count or 0)}
         for label, count in values.items()]
    )
    if frame.empty:
        return pd.DataFrame(columns=["Answer", "Responses"])
    return frame.sort_values("Responses", ascending=False)


def render_analytics(stats: dict[str, Any]) -> None:
    total = int(stats.get("total_responses") or 0)
    avg_focus = stats.get("average_focus_score")
    avg_age = stats.get("average_age")
    notification_counts = stats.get("notification_counts") or {}
    phone_time_counts = stats.get("phone_time_counts") or {}

    first, second, third = st.columns(3)
    first.metric("Total responses", f"{total:,}")
    second.metric(
        "Average focus score",
        f"{float(avg_focus):.1f} / 10" if avg_focus is not None else "—",
    )
    third.metric(
        "Average age",
        f"{float(avg_age):.1f}" if avg_age is not None else "—",
    )

    left, right = st.columns(2)

    with left:
        frame = make_count_frame(notification_counts, "Notification frequency")
        if not frame.empty:
            figure = px.bar(
                frame,
                x="Answer",
                y="Responses",
                title="How often notifications interrupt study",
                color_discrete_sequence=[COLORS["teal"]],
            )
            figure.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_color=COLORS["ink"],
                xaxis_title=None,
                yaxis_title="Responses",
                margin=dict(l=10, r=10, t=55, b=10),
            )
            st.plotly_chart(figure, use_container_width=True)
        else:
            st.info("No notification data yet.")

    with right:
        frame = make_count_frame(phone_time_counts, "Daily phone time")
        if not frame.empty:
            figure = px.bar(
                frame,
                x="Answer",
                y="Responses",
                title="Daily smartphone screen time",
                color_discrete_sequence=[COLORS["orange"]],
            )
            figure.update_layout(
                plot_bgcolor="white",
                paper_bgcolor="white",
                font_color=COLORS["ink"],
                xaxis_title=None,
                yaxis_title="Responses",
                margin=dict(l=10, r=10, t=55, b=10),
            )
            st.plotly_chart(figure, use_container_width=True)
        else:
            st.info("No screen-time data yet.")


def main() -> None:
    apply_styles()

    st.markdown(
        """
        <section class="hero">
            <h1>🎯 FocusLab</h1>
            <p>Student digital habits and study concentration survey</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        "This anonymous student survey explores how smartphone use, "
        "notifications and study routines relate to perceived concentration. "
        "It takes about two minutes. Please do not include names or contact details."
    )
    st.caption("Academic portfolio project · Voluntary participation · Anonymous survey")

    try:
        url, key = get_supabase_credentials()
        database = get_supabase(url, key)
        database_ready = True
    except Exception as exc:
        database_ready = False
        database_error = str(exc)

    if database_ready:
        st.success("Database connection configured.")
    else:
        st.warning("The survey database is not configured yet.")
        with st.expander("Setup details"):
            st.code(database_error)

    with st.form("focus_survey", clear_on_submit=True):
        st.subheader("About your study habits")
        left, right = st.columns(2)

        with left:
            age = st.number_input("Your age", min_value=14, max_value=80, value=19, step=1)
            course = st.selectbox(
                "Current study year",
                ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5 or above", "Not currently studying"],
            )
            phone_time = st.select_slider(
                "How much time do you spend on your smartphone each day?",
                options=["Less than 1 hour", "1–2 hours", "3–4 hours", "5–6 hours", "7 hours or more"],
            )
            notifications = st.radio(
                "How often do notifications distract you while studying?",
                ["Never", "Rarely", "Sometimes", "Often", "Very often"],
            )

        with right:
            focus_score = st.slider(
                "How easy is it for you to concentrate on a study task?",
                min_value=1,
                max_value=10,
                value=6,
                help="1 = very difficult; 10 = very easy",
            )
            phone_during_study = st.radio(
                "What do you usually do with your phone while studying?",
                [
                    "Put it away and do not check it",
                    "Check it occasionally",
                    "Get distracted by it frequently",
                    "Use it for study-related tasks",
                ],
            )
            study_session = st.selectbox(
                "How long is your usual uninterrupted study session?",
                ["Under 15 minutes", "15–30 minutes", "31–45 minutes", "46–60 minutes", "More than an hour"],
            )
            break_frequency = st.selectbox(
                "How often do you take breaks during independent study?",
                [
                    "Every 15–20 minutes",
                    "Every 30–45 minutes",
                    "About once an hour",
                    "When I feel tired",
                    "Almost never",
                ],
            )

        distractions = st.multiselect(
            "What most often makes it difficult to concentrate?",
            [
                "Notifications and messages",
                "Social media",
                "Videos and games",
                "Background noise",
                "Fatigue",
                "Difficult study material",
                "Personal matters",
                "None of the above",
            ],
        )
        focus_tips = st.text_area(
            "What helps you concentrate better? (optional)",
            max_chars=500,
            placeholder="Share a tip or leave this field blank.",
        )
        submitted = st.form_submit_button(
            "Submit anonymous response",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not database_ready:
            st.error("Your response was not saved because the database is unavailable.")
        else:
            answer = {
                "age": int(age),
                "course": course,
                "daily_phone_time": phone_time,
                "notification_distraction": notifications,
                "focus_score": int(focus_score),
                "phone_during_study": phone_during_study,
                "study_session": study_session,
                "break_frequency": break_frequency,
                "distractions": distractions,
                "focus_tips": focus_tips.strip(),
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                database.table("survey_responses").insert(
                    {"answers": answer}
                ).execute()
                load_stats.clear()
                st.success("Thank you! Your anonymous response has been saved.")
            except Exception:
                st.error(
                    "We could not save your response. Check the Supabase table "
                    "and anonymous INSERT policy in the setup guide."
                )

    st.divider()
    st.subheader("📊 Community insights")
    st.caption(
        "Only aggregated statistics are displayed. Individual answers and "
        "free-text comments are not exposed on this page."
    )

    if database_ready:
        try:
            with st.spinner("Loading aggregated results…"):
                stats = load_stats(url, key)
            response_count = int(stats.get("total_responses") or 0)
            if response_count == 0:
                st.info("There are no responses yet. Submit the survey to start the dataset.")
            elif response_count < 5:
                st.info(
                    "Aggregate insights will appear after at least five responses "
                    "have been collected, to help protect participant privacy."
                )
            else:
                render_analytics(stats)
        except Exception:
            st.error(
                "Analytics are not available. Follow the Supabase SQL setup "
                "instructions in the README to create the statistics function."
            )

    st.caption(
        "FocusLab is an educational survey, not a clinically validated "
        "assessment of attention or productivity."
    )


if __name__ == "__main__":
    main()

"""
AgroSense AI - Chat History & Session Manager View
Browse all saved chat sessions, replay transcripts, search by keyword,
export full sessions as JSON or Markdown, and resume historical sessions.
"""

import streamlit as st
import json
from datetime import datetime
from src.database.db import get_db_connection, clear_chat_history, get_chat_history
from src.ui.components import render_section_header, render_metric, navigate_to


def _fetch_all_sessions():
    """Returns all distinct session IDs with metadata."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT session_id,
                       COUNT(*) as message_count,
                       MIN(timestamp) as started_at,
                       MAX(timestamp) as last_active,
                       SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) as user_turns
                FROM chat_history
                GROUP BY session_id
                ORDER BY MAX(timestamp) DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def _fetch_session_messages(session_id: str):
    """Returns full message history for a specific session."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, role, content, sources_json, timestamp
                FROM chat_history
                WHERE session_id = ?
                ORDER BY id ASC
                """,
                (session_id,)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def _export_session_markdown(session_id: str, messages: list) -> str:
    """Converts a chat session to Markdown format."""
    lines = [
        f"# AgroSense AI — Chat Session Export",
        f"**Session ID:** `{session_id}`",
        f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        ""
    ]
    for msg in messages:
        role_label = "🧑‍🌾 **Farmer / User**" if msg["role"] == "user" else "🌱 **AgroSense AI**"
        ts = msg.get("timestamp", "")
        lines.append(f"### {role_label} ({ts})")
        lines.append(msg["content"])
        lines.append("")
        try:
            sources = json.loads(msg.get("sources_json", "[]"))
            if sources:
                lines.append("**📚 Verified Sources:**")
                for s in sources:
                    lines.append(f"- [{s.get('id','')}] **{s.get('title','')}** — `{s.get('source','')}` (Score: {s.get('relevance_score','')})")
        except Exception:
            pass
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def render_history_view():
    """Renders the chat history browser and session manager."""
    st.subheader("🗂️ Chat History & Session Manager")
    st.caption("Browse all saved agronomic advisory conversations, replay transcripts, and resume past sessions.")

    sessions = _fetch_all_sessions()

    # ── Top KPIs ─────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric("Total Sessions", len(sessions), "Unique conversation threads", "💬")
    with col2:
        total_msgs = sum(s["message_count"] for s in sessions)
        render_metric("Total Messages", total_msgs, "Across all sessions", "📝")
    with col3:
        total_turns = sum(s["user_turns"] for s in sessions)
        render_metric("Farmer Inquiries", total_turns, "Questions answered by AI", "❓")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    if not sessions:
        st.info(
            "📂 **No saved sessions found.** Start a conversation in the **💬 AI Assistant** tab — "
            "all exchanges are automatically persisted here in SQLite."
        )
        return

    # ── Search & Filter ──────────────────────────────────────────────
    render_section_header("Saved Sessions Directory", "🔍")
    scol_a, scol_b = st.columns([3, 1])
    with scol_a:
        search_term = st.text_input(
            "Search transcripts by keyword",
            placeholder="e.g. 'wheat rust', 'soil pH', 'stem borer'..."
        )
    with scol_b:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🗑️ Clear All History", type="secondary", use_container_width=True):
            clear_chat_history()
            st.session_state["chat_messages"] = []
            st.success("All chat history wiped successfully.")
            st.rerun()

    # ── Session List ─────────────────────────────────────────────────
    for session in sessions:
        sid = session["session_id"]
        msg_count = session["message_count"]
        user_turns = session["user_turns"]
        started = session.get("started_at", "")[:16] if session.get("started_at") else ""
        last_active = session.get("last_active", "")[:16] if session.get("last_active") else ""

        msgs = _fetch_session_messages(sid)
        first_question = ""
        for m in msgs:
            if m["role"] == "user":
                first_question = m["content"][:90] + ("..." if len(m["content"]) > 90 else "")
                break

        # Apply keyword search filter
        if search_term:
            full_text = " ".join(m["content"] for m in msgs).lower()
            if search_term.lower() not in full_text:
                continue

        with st.expander(
            f"💬 Session `{sid}` — {user_turns} Q&As · {msg_count} msgs · Last: {last_active}",
            expanded=False
        ):
            if first_question:
                st.caption(f"📌 **Initial Query:** *\"{first_question}\"*")

            st.markdown(
                f"**Started:** `{started}` &nbsp;|&nbsp; "
                f"**Total Exchanges:** `{msg_count}` &nbsp;|&nbsp; "
                f"**Inquiries:** `{user_turns}`"
            )
            st.markdown("")

            # Action buttons row
            act_col1, act_col2, act_col3, act_col4 = st.columns([1.3, 1, 1, 1])

            with act_col1:
                if st.button("▶️ Resume in AI Assistant", key=f"resume_{sid}", type="primary", use_container_width=True):
                    st.session_state["session_id"] = sid
                    st.session_state["chat_messages"] = get_chat_history(sid)
                    navigate_to("💬 AI Assistant")

            with act_col2:
                if st.button("🗑️ Delete Session", key=f"del_{sid}", use_container_width=True):
                    clear_chat_history(sid)
                    if st.session_state.get("session_id") == sid:
                        st.session_state["chat_messages"] = []
                    st.success(f"Session `{sid}` deleted.")
                    st.rerun()

            with act_col3:
                json_export = json.dumps(msgs, indent=2, default=str)
                st.download_button(
                    "📥 JSON",
                    data=json_export,
                    file_name=f"agrosense_{sid}.json",
                    mime="application/json",
                    key=f"json_{sid}",
                    use_container_width=True
                )

            with act_col4:
                md_export = _export_session_markdown(sid, msgs)
                st.download_button(
                    "📥 Markdown",
                    data=md_export,
                    file_name=f"agrosense_{sid}.md",
                    mime="text/markdown",
                    key=f"md_{sid}",
                    use_container_width=True
                )

            # Transcript accordion inside session card
            st.markdown("---")
            st.markdown("#### 📄 Conversation Transcript")
            for msg in msgs:
                role = msg["role"]
                avatar = "🧑‍🌾" if role == "user" else "🌱"
                ts = msg.get("timestamp", "")

                with st.chat_message(role, avatar=avatar):
                    st.markdown(msg["content"])
                    st.caption(f"🕐 {ts}")

                    try:
                        sources = json.loads(msg.get("sources_json", "[]") or "[]")
                        if sources and role == "assistant":
                            with st.expander(f"📚 Sources Cited ({len(sources)})"):
                                for s in sources:
                                    st.markdown(
                                        f"**[{s.get('id','')}] {s.get('title','')}** — "
                                        f"`{s.get('source','')}` "
                                        f"<span class='badge-optimal'>Relevance: {s.get('relevance_score', 'N/A')}</span>",
                                        unsafe_allow_html=True
                                    )
                                    if s.get("snippet"):
                                        st.caption(f'Excerpt: "{s["snippet"][:200]}..."')
                    except Exception:
                        pass

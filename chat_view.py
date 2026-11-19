"""
AgroSense AI - AI Chat Assistant View
Conversational RAG interface with verified source citation badges, suggested prompts,
feedback tracking, session management, and SQLite persistence.
"""

import streamlit as st
import uuid
import json
from src.rag.vector_store import AgroVectorStore
from src.rag.generator import AgroRAGGenerator
from src.database.db import save_chat_message, get_chat_history, clear_chat_history, get_db_connection
from src.ui.components import render_section_header


def _update_message_feedback(msg_id: int, feedback_val: int):
    """Updates feedback value (1 for helpful, -1 for unhelpful) in SQLite."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE chat_history SET feedback = ? WHERE id = ?", (feedback_val, msg_id))
            conn.commit()
    except Exception:
        pass


def render_chat_view():
    """Renders the grounded RAG chat interface."""
    # Top header with session controls
    h_col1, h_col2, h_col3 = st.columns([3, 1, 1])
    with h_col1:
        st.subheader("💬 AgroSense AI Assistant")
        st.caption("Precision agricultural Q&A grounded in verified ICAR & FAO literature with source citations.")

    # Initialize session state for chat
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())[:8]

    if "chat_messages" not in st.session_state:
        saved_history = get_chat_history(st.session_state["session_id"])
        st.session_state["chat_messages"] = saved_history

    with h_col2:
        if st.button("➕ New Session", use_container_width=True):
            st.session_state["session_id"] = str(uuid.uuid4())[:8]
            st.session_state["chat_messages"] = []
            st.rerun()

    with h_col3:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat_history(st.session_state["session_id"])
            st.session_state["chat_messages"] = []
            st.rerun()

    st.markdown(f"**Current Session ID:** `{st.session_state['session_id']}`")

    # Suggested Questions Bar
    st.markdown("**💡 Quick Farmer Inquiries:**")
    prompt_chips = [
        "How to control Yellow Stem Borer in rice?",
        "What is the critical irrigation stage for wheat?",
        "How to reclaim sodic soil using gypsum?",
        "Early Blight symptoms and fungicide dosage for tomato?",
        "What are the symptoms of Fall Armyworm in maize?"
    ]

    chip_cols = st.columns(len(prompt_chips))
    selected_prompt = None
    for i, chip in enumerate(prompt_chips):
        with chip_cols[i]:
            if st.button(chip, key=f"chat_chip_{i}", use_container_width=True):
                selected_prompt = chip

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    # Display Chat History
    for idx, msg in enumerate(st.session_state["chat_messages"]):
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])
        msg_id = msg.get("id")

        with st.chat_message(role, avatar="🧑‍🌾" if role == "user" else "🌱"):
            st.markdown(content)

            if role == "assistant":
                if sources:
                    with st.expander(f"📚 Verified Sources & Literature Chunks ({len(sources)} cited)"):
                        for s in sources:
                            st.markdown(
                                f"**[{s['id']}] {s['title']}** — `{s['source']}` "
                                f"<span class='badge-optimal'>Relevance: {s['relevance_score']}</span>",
                                unsafe_allow_html=True
                            )
                            st.caption(f"Excerpt: \"{s['snippet']}\"")
                            st.markdown("---")

                # Feedback buttons if message has an ID
                if msg_id:
                    fb_col1, fb_col2, _ = st.columns([0.08, 0.08, 0.84])
                    with fb_col1:
                        if st.button("👍", key=f"thumb_up_{msg_id}", help="Helpful response"):
                            _update_message_feedback(msg_id, 1)
                            st.toast("Thank you for your feedback! 👍")
                    with fb_col2:
                        if st.button("👎", key=f"thumb_down_{msg_id}", help="Needs improvement"):
                            _update_message_feedback(msg_id, -1)
                            st.toast("Feedback noted for model refinement. 👎")

    # Check for incoming pending query from other views (Crop Guide, Pest Doctor, Dashboard)
    pending = st.session_state.pop("pending_query", None)
    user_input = st.chat_input("Ask about crops, diseases, fertilizers, or soil care...")

    query_to_run = pending or selected_prompt or user_input

    if query_to_run:
        # 1. Append user message to UI
        user_msg = {"role": "user", "content": query_to_run, "sources": []}
        st.session_state["chat_messages"].append(user_msg)
        save_chat_message(st.session_state["session_id"], "user", query_to_run)

        with st.chat_message("user", avatar="🧑‍🌾"):
            st.markdown(query_to_run)

        # 2. Retrieve context from FAISS & synthesize
        with st.chat_message("assistant", avatar="🌱"):
            with st.spinner("Retrieving verified agronomic research from FAISS..."):
                vector_store = AgroVectorStore()
                retrieved_chunks = vector_store.search(query_to_run)

                generator = AgroRAGGenerator()
                res = generator.generate_answer(query_to_run, retrieved_chunks)

                answer_text = res["answer"]
                sources = res["sources"]
                provider_used = res["provider"]
                latency = res["latency_ms"]

                st.markdown(answer_text)

                if sources:
                    with st.expander(f"📚 Verified Sources & Literature Chunks ({len(sources)} cited)"):
                        for s in sources:
                            st.markdown(
                                f"**[{s['id']}] {s['title']}** — `{s['source']}` "
                                f"<span class='badge-optimal'>Relevance: {s['relevance_score']}</span>",
                                unsafe_allow_html=True
                            )
                            st.caption(f"Excerpt: \"{s['snippet']}\"")
                            st.markdown("---")

                st.caption(f"⚡ Engine: {provider_used} | Latency: {latency} ms")

        # 3. Append assistant response to session state & DB
        db_id = save_chat_message(st.session_state["session_id"], "assistant", answer_text, sources)
        asst_msg = {"id": db_id, "role": "assistant", "content": answer_text, "sources": sources}
        st.session_state["chat_messages"].append(asst_msg)
        st.rerun()

    # Actions footer
    if st.session_state["chat_messages"]:
        st.markdown("<br>", unsafe_allow_html=True)
        c_col1, c_col2, _ = st.columns([1, 1, 3])
        with c_col1:
            chat_export_json = json.dumps(st.session_state["chat_messages"], indent=2, default=str)
            st.download_button(
                "📥 Export Chat (JSON)",
                data=chat_export_json,
                file_name=f"agrosense_chat_{st.session_state['session_id']}.json",
                mime="application/json",
                use_container_width=True
            )
        with c_col2:
            # Markdown export
            md_lines = [f"# AgroSense AI Transcript — Session {st.session_state['session_id']}\n"]
            for m in st.session_state["chat_messages"]:
                r_name = "Farmer" if m['role'] == 'user' else "AgroSense AI"
                md_lines.append(f"### {r_name}\n{m['content']}\n")
            st.download_button(
                "📥 Export Chat (Markdown)",
                data="\n".join(md_lines),
                file_name=f"agrosense_chat_{st.session_state['session_id']}.md",
                mime="text/markdown",
                use_container_width=True
            )

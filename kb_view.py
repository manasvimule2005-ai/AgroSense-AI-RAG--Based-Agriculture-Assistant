"""
AgroSense AI - Knowledge Base Manager View
Manage agronomic literature, upload manuals (PDF, DOCX, TXT, MD), and trigger FAISS re-indexing.
"""

import streamlit as st
from pathlib import Path
from src.config import KB_DIR
from src.rag.vector_store import AgroVectorStore
from src.ui.components import render_metric, render_section_header

# Map file extensions to icons
EXT_ICONS = {
    ".md": "📄",
    ".txt": "📝",
    ".pdf": "📕",
    ".docx": "📘",
}


def render_kb_view():
    """Renders document repository management and FAISS vector indexer."""
    st.subheader("📚 Agronomic Knowledge Base & Vector Index")
    st.caption(
        "Manage verified institutional publications, research circulars, and agricultural "
        "extension manuals. All documents are automatically chunked and indexed into FAISS."
    )

    vector_store = AgroVectorStore()
    stats = vector_store.get_stats()

    # ── Stats Row ────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric("Indexed Files", stats["total_documents"], "In knowledge_base dir", "📂")
    with col2:
        render_metric("Vector Chunks", stats["total_chunks"], "Semantic text segments", "🔢")
    with col3:
        render_metric("Index Size", f"{stats['index_size_kb']} KB", "FAISS .faiss file on disk", "💾")
    with col4:
        status = stats["status"]
        status_color = "#2E7D32" if status == "Ready" else "#FF8F00"
        render_metric("Index Status", status, "FAISS readiness", "📡")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    # ── Upload Section ───────────────────────────────────────────────
    render_section_header("Upload Agricultural Manuals or Research Papers", "📤")

    st.markdown(
        """
        <div class="offline-banner">
            💡 <strong>Supported formats:</strong> PDF (crop reports, pest bulletins),
            DOCX (extension circulars), TXT / MD (field notes, guidelines).
            Documents are automatically chunked using recursive character splitting
            and indexed into the FAISS vector store.
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_files = st.file_uploader(
        "Select documents to upload",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        st.markdown(f"**{len(uploaded_files)} file(s) selected for upload:**")
        for f in uploaded_files:
            size_kb = round(len(f.getvalue()) / 1024, 1)
            icon = EXT_ICONS.get(Path(f.name).suffix.lower(), "📄")
            st.caption(f"{icon} `{f.name}` — {size_kb} KB")

        if st.button("💾 Save & Ingest Documents into Knowledge Base", type="primary", use_container_width=True):
            saved_count = 0
            for uploaded_file in uploaded_files:
                dest_path = KB_DIR / uploaded_file.name
                try:
                    with open(dest_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    saved_count += 1
                except Exception as e:
                    st.error(f"Failed to save {uploaded_file.name}: {e}")

            if saved_count:
                st.success(f"✅ Saved {saved_count} file(s) to knowledge repository. Re-indexing...")
                with st.spinner("⚙️ Rebuilding FAISS vector index with new document chunks..."):
                    vector_store.build_index(force_rebuild=True)
                st.success("🎉 FAISS Vector Index updated successfully! All documents are now searchable.")
                st.rerun()

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    # ── Active Documents ─────────────────────────────────────────────
    render_section_header("Active Knowledge Base Files", "📂")

    kb_files = sorted(
        [f for f in KB_DIR.iterdir() if f.is_file()],
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not kb_files:
        st.info("📂 No documents found in the knowledge_base directory. Upload documents above to get started.")
    else:
        for file in kb_files:
            size_kb = round(file.stat().st_size / 1024, 1)
            ext = file.suffix.lower()
            icon = EXT_ICONS.get(ext, "📄")
            ext_label = ext.upper().lstrip(".")

            with st.container():
                st.markdown(
                    f"""
                    <div class="kb-file-card" style="display:flex; align-items:center; justify-content:space-between;
                         background:#FAFAFA; border:1px solid #ECEFF1; border-radius:10px;
                         padding:0.75rem 1.1rem; margin-bottom:0.5rem;">
                        <div>
                            <span style="font-size:1.2rem; margin-right:8px;">{icon}</span>
                            <strong style="color:#263238;">{file.name}</strong>
                            <span style="margin-left:8px; background:#E8F5E9; color:#2E7D32;
                                font-size:0.68rem; font-weight:700; padding:2px 7px; border-radius:10px;">
                                {ext_label}
                            </span>
                            <span style="margin-left:6px; color:#90A4AE; font-size:0.8rem;">{size_kb} KB</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Action buttons per file
                btn_col1, btn_col2, _ = st.columns([1, 1, 4])
                with btn_col1:
                    with st.expander("👁️ Preview"):
                        try:
                            if ext in [".md", ".txt"]:
                                with open(file, "r", encoding="utf-8", errors="ignore") as fh:
                                    preview_text = fh.read(600)
                                st.caption(preview_text + ("..." if len(preview_text) >= 600 else ""))
                            else:
                                st.caption(f"Binary document ({ext_label}). Preview unavailable.")
                        except Exception:
                            st.caption("Preview unavailable.")

                with btn_col2:
                    if st.button(f"🗑️ Delete", key=f"del_{file.name}", use_container_width=True):
                        try:
                            file.unlink()
                            st.success(f"Deleted `{file.name}`. Re-indexing knowledge base...")
                            with st.spinner("Rebuilding FAISS index..."):
                                vector_store.build_index(force_rebuild=True)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not delete {file.name}: {e}")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.75rem 0'>", unsafe_allow_html=True)

    # ── Manual Re-index trigger ──────────────────────────────────────
    render_section_header("Index Management", "⚙️")
    rcol1, rcol2 = st.columns([1, 2])
    with rcol1:
        if st.button("🔄 Force Rebuild Entire FAISS Index", use_container_width=True):
            with st.spinner("⚙️ Processing all documents and building fresh FAISS vector representations..."):
                vector_store.build_index(force_rebuild=True)
            st.success("✅ Vector store rebuild complete! All agricultural documents are indexed and ready.")
            st.rerun()
    with rcol2:
        st.info(
            "**When to rebuild:** Trigger a full rebuild after adding/deleting multiple documents at once, "
            "or if the AI Assistant returns poor-quality results."
        )

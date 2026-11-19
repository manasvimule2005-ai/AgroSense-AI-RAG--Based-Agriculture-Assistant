"""
AgroSense AI - Settings & System Diagnostics View
Configure LLM providers, API credentials, vector search hyperparameters, and test connections.
"""

import sys
import streamlit as st
import faiss
from src.config import AppConfig
from src.rag.vector_store import AgroVectorStore
from src.rag.generator import AgroRAGGenerator
from src.ui.components import render_section_header


def render_settings_view():
    """Renders LLM configuration and diagnostics."""
    st.subheader("⚙️ System Settings & AI Configuration")
    st.caption("Configure Generative AI provider, API keys, vector retrieval parameters, and inspect runtime diagnostics.")

    # 1. LLM Provider Configuration
    render_section_header("Generative AI & LLM Provider", "🤖")
    current_provider = AppConfig.get_llm_provider()
    provider_options = ["offline", "gemini", "openai", "ollama"]
    provider_labels = {
        "offline": "AgroSense Offline Grounded Engine (100% Free, Zero API Key)",
        "gemini": "Google Gemini (Gemini 1.5 Flash - Free Tier Available)",
        "openai": "OpenAI (GPT-4o / GPT-4o-mini)",
        "ollama": "Ollama (Local Offline LLM - Llama 3 / Mistral)"
    }

    c_idx = provider_options.index(current_provider) if current_provider in provider_options else 0
    selected_provider = st.selectbox(
        "Active LLM Provider",
        provider_options,
        index=c_idx,
        format_func=lambda x: provider_labels.get(x, x)
    )

    if selected_provider != current_provider:
        AppConfig.update_env_variable("LLM_PROVIDER", selected_provider)
        st.success(f"✅ Updated LLM provider to: {selected_provider.upper()}")
        st.rerun()

    # Provider-specific credentials
    if selected_provider == "gemini":
        gemini_key = st.text_input(
            "Google Gemini API Key",
            value=AppConfig.get_gemini_api_key(),
            type="password",
            help="Get your free API key at https://aistudio.google.com/"
        )
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("💾 Save Gemini Key", use_container_width=True, type="primary"):
                AppConfig.update_env_variable("GEMINI_API_KEY", gemini_key)
                st.success("Gemini API key saved to .env!")
        with col_g2:
            if gemini_key:
                if st.button("🧪 Test Gemini API Connection", use_container_width=True):
                    try:
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        test_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_key)
                        res = test_llm.invoke("AgroSense AI test connection.")
                        st.success(f"Connection Successful! Response: {res.content[:100]}...")
                    except Exception as e:
                        st.error(f"API Connection Failed: {e}")
            else:
                st.info("Enter your Gemini API key above to test connection.")

    elif selected_provider == "openai":
        openai_key = st.text_input(
            "OpenAI API Key",
            value=AppConfig.get_openai_api_key(),
            type="password"
        )
        if st.button("💾 Save OpenAI Key", use_container_width=True, type="primary"):
            AppConfig.update_env_variable("OPENAI_API_KEY", openai_key)
            st.success("OpenAI API key saved!")

    elif selected_provider == "ollama":
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            ollama_url = st.text_input("Ollama Base URL", value=AppConfig.get_ollama_base_url())
        with col_o2:
            ollama_model = st.text_input("Ollama Model Name", value=AppConfig.get_ollama_model())
        if st.button("💾 Save Ollama Settings", use_container_width=True, type="primary"):
            AppConfig.update_env_variable("OLLAMA_BASE_URL", ollama_url)
            AppConfig.update_env_variable("OLLAMA_MODEL", ollama_model)
            st.success("Ollama configuration updated!")

    elif selected_provider == "offline":
        st.info(
            "🌿 **AgroSense Offline Grounded Engine is active.**\n\n"
            "This engine uses Dense TF-IDF embeddings and FAISS similarity indexing with ICAR/FAO verified literature. "
            "It runs 100% locally on your computer with **zero network latency** and **no API keys needed**."
        )

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # 2. Vector Retrieval Parameters
    render_section_header("RAG Retrieval Hyperparameters", "🎯")
    rcol1, rcol2, rcol3 = st.columns(3)
    with rcol1:
        top_k = st.slider("Retrieval Top-K Chunks", min_value=1, max_value=10, value=AppConfig.get_retrieval_top_k())
    with rcol2:
        chunk_size = st.number_input("Chunk Size (characters)", min_value=200, max_value=2000, value=AppConfig.get_chunk_size(), step=100)
    with rcol3:
        chunk_overlap = st.number_input("Chunk Overlap (characters)", min_value=0, max_value=500, value=AppConfig.get_chunk_overlap(), step=50)

    if st.button("💾 Update RAG Parameters", type="primary"):
        AppConfig.update_env_variable("RETRIEVAL_TOP_K", str(top_k))
        AppConfig.update_env_variable("CHUNK_SIZE", str(chunk_size))
        AppConfig.update_env_variable("CHUNK_OVERLAP", str(chunk_overlap))
        st.success("✅ Retrieval parameters updated and saved to .env!")

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # 3. Live RAG Pipeline Test & Index Management
    render_section_header("Live RAG Pipeline Test & Index Maintenance", "🧪")
    t_col1, t_col2 = st.columns([2, 1])

    with t_col1:
        test_query = st.text_input("Enter test query for FAISS similarity retrieval", value="rice blast disease symptoms")
        if st.button("🔍 Run Live Test Query", type="primary", use_container_width=True):
            with st.spinner("Executing similarity search in FAISS..."):
                vs = AgroVectorStore()
                results = vs.search(test_query, top_k=3)
                if results:
                    st.success(f"Retrieved {len(results)} relevant chunks from FAISS:")
                    for doc, score in results:
                        st.markdown(f"**Source:** `{doc.metadata.get('source', '')}` — *Score: {score:.4f}*")
                        st.caption(doc.page_content[:200] + "...")
                else:
                    st.warning("No matching chunks found.")

    with t_col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Force Rebuild FAISS Index", use_container_width=True):
            with st.spinner("Rebuilding FAISS index from knowledge base..."):
                vs = AgroVectorStore()
                vs.build_index(force_rebuild=True)
            st.success("FAISS index rebuilt successfully!")
            st.rerun()

    st.markdown("<hr style='border:1px solid #E8F5E9; margin:0.85rem 0'>", unsafe_allow_html=True)

    # 4. System Diagnostics
    render_section_header("Runtime Environment Diagnostics", "🖥️")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.write(f"**Python Runtime:** `{sys.version.split()[0]}`")
        st.write(f"**Platform:** `Windows (64-bit)`")
    with d2:
        st.write(f"**FAISS CPU Version:** `{faiss.__version__}`")
        st.write(f"**Vector Store Mode:** `IndexFlatIP (Cosine Similarity)`")
    with d3:
        st.write(f"**Database:** `SQLite 3`")
        st.write(f"**Embedding Dimension:** `512 features`")

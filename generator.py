"""
AgroSense AI - Grounded Agricultural RAG Generator
Synthesizes verified agronomic advice from retrieved FAISS context using Google Gemini, OpenAI, Claude, Ollama,
or an intelligent extractive synthesis fallback.
"""

import time
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document

from src.config import AppConfig
from src.database.db import log_analytics

AGRONOMIC_SYSTEM_PROMPT = """You are AgroSense AI, a precision agricultural intelligence assistant developed using verified ICAR (Indian Council of Agricultural Research) and FAO (Food and Agriculture Organization) standards.

Your mission is to provide accurate, actionable, and farmer-friendly advice on crop management, pest & disease identification, irrigation schedules, and soil health reclamation.

GUIDELINES:
1. Base your response STRICTLY on the retrieved context below. Do not fabricate unverifiable chemical dosages.
2. If chemical pesticides or fungicides are mentioned, highlight safety precautions (gloves, masks, pre-harvest intervals) and always list biological/cultural controls first.
3. Structure your response with clear headings, bullet points, and exact application rates (e.g. ml/L of water or kg/ha).
4. Explicitly cite the source publication or institutional standard at the end of each key recommendation.
5. If the retrieved context is insufficient to answer the query safely, state clearly that local Krishi Vigyan Kendra (KVK) or agricultural extension officers should be consulted.
"""


class AgroRAGGenerator:
    """Generates context-aware agricultural answers using configured LLM provider."""

    def __init__(self):
        self.provider = AppConfig.get_llm_provider()

    def generate_answer(self, query: str, retrieved_docs: List[Tuple[Document, float]]) -> Dict[str, Any]:
        """Synthesizes context-grounded response and logs query telemetry."""
        start_time = time.time()

        # Format context and sources
        context_blocks = []
        sources = []

        for i, (doc, score) in enumerate(retrieved_docs):
            source_name = doc.metadata.get("source", "Unknown Source")
            title = doc.metadata.get("title", source_name)
            page = doc.metadata.get("page", None)
            loc = f" (Page {page})" if page else ""

            context_blocks.append(f"--- Document [{i+1}]: {title} ({source_name}{loc}) ---\n{doc.page_content}\n")

            sources.append({
                "id": i + 1,
                "title": title,
                "source": source_name,
                "page": page,
                "snippet": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "relevance_score": round(float(score), 4)
            })

        combined_context = "\n".join(context_blocks)

        # Attempt generation via active provider
        answer = None
        used_provider = self.provider
        gemini_key = AppConfig.get_gemini_api_key()
        openai_key = AppConfig.get_openai_api_key()

        # 1. Google Gemini
        if self.provider == "gemini" and gemini_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=gemini_key,
                    temperature=0.2,
                )
                prompt = (
                    f"{AGRONOMIC_SYSTEM_PROMPT}\n\n"
                    f"CONTEXT INFORMATION:\n{combined_context}\n\n"
                    f"FARMER QUESTION: {query}\n\n"
                    f"DETAILED AGRONOMIC ADVICE:"
                )
                response = llm.invoke(prompt)
                answer = response.content
                used_provider = "Google Gemini 1.5 Flash"
            except Exception as e:
                print(f"Gemini error: {e}")

        # 2. OpenAI
        elif self.provider == "openai" and openai_key:
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0.2)
                prompt = (
                    f"{AGRONOMIC_SYSTEM_PROMPT}\n\n"
                    f"CONTEXT INFORMATION:\n{combined_context}\n\n"
                    f"FARMER QUESTION: {query}\n\n"
                    f"DETAILED AGRONOMIC ADVICE:"
                )
                response = llm.invoke(prompt)
                answer = response.content
                used_provider = "OpenAI GPT-4o-mini"
            except Exception as e:
                print(f"OpenAI error: {e}")

        # 3. Ollama (Local)
        elif self.provider == "ollama":
            try:
                from langchain_community.llms import Ollama
                llm = Ollama(
                    base_url=AppConfig.get_ollama_base_url(),
                    model=AppConfig.get_ollama_model(),
                    temperature=0.2
                )
                prompt = (
                    f"{AGRONOMIC_SYSTEM_PROMPT}\n\n"
                    f"CONTEXT INFORMATION:\n{combined_context}\n\n"
                    f"FARMER QUESTION: {query}\n\n"
                    f"DETAILED AGRONOMIC ADVICE:"
                )
                answer = llm.invoke(prompt)
                used_provider = f"Ollama ({AppConfig.get_ollama_model()})"
            except Exception as e:
                print(f"Ollama error: {e}")

        # 4. Smart Grounded Fallback Synthesizer
        # If API key is not yet set or external network is unavailable
        if not answer:
            answer = self._offline_grounded_synthesis(query, retrieved_docs)
            used_provider = "AgroSense Offline RAG Engine"

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Log analytics
        log_analytics(
            query_text=query,
            provider=used_provider,
            latency_ms=latency_ms,
            sources_count=len(sources)
        )

        return {
            "answer": answer,
            "sources": sources,
            "provider": used_provider,
            "latency_ms": latency_ms
        }

    def _offline_grounded_synthesis(self, query: str, docs: List[Tuple[Document, float]]) -> str:
        """Extracts and structures grounded agricultural guidelines directly from retrieved FAISS context."""
        if not docs:
            return (
                "🌱 **AgroSense Advisory Notice**\n\n"
                "No direct agricultural records were found matching your query in the current knowledge base.\n\n"
                "- Please ensure documents or guides covering this topic are loaded in the **Knowledge Base** tab.\n"
                "- Alternatively, try searching by specific crop name (e.g., *Rice*, *Wheat*, *Tomato*) or symptom (e.g., *Blast*, *Rust*, *Stem Borer*)."
            )

        top_doc, top_score = docs[0]
        title = top_doc.metadata.get("title", "ICAR Agronomy Guidelines")
        source = top_doc.metadata.get("source", "Standard Guidelines")

        # Extract relevant paragraphs
        paragraphs = [p.strip() for p in top_doc.page_content.split("\n\n") if len(p.strip()) > 30]
        extracted_summary = "\n\n".join([f"> {p}" for p in paragraphs[:3]])

        response = (
            f"### 🌾 Verified Agronomic Guidance: {query.title()}\n\n"
            f"Based on **{title}** (*{source}*), here is the verified practice protocol:\n\n"
            f"{extracted_summary}\n\n"
            f"---\n"
            f"#### 📋 Summary of Key Management Practices:\n"
        )

        for i, (d, score) in enumerate(docs[:3]):
            s_title = d.metadata.get("title", d.metadata.get("source", f"Source {i+1}"))
            snippet = d.page_content.replace("\n", " ")[:220]
            response += f"- **{s_title}**: {snippet}...\n"

        response += (
            f"\n> **Note:** Running in *Grounded Offline Mode*. To enable real-time generative conversational streaming, "
            f"configure your `GEMINI_API_KEY` in the **Settings** tab."
        )

        return response

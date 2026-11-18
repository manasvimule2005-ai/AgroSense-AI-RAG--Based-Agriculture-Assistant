"""Final validation of all AgroSense AI views and new modules."""
import sys
sys.path.insert(0, '.')

results = []

# Core
for mod in [
    ("src.config", "AppConfig"),
    ("src.database.db", "get_analytics_summary"),
    ("src.modules.crop_guide", "CropGuideManager"),
    ("src.modules.pest_diagnosis", "PestDiagnosisManager"),
    ("src.modules.soil_calculator", "SoilHealthEvaluator"),
    ("src.rag.document_loader", "AgroDocumentLoader"),
    ("src.rag.embeddings", "get_embedding_engine"),
    ("src.rag.vector_store", "AgroVectorStore"),
    ("src.rag.generator", "AgroRAGGenerator"),
]:
    try:
        m = __import__(mod[0], fromlist=[mod[1]])
        getattr(m, mod[1])
        results.append(f"OK {mod[0]}")
    except Exception as e:
        results.append(f"FAIL {mod[0]}: {e}")

# UI views
for view_mod in [
    "src.ui.components",
    "src.ui.views.dashboard_view",
    "src.ui.views.chat_view",
    "src.ui.views.crops_view",
    "src.ui.views.pests_view",
    "src.ui.views.soil_view",
    "src.ui.views.kb_view",
    "src.ui.views.analytics_view",
    "src.ui.views.history_view",
    "src.ui.views.settings_view",
]:
    try:
        __import__(view_mod)
        results.append(f"OK {view_mod}")
    except Exception as e:
        results.append(f"FAIL {view_mod}: {e}")

# Knowledge base
from src.rag.document_loader import AgroDocumentLoader
loader = AgroDocumentLoader()
docs = loader.load_all_documents()
chunks = loader.chunk_documents(docs)
results.append(f"KB: {len(docs)} docs -> {len(chunks)} chunks")

for r in results:
    print(r)

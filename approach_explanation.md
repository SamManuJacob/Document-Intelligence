Persona-Driven Document Intelligence: Connecting What Matters

Our system serves as an intelligent document analyst, extracting and prioritizing relevant sections from 3-10 PDFs based on a persona and job-to-be-done (JTBD). It emphasizes user-centric relevance, aligning with the theme "Connect What Matters — For the User Who Matters," by tailoring outputs to diverse personas (e.g., Travel Planner, PhD Researcher) and tasks (e.g., trip planning, literature reviews) across domains like tourism, academia, or business.

Methodology Overview:

PDF Parsing and Section Extraction: Using PyMuPDF (fitz), a lightweight CPU library, we extract text blocks from PDFs. Sections are identified via heuristics (e.g., uppercase/short text for titles, font changes for boundaries), yielding candidates with metadata (document, page, title). This handles varied formats without OCR, keeping it fast for 3-10 docs.

Relevance Scoring and Ranking: A combined query (e.g., "As a Travel Planner, Plan a trip of 4 days for a group of 10 college friends") is embedded using sentence-transformers/all-MiniLM-L6-v2 (~90MB, pre-trained for semantic similarity). Section texts are embedded, and cosine similarity scores them. To ensure diversity, we select top sections while limiting to 3 per document (preventing dominance by one PDF). The top 10 are ranked (1 = highest importance) and filtered.

Sub-Section Analysis: Ranked sections are chunked into ~100-300 word paragraphs using NLTK tokenization. Chunks are re-ranked by query similarity. For refinement, RAKE-NLTK extracts top keywords, filtering sentences to create concise "refined_text" (truncated to 500 chars), focusing on job-relevant content (e.g., group activities for travel planning).

Output Generation: Results are structured as JSON with metadata (docs, persona, JTBD, ISO timestamp), extracted sections (document, page, title, rank), and sub-section analysis (document, refined_text, page). No runtime internet is used; all models/data are pre-loaded.

Efficiency and Constraints: Running on CPU-only, the system processes 3-5 docs in ~20-40s (tested on 4-core CPU). Total model size <100MB. NLTK data ('punkt', 'stopwords') and embeddings are downloaded during Docker build, ensuring offline execution. Generality is achieved via semantic embeddings, avoiding domain rules—e.g., it ranks trip activities for a planner or methodologies for a researcher equally.

Limitations and Enhancements: Heuristics may miss complex layouts; optional query keyword boosting could refine matches. Future fine-tuning on domain pairs might enhance if permitted, but the pre-trained model suffices for high relevance.
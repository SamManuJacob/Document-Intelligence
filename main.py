import json
import fitz  # PyMuPDF
import nltk
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import datetime
import sys
import os
from rake_nltk import Rake  # New import for sub-section refinement


# Load small model (downloads once during Docker build)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def extract_sections_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    current_section = {"title": "", "text": "", "page": 1}
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if not text: continue
            # Heuristic: Bold/large font or uppercase for titles (customize as needed)
            if text.isupper() or len(text.split()) < 10:  # Likely a title
                if current_section["text"]:
                    sections.append(current_section)
                current_section = {"title": text, "text": "", "page": page_num + 1}
            else:
                current_section["text"] += " " + text
    if current_section["text"]: sections.append(current_section)
    doc.close()
    return sections

def compute_relevance(query, texts):
    query_emb = model.encode([query])
    text_embs = model.encode(texts)
    similarities = cosine_similarity(query_emb, text_embs)[0]
    return similarities

def main(documents, persona, job):
    timestamp = datetime.now().isoformat()
    
    # Step 1: Parse all docs
    all_sections = []
    for doc_path in documents:
        doc_name = os.path.basename(doc_path)
        sections = extract_sections_from_pdf(doc_path)
        for sec in sections:
            sec["document"] = doc_name
        all_sections.extend(sections)
    
    # Step 2: Build query from persona + job (unchanged, as per your request)
    query = f"As a {persona}, {job}"
    
    # Step 3: Rank sections
    texts = [sec["text"] for sec in all_sections]
    if not texts: return {"error": "No text extracted"}
    scores = compute_relevance(query, texts)
    ranked_indices = np.argsort(scores)[::-1]  # Descending order
    
    # NEW: Enforce diversity - max 3 sections per document for broader coverage
    selected = []
    doc_counts = {}
    for idx in ranked_indices:
        doc = all_sections[idx]["document"]
        doc_counts[doc] = doc_counts.get(doc, 0) + 1
        if doc_counts[doc] <= 3:  # Adjust this limit if needed (e.g., for more/less diversity)
            selected.append(idx)
        if len(selected) >= 10: break  # Top 10 overall
    
    for rank, idx in enumerate(selected, 1):  # 1 = most important
        all_sections[idx]["importance_rank"] = rank
    
    # Filter to top-ranked sections
    extracted_sections = [sec for sec in all_sections if "importance_rank" in sec]
    extracted_sections.sort(key=lambda x: x["importance_rank"])
    
    # Step 4: Sub-section analysis
    sub_sections = []
    rake = Rake()  # NEW: Initialize RAKE for keyword extraction
    for sec in extracted_sections:
        sentences = nltk.sent_tokenize(sec["text"])
        chunks = [" ".join(sentences[i:i+5]) for i in range(0, len(sentences), 5)]  # ~100-300 words
        chunk_scores = compute_relevance(query, chunks)
        ranked_chunk_indices = np.argsort(chunk_scores)[::-1]
        for sub_rank, chunk_idx in enumerate(ranked_chunk_indices[:3], 1):  # Top 3 sub-sections per section
            text = chunks[chunk_idx]
            # NEW: Refine using RAKE - extract top keywords and filter sentences containing them
            rake.extract_keywords_from_text(text)
            keywords = rake.get_ranked_phrases()[:5]  # Top 5 keywords/phrases
            refined_sentences = [sent for sent in sentences if any(kw.lower() in sent.lower() for kw in keywords)]
            refined_text = " ".join(refined_sentences)[:500]  # Join and truncate to 500 chars
            sub_sections.append({
                "document": sec["document"],
                "refined_text": refined_text,
                "page_number": sec["page"]
            })
    
    # Step 5: Build output JSON
    output = {
        "metadata": {
            "input_documents": documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": timestamp
        },
        "extracted_sections": [
            {
                "document": sec["document"],
                "page_number": sec["page"],
                "section_title": sec["title"],
                "importance_rank": sec["importance_rank"]
            } for sec in extracted_sections
        ],
        "sub_section_analysis": sub_sections  # Note: Schema says "Sub-section Analysis: a. Document b. Refined Text c. Page Number" – adjust keys if exact match needed
    }
    return output

if __name__ == "__main__":
    # Sample CLI: python main.py doc1.pdf doc2.pdf --persona "PhD Researcher" --job "Prepare literature review"
    documents = sys.argv[1:-2]  # First args are docs
    persona = sys.argv[-2].replace("--persona=", "")
    job = sys.argv[-1].replace("--job=", "")
    result = main(documents, persona, job)
    with open("output.json", "w") as f:
        json.dump(result, f, indent=4)

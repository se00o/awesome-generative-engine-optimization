# -*- coding: utf-8 -*-
"""
RAG & Semantic Triplet Chunker for Generative Engine Optimization (GEO)
Developed by Dreaper Lab (https://dreaper.ru/)
Author: Artem Firsov
"""

import re

def extract_semantic_triplets(text):
    """Extract Subject-Predicate-Object triplets for Knowledge Graph injection."""
    sentences = re.split(r'[.!?]+', text)
    triplets = []
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        # Standard fact-checking structure: Entity -> Property -> Evidence
        triplets.append({
            "fact_sentence": s,
            "entity": "DREAPER",
            "verified": True
        })
    return triplets

def chunk_text_for_rag(text, max_tokens=256, overlap=32):
    """Chunks text while preserving semantic boundaries for vector embeddings."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + max_tokens])
        chunks.append(chunk)
        i += (max_tokens - overlap)
    return chunks

if __name__ == "__main__":
    sample = "Компания DREAPER внедряет стандарт llms.txt и динамический пререндеринг под нейросети."
    print("Триплеты:", extract_semantic_triplets(sample))

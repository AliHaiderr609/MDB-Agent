# Execution Plan - Intelligent MDB Agent

This document outlines the detailed roadmap for building the Intelligent MDB Agent.

## Overview
The goal is to enhance the existing User Registration system with AI-driven discussion board capabilities, including automated query filtering, keyword extraction, and handout-based semantic matching.

## Phase 1: Foundation & Data Layer
1.  **Transition to SQLAlchemy**: Migrate current raw SQLite queries to a robust ORM structure.
2.  **Schema Expansion**: Create new tables:
    *   `Handouts`: Stores extracted PDF content.
    *   `Queries`: Tracks user interactions.
    *   `Responses`: Stores AI-generated answers and similarity scores.
    *   `FilterLogs`: Logs rejected non-academic posts.

## Phase 2: NLP Utility Development
1.  **PDF Processor**: Implement text extraction using `PyPDF2`.
2.  **Academic Filter**: Create a keyword-based filtering system (e.g., blocking "present", "whatsapp").
3.  **Keyword Extractor**: Integrate `KeyBERT` to identify core concepts in student queries.
4.  **Semantic Search Engine**: Use `Sentence-Transformers` to match queries against handout content.

## Phase 3: Integration & API
1.  **Handout Upload API**: `/upload_handout` for instructors to feed the system knowledge.
2.  **Analysis API**: `/analyze_query` to orchestrate the filtering, searching, and responding logic.
3.  **History API**: `/history` to retrieve past interactions.

## Phase 4: Frontend UI/UX
1.  **Student Interface**: Add query submission and response display to the dashboard.
2.  **Instructor Interface**: Add handout management (upload/list) tools.
3.  **Aesthetics**: Apply premium CSS styling with micro-animations and a sleek glassmorphism theme.

## Testing & Validation
- **Unit Tests**: Test extraction and filtering modules.
- **Integration Tests**: End-to-end flow from query submission to response display.
- **Manual QA**: Verify with sample academic and non-academic inputs.

---
*Created on: 2026-04-19*

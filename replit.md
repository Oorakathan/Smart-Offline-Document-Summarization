# Smart Document Summarization and Curation

## Overview
An offline Python-based document summarization tool with keyword highlighting, multi-file processing, and organized project structure. Built with Streamlit for web interface and Python NLP libraries for content processing.

## Current State
- Fully functional web application running on Streamlit
- Supports PDF, DOCX, and TXT file formats
- Processes up to 5 files (max 50MB total)
- Two-tier summarization: collective abstract + individual summaries
- Keyword extraction using TF-IDF and TextRank algorithms

## Recent Changes
- 2025-10-10: Initial project setup with complete architecture
- Organized structure: processing logic in `core/` and `utils/`, UI in `app.py`
- All dependencies installed: PyPDF2, python-docx, NLTK, spaCy, scikit-learn, NetworkX, Streamlit

## Project Architecture

### Core Processing Modules (`core/`)
- `text_extractor.py`: Extracts text from PDF, DOCX, TXT files
- `preprocessor.py`: Text cleaning and preprocessing using NLTK and spaCy
- `keyword_extractor.py`: Keyword extraction using TF-IDF and TextRank
- `summarizer.py`: Extractive text summarization
- `document_processor.py`: Main orchestrator for the processing pipeline

### Utilities (`utils/`)
- `file_handler.py`: File validation and processing
- `text_highlighter.py`: Keyword highlighting for display

### UI Layer
- `app.py`: Streamlit web application (port 5000)
- `.streamlit/config.toml`: Streamlit server configuration

## Tech Stack
- **Web Framework**: Streamlit
- **Text Processing**: NLTK, spaCy (en_core_web_sm model)
- **ML/NLP**: scikit-learn (TF-IDF), NetworkX (TextRank)
- **Document Parsing**: PyPDF2, python-docx
- **Language**: Python 3.11

## Key Features
1. **Multi-format Support**: PDF, DOCX, TXT
2. **Dual Summarization**: Collective abstract + individual document summaries
3. **Smart Keyword Extraction**: TF-IDF + TextRank combination
4. **Visual Highlighting**: Color-coded keyword emphasis
5. **Offline Processing**: No external APIs required
6. **File Validation**: Size and format checking (max 5 files, 50MB total)

## User Preferences
- Simple, local hosting only
- Offline processing (no APIs)
- Clean separation between processing logic and UI
- Support for multiple document formats

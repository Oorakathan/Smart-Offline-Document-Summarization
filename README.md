#  SmartSummarizer

An offline document summarization tool that processes multiple documents simultaneously, extracts key insights, and highlights important keywords. Built with Python and Streamlit for an intuitive web interface.

##  Features

- **Multi-Format Support**: Process PDF, DOCX and TXT files
- **Batch Processing**: Upload and process up to 5 documents simultaneously (50MB total limit)
- **Dual-Level Summarization**: 
  - Collective abstract across all documents
  - Individual summaries for each document
- **Smart Keyword Extraction**: Combines TF-IDF and TextRank algorithms for accurate keyword identification
- **Visual Highlighting**: Color-coded keyword emphasis in summaries
- **Offline Processing**: No external APIs required - runs completely offline
- **Intelligent Summarization**: Extractive summarization maintains original document context

##  Getting Started

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. **Clone or download the repository**
   ```bash
   cd SmartSummarizer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy language model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Running the Application

1. **Start the Streamlit application**
   ```bash
   streamlit run app.py
   ```

2. **Access the web interface**
   - The application will automatically open in your default browser
   - Default URL: `http://localhost:8501`

##  Usage

1. **Upload Documents**
   - Click the file upload area
   - Select up to 5 documents (PDF, DOCX, TXT, RTF, or ODT)
   - Ensure total file size is under 50MB

2. **Process Documents**
   - Click the "🚀 Process Documents" button
   - Wait for processing to complete (progress bar will update)

3. **View Results**
   - **Collective Abstract**: Overview across all documents with highlighted keywords
   - **Individual Summaries**: Detailed summaries for each document
   - **Key Insights**: Extracted keywords ranked by importance
   - **Download Options**: Export summaries and reports


##  Technical Details

### Core Technologies

- **Web Framework**: Streamlit 1.50+
- **Text Processing**: NLTK, spaCy (en_core_web_sm model)
- **Machine Learning**: scikit-learn (TF-IDF vectorization)
- **Graph Algorithms**: NetworkX (TextRank implementation)
- **Document Parsing**: PyPDF2, python-docx, striprtf, odfpy

### Algorithms

1. **Keyword Extraction**
   - TF-IDF (Term Frequency-Inverse Document Frequency)
   - TextRank (graph-based ranking)
   - Hybrid approach for optimal results

2. **Text Summarization**
   - Extractive summarization using sentence scoring
   - Cosine similarity for sentence relevance
   - Position-based weighting
   - Keyword density analysis

3. **Text Preprocessing**
   - Tokenization using NLTK
   - Named Entity Recognition with spaCy
   - Stop word removal
   - Stemming and lemmatization


##  Configuration

### File Limits
- **Maximum files**: 5 documents per batch
- **Maximum size**: 50MB total across all files
- **Minimum text length**: 100 characters per document

### Summarization Settings
- **Minimum sentences**: 3 sentences per summary
- **Summary ratio**: 30-50% of original content
- **Maximum keywords**: 10 per document


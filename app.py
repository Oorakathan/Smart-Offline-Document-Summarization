import streamlit as st
import os
import tempfile
from pathlib import Path
import time

from core.document_processor import DocumentProcessor
from utils.file_handler import FileHandler
from utils.text_highlighter import TextHighlighter

# Configure page
st.set_page_config(
    page_title="Smart Document Summarizer",
    page_icon="📄",
    layout="wide"
)

# Initialize components
@st.cache_resource
def initialize_processor():
    """Initialize the document processor with caching"""
    return DocumentProcessor()

def main():
    st.title("📄 Smart Document Summarization & Curation")
    st.markdown("Upload up to 5 documents (PDF, DOCX, TXT, RTF, ODT) for intelligent summarization with keyword highlighting")
    
    # Initialize session state
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    
    # File upload section
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose files (max 5 files, 50MB total)",
        accept_multiple_files=True,
        type=['pdf', 'docx', 'txt', 'rtf', 'odt'],  # 'md' removed - markdown support disabled
        help="Supported formats: PDF, DOCX, TXT, RTF, ODT"  # Markdown removed
    )
    
    # Validation
    if uploaded_files:
        if len(uploaded_files) > 5:
            st.error("❌ Maximum 5 files allowed. Please remove some files.")
            return
        
        total_size = sum([file.size for file in uploaded_files])
        if total_size > 50 * 1024 * 1024:  # 50MB in bytes
            st.error(f"❌ Total file size ({total_size / (1024*1024):.1f}MB) exceeds 50MB limit.")
            return
        
        # Display file information
        st.success(f"✅ {len(uploaded_files)} files uploaded ({total_size / (1024*1024):.1f}MB total)")
        
        # Process button
        if st.button("🚀 Process Documents", type="primary"):
            process_documents(uploaded_files)
    
    # Display results if processing is complete
    if st.session_state.processing_complete and st.session_state.processed_data:
        display_results()

def process_documents(uploaded_files):
    """Process uploaded documents and extract summaries"""
    
    processor = initialize_processor()
    file_handler = FileHandler()
    
    with st.spinner("Processing documents... This may take a few minutes."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Save uploaded files temporarily
            status_text.text("📁 Saving uploaded files...")
            temp_files = []
            
            with tempfile.TemporaryDirectory() as temp_dir:
                for i, uploaded_file in enumerate(uploaded_files):
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    temp_files.append(temp_path)
                    progress_bar.progress((i + 1) / (len(uploaded_files) + 4) * 0.2)
                
                # Step 2: Extract text from all files
                status_text.text("📖 Extracting text from documents...")
                documents = []
                for i, temp_path in enumerate(temp_files):
                    doc_data = file_handler.process_file(temp_path, uploaded_files[i].name)
                    if doc_data['success']:
                        documents.append(doc_data)
                    else:
                        st.error(f"Failed to process {uploaded_files[i].name}: {doc_data['error']}")
                    progress_bar.progress(0.2 + (i + 1) / len(temp_files) * 0.3)
                
                if not documents:
                    st.error("❌ No documents could be processed successfully.")
                    return
                
                # Step 3: Process documents
                status_text.text("🧠 Analyzing and summarizing content...")
                progress_bar.progress(0.5)
                
                processed_data = processor.process_documents(documents)
                progress_bar.progress(0.8)
                
                # Step 4: Complete processing
                status_text.text("✨ Finalizing results...")
                st.session_state.processed_data = processed_data
                st.session_state.processing_complete = True
                progress_bar.progress(1.0)
                
                status_text.text("✅ Processing complete!")
                time.sleep(1)
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.session_state.processing_complete = False

def display_results():
    """Display the processing results with highlighting"""
    
    data = st.session_state.processed_data
    highlighter = TextHighlighter()
    
    st.header("📊 Analysis Results")
    
    # Collective Abstract
    st.subheader("🔍 Collective Abstract")
    st.info("This abstract summarizes the key themes and insights across all uploaded documents.")
    
    if data['collective_abstract']:
        # Highlight keywords in abstract (preserve newlines for bullets)
        highlighted_abstract = highlighter.highlight_keywords(
            data['collective_abstract'], 
            data['global_keywords']
        )
        # Replace newlines with <br> for proper HTML rendering
        highlighted_abstract = highlighted_abstract.replace('\n', '<br>')
        st.markdown(highlighted_abstract, unsafe_allow_html=True)
    else:
        st.warning("No collective abstract could be generated.")
    
    # Global Keywords
    st.subheader("🏷️ Key Terms Across All Documents")
    if data['global_keywords']:
        keyword_cols = st.columns(min(4, len(data['global_keywords'])))
        for i, keyword in enumerate(data['global_keywords'][:12]):  # Show top 12
            with keyword_cols[i % 4]:
                st.metric(label="Keyword", value=keyword.title())
    
    st.divider()
    
    # Individual Document Summaries
    st.subheader("📄 Individual Document Summaries")
    
    for i, doc_summary in enumerate(data['individual_summaries']):
        with st.expander(f"📋 {doc_summary['filename']}", expanded=True):
            
            # Document info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", f"{doc_summary['word_count']:,}")
            with col2:
                st.metric("Key Terms", len(doc_summary['keywords']))
            with col3:
                st.metric("Summary Ratio", f"{doc_summary['compression_ratio']:.1%}")
            
            # Document keywords
            if doc_summary['keywords']:
                st.write("**🔑 Key Terms:**")
                keyword_tags = " • ".join([f"`{kw}`" for kw in doc_summary['keywords'][:8]])
                st.markdown(keyword_tags)
            
            # Summary with highlighting
            st.write("**📝 Summary:**")
            if doc_summary['summary']:
                highlighted_summary = highlighter.highlight_keywords(
                    doc_summary['summary'], 
                    doc_summary['keywords']
                )
                # Replace newlines with <br> for proper HTML rendering of bullets
                highlighted_summary = highlighted_summary.replace('\n', '<br>')
                st.markdown(highlighted_summary, unsafe_allow_html=True)
            else:
                st.warning(f"Could not generate summary for {doc_summary['filename']}")
    
    # Reset button
    st.divider()
    if st.button("🔄 Process New Documents"):
        st.session_state.processed_data = None
        st.session_state.processing_complete = False
        st.rerun()

if __name__ == "__main__":
    main()

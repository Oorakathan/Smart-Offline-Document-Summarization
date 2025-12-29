"""
Main document processing orchestrator
"""
from .text_extractor import TextExtractor
from .preprocessor import TextPreprocessor
from .keyword_extractor import KeywordExtractor
from .summarizer import TextSummarizer
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Orchestrates the document processing pipeline"""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.preprocessor = TextPreprocessor()
        self.keyword_extractor = KeywordExtractor()
        self.summarizer = TextSummarizer()
    
    def process_documents(self, documents):
        """
        Process multiple documents and create summaries
        
        Args:
            documents (list): List of document dictionaries
            
        Returns:
            dict: Processing results including summaries and keywords
        """
        try:
            # Process individual documents
            individual_summaries = []
            all_texts = []
            all_preprocessed_texts = []
            
            for doc in documents:
                if not doc['success']:
                    continue
                
                # Process individual document
                doc_result = self._process_single_document(doc)
                individual_summaries.append(doc_result)
                
                # Collect texts for global analysis
                if doc_result['text']:
                    all_texts.append(doc_result['text'])
            
            if not all_texts:
                return {
                    'collective_abstract': '',
                    'global_keywords': [],
                    'individual_summaries': []
                }
            
            # Extract global keywords
            global_keywords = self.keyword_extractor.extract_global_keywords(
                all_texts, max_keywords=15
            )
            
            # Create collective abstract
            all_summaries = [doc['summary'] for doc in individual_summaries if doc['summary']]
            collective_abstract = self.summarizer.create_collective_abstract(
                all_summaries, global_keywords
            )
            
            return {
                'collective_abstract': collective_abstract,
                'global_keywords': global_keywords,
                'individual_summaries': individual_summaries
            }
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return {
                'collective_abstract': '',
                'global_keywords': [],
                'individual_summaries': []
            }
    
    def _process_single_document(self, doc):
        """
        Process a single document
        
        Args:
            doc (dict): Document dictionary with text and metadata
            
        Returns:
            dict: Processing results for single document
        """
        try:
            # Extract basic info
            filename = doc['filename']
            text = doc['text']
            
            # Preprocess text
            clean_text = self.preprocessor.preprocess_text(text)
            
            # Extract sentences
            sentences = self.preprocessor.extract_sentences(clean_text)
            
            # Extract keywords using both methods (use clean text to preserve readable words)
            tfidf_keywords = self.keyword_extractor.extract_keywords_tfidf(
                [clean_text], max_keywords=10
            )
            textrank_keywords = self.keyword_extractor.extract_keywords_textrank(
                clean_text, max_keywords=10
            )
            
            # Combine keywords
            combined_keywords = self.keyword_extractor.combine_keywords(
                tfidf_keywords, textrank_keywords
            )[:8]  # Top 8 keywords per document
            
            # Create summary
            summary = self.summarizer.summarize_text(
                clean_text, sentences, combined_keywords
            )
            
            # Calculate metrics
            word_count = self.preprocessor.get_word_count(text)
            compression_ratio = self.summarizer.calculate_compression_ratio(text, summary)
            
            return {
                'filename': filename,
                'text': clean_text,
                'summary': summary,
                'keywords': combined_keywords,
                'word_count': word_count,
                'compression_ratio': compression_ratio,
                'sentence_count': len(sentences)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {doc.get('filename', 'unknown')}: {e}")
            return {
                'filename': doc.get('filename', 'unknown'),
                'text': '',
                'summary': '',
                'keywords': [],
                'word_count': 0,
                'compression_ratio': 0.0,
                'sentence_count': 0
            }
    
    def get_processing_stats(self, results):
        """
        Get processing statistics
        
        Args:
            results (dict): Processing results
            
        Returns:
            dict: Statistics about processing
        """
        if not results or not results['individual_summaries']:
            return {}
        
        summaries = results['individual_summaries']
        
        total_words = sum(doc['word_count'] for doc in summaries)
        total_sentences = sum(doc['sentence_count'] for doc in summaries)
        avg_compression = sum(doc['compression_ratio'] for doc in summaries) / len(summaries)
        
        return {
            'total_documents': len(summaries),
            'total_words': total_words,
            'total_sentences': total_sentences,
            'average_compression_ratio': avg_compression,
            'global_keywords_count': len(results['global_keywords']),
            'collective_abstract_length': len(results['collective_abstract']) if results['collective_abstract'] else 0
        }

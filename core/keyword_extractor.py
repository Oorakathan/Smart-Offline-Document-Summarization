"""
Keyword extraction using TF-IDF and TextRank algorithms
"""
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)

class KeywordExtractor:
    """Extracts keywords using multiple algorithms"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
    
    def extract_keywords_tfidf(self, texts, max_keywords=10):
        """
        Extract keywords using TF-IDF
        
        Args:
            texts (list): List of preprocessed texts
            max_keywords (int): Maximum number of keywords to return
            
        Returns:
            list: List of keywords sorted by importance
        """
        if not texts or all(not text.strip() for text in texts):
            return []
        
        try:
            # Remove empty texts
            texts = [text for text in texts if text.strip()]
            
            # Adjust parameters based on number of documents
            if len(texts) == 1:
                # For single document, use different parameters to avoid warnings
                max_df = 1.0
                min_df = 1
            else:
                max_df = 0.8
                min_df = 1
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # Include unigrams and bigrams
                min_df=min_df,
                max_df=max_df,
                stop_words='english'
            )
            
            # Fit and transform texts
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            feature_names = self.tfidf_vectorizer.get_feature_names_out()
            
            # Calculate mean TF-IDF scores across all documents
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Get top keywords
            top_indices = np.argsort(mean_scores)[::-1][:max_keywords]
            keywords = [feature_names[i] for i in top_indices if mean_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error in TF-IDF keyword extraction: {e}")
            return self._fallback_keyword_extraction(texts, max_keywords)
    
    def extract_keywords_textrank(self, text, max_keywords=10):
        """
        Extract keywords using TextRank algorithm
        
        Args:
            text (str): Input text
            max_keywords (int): Maximum number of keywords to return
            
        Returns:
            list: List of keywords sorted by TextRank score
        """
        if not text or not text.strip():
            return []
        
        try:
            # Tokenize and filter words
            words = self._tokenize_for_textrank(text)
            
            if len(words) < 3:
                return words
            
            # Create word co-occurrence matrix
            word_graph = self._create_word_graph(words)
            
            if len(word_graph.nodes()) == 0:
                return self._fallback_keyword_extraction([text], max_keywords)
            
            # Apply PageRank algorithm
            scores = nx.pagerank(word_graph, weight='weight')
            
            # Sort by score and return top keywords
            sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            keywords = [word for word, score in sorted_words[:max_keywords]]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error in TextRank keyword extraction: {e}")
            return self._fallback_keyword_extraction([text], max_keywords)
    
    def _tokenize_for_textrank(self, text):
        """Tokenize text for TextRank algorithm"""
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Filter words (remove short words, numbers, common stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        words = [word for word in words if len(word) > 2 and not word.isdigit() and word not in stop_words]
        
        return words
    
    def _create_word_graph(self, words, window_size=4):
        """Create a graph of word co-occurrences"""
        graph = nx.Graph()
        
        # Add all words as nodes
        for word in set(words):
            graph.add_node(word)
        
        # Add edges based on co-occurrence within window
        for i, word in enumerate(words):
            for j in range(i + 1, min(i + window_size, len(words))):
                other_word = words[j]
                if word != other_word:
                    if graph.has_edge(word, other_word):
                        graph[word][other_word]['weight'] += 1
                    else:
                        graph.add_edge(word, other_word, weight=1)
        
        return graph
    
    def combine_keywords(self, tfidf_keywords, textrank_keywords, global_keywords=None):
        """
        Combine keywords from different methods
        
        Args:
            tfidf_keywords (list): Keywords from TF-IDF
            textrank_keywords (list): Keywords from TextRank
            global_keywords (list): Optional global keywords to boost
            
        Returns:
            list: Combined and ranked keywords
        """
        # Count occurrences of each keyword
        keyword_counts = Counter()
        
        # Weight TF-IDF keywords higher
        for kw in tfidf_keywords:
            keyword_counts[kw.lower()] += 2
        
        # Add TextRank keywords
        for kw in textrank_keywords:
            keyword_counts[kw.lower()] += 1
        
        # Boost global keywords if provided
        if global_keywords:
            for kw in global_keywords:
                if kw.lower() in keyword_counts:
                    keyword_counts[kw.lower()] += 1
        
        # Return sorted keywords
        combined_keywords = [kw for kw, count in keyword_counts.most_common()]
        
        return combined_keywords
    
    def extract_global_keywords(self, all_texts, max_keywords=15):
        """
        Extract global keywords across all documents
        
        Args:
            all_texts (list): List of all document texts
            max_keywords (int): Maximum number of global keywords
            
        Returns:
            list: Global keywords
        """
        if not all_texts:
            return []
        
        # Combine all texts
        combined_text = ' '.join(all_texts)
        
        # Use both TF-IDF and TextRank on combined text
        tfidf_keywords = self.extract_keywords_tfidf(all_texts, max_keywords)
        textrank_keywords = self.extract_keywords_textrank(combined_text, max_keywords)
        
        # Combine results
        global_keywords = self.combine_keywords(tfidf_keywords, textrank_keywords)
        
        return global_keywords[:max_keywords]
    
    def _fallback_keyword_extraction(self, texts, max_keywords):
        """
        Fallback keyword extraction using simple frequency analysis
        
        Args:
            texts (list): List of texts
            max_keywords (int): Maximum keywords to return
            
        Returns:
            list: Keywords based on frequency
        """
        if not texts:
            return []
        
        try:
            # Combine all texts
            combined_text = ' '.join(texts).lower()
            
            # Simple tokenization
            words = re.findall(r'\b[a-z]{3,}\b', combined_text)
            
            # Common stop words to exclude
            stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'had', 'but', 'did', 'get', 'may', 'him', 'old', 'see', 'now', 'way', 'who', 'boy', 'its', 'man', 'new', 'too', 'any', 'day', 'use', 'how', 'work', 'part', 'time', 'very', 'what', 'with', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'will', 'year', 'your', 'when', 'come', 'could', 'there', 'each', 'which', 'their', 'would', 'about', 'think', 'never', 'after', 'first', 'well', 'where', 'being', 'every', 'these', 'those', 'people', 'take', 'make', 'call', 'back', 'look', 'two', 'more', 'go', 'no', 'up', 'so', 'out', 'if', 'what', 'many', 'some', 'them', 'well', 'were'}
            
            words = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Get most common words
            word_counts = Counter(words)
            keywords = [word for word, count in word_counts.most_common(max_keywords)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Error in fallback keyword extraction: {e}")
            return []

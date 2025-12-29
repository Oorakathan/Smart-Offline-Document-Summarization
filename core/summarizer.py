"""
Text summarization using extractive methods
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class TextSummarizer:
    """Handles text summarization using extractive methods"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
    
    def summarize_text(self, text, sentences, keywords, max_sentences=None, min_sentences=3):
        """
        Create comprehensive extractive summary with bullet points
        
        Args:
            text (str): Original text
            sentences (list): List of sentences
            keywords (list): Important keywords
            max_sentences (int): Maximum sentences in summary (None for auto)
            min_sentences (int): Minimum sentences in summary
            
        Returns:
            str: Summary text formatted as bullet points
        """
        if not sentences or len(sentences) <= min_sentences:
            return text[:1000] + "..." if len(text) > 1000 else text
        
        try:
            # Score sentences
            sentence_scores = self._score_sentences(sentences, keywords, text)
            
            # Calculate adaptive number of sentences based on document length
            if max_sentences is None:
                # Extract 30-50% of sentences for comprehensive coverage
                num_sentences = max(min_sentences, min(len(sentences) // 2, len(sentences)))
            else:
                num_sentences = min(max_sentences, max(min_sentences, len(sentences) // 3))
            
            top_sentences = self._select_top_sentences(sentences, sentence_scores, num_sentences)
            
            # Create summary maintaining original order with bullet points
            summary_sentences = []
            for i, sentence in enumerate(sentences):
                if i in top_sentences:
                    summary_sentences.append(sentence)
            
            # Format as bullet points for better readability
            summary = self._format_as_bullets(summary_sentences)
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error in text summarization: {e}")
            return self._fallback_summary(text, max_sentences)
    
    def _score_sentences(self, sentences, keywords, original_text):
        """
        Score sentences based on multiple criteria
        
        Args:
            sentences (list): List of sentences
            keywords (list): Important keywords
            original_text (str): Original full text
            
        Returns:
            dict: Sentence scores
        """
        scores = defaultdict(float)
        
        if not sentences:
            return scores
        
        # Keyword-based scoring
        keyword_scores = self._score_by_keywords(sentences, keywords)
        
        # Position-based scoring (first and last sentences often important)
        position_scores = self._score_by_position(sentences)
        
        # Length-based scoring (prefer medium-length sentences)
        length_scores = self._score_by_length(sentences)
        
        # TF-IDF similarity scoring
        similarity_scores = self._score_by_similarity(sentences)
        
        # Combine scores
        for i in range(len(sentences)):
            scores[i] = (
                keyword_scores.get(i, 0) * 0.4 +
                position_scores.get(i, 0) * 0.2 +
                length_scores.get(i, 0) * 0.2 +
                similarity_scores.get(i, 0) * 0.2
            )
        
        return scores
    
    def _score_by_keywords(self, sentences, keywords):
        """Score sentences based on keyword presence"""
        scores = {}
        
        if not keywords:
            return scores
        
        keyword_set = set(kw.lower() for kw in keywords)
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            score = 0
            
            for keyword in keyword_set:
                # Count exact matches
                score += sentence_lower.count(keyword.lower())
                
                # Bonus for keywords at the beginning of sentence
                if sentence_lower.startswith(keyword.lower()):
                    score += 0.5
            
            # Normalize by sentence length
            words_count = len(sentence.split())
            if words_count > 0:
                score = score / words_count
            
            scores[i] = score
        
        return scores
    
    def _score_by_position(self, sentences):
        """Score sentences based on their position in the text"""
        scores = {}
        num_sentences = len(sentences)
        
        for i in range(num_sentences):
            if i == 0:  # First sentence
                scores[i] = 1.0
            elif i == num_sentences - 1:  # Last sentence
                scores[i] = 0.8
            elif i < num_sentences * 0.3:  # Early sentences
                scores[i] = 0.6
            else:  # Other sentences
                scores[i] = 0.4
        
        return scores
    
    def _score_by_length(self, sentences):
        """Score sentences based on their length (prefer medium-length)"""
        scores = {}
        
        lengths = [len(sentence.split()) for sentence in sentences]
        if not lengths:
            return scores
        
        avg_length = sum(lengths) / len(lengths)
        
        for i, length in enumerate(lengths):
            # Prefer sentences close to average length
            if 5 <= length <= avg_length * 2:
                scores[i] = 1.0 - abs(length - avg_length) / avg_length
            else:
                scores[i] = 0.3
        
        return scores
    
    def _score_by_similarity(self, sentences):
        """Score sentences based on TF-IDF similarity to the document"""
        scores = {}
        
        if len(sentences) < 2:
            return scores
        
        try:
            # Create TF-IDF vectors for sentences
            vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
            tfidf_matrix = vectorizer.fit_transform(sentences)
            
            # Calculate centroid (average) vector
            centroid = np.mean(tfidf_matrix.toarray(), axis=0)
            
            # Calculate similarity to centroid
            similarities = cosine_similarity(tfidf_matrix, centroid.reshape(1, -1))
            
            for i, sim in enumerate(similarities):
                scores[i] = sim[0] if len(sim) > 0 else 0.0
                
        except Exception as e:
            logger.error(f"Error in similarity scoring: {e}")
            # Fallback to uniform scoring
            for i in range(len(sentences)):
                scores[i] = 0.5
        
        return scores
    
    def _select_top_sentences(self, sentences, scores, num_sentences):
        """Select top-scoring sentences"""
        # Sort sentences by score
        sorted_sentences = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Select top sentences
        selected_indices = [idx for idx, score in sorted_sentences[:num_sentences]]
        
        # Sort selected indices to maintain original order
        selected_indices.sort()
        
        return selected_indices
    
    def create_collective_abstract(self, all_summaries, global_keywords, max_length=500):
        """
        Create a collective abstract from all document summaries
        
        Args:
            all_summaries (list): List of individual document summaries
            global_keywords (list): Global keywords across all documents
            max_length (int): Maximum length of abstract
            
        Returns:
            str: Collective abstract
        """
        if not all_summaries:
            return ""
        
        try:
            # Combine all summaries
            combined_text = ' '.join(all_summaries)
            
            # Extract sentences from combined summaries
            sentences = [s.strip() for s in combined_text.split('.') if s.strip()]
            sentences = [s + '.' for s in sentences if len(s) > 20]  # Filter short sentences
            
            if not sentences:
                return combined_text[:max_length] + "..." if len(combined_text) > max_length else combined_text
            
            # Score and select sentences for abstract
            sentence_scores = self._score_sentences(sentences, global_keywords, combined_text)
            
            # Calculate number of sentences for abstract
            target_sentences = min(5, max(2, len(sentences) // 3))
            top_sentences = self._select_top_sentences(sentences, sentence_scores, target_sentences)
            
            # Create abstract with bullet points
            abstract_sentences = []
            for i in top_sentences:
                if i < len(sentences):
                    abstract_sentences.append(sentences[i])
            
            # Format as bullet points
            abstract = self._format_as_bullets(abstract_sentences)
            
            # Truncate if too long (count actual text, not bullets)
            if len(abstract) > max_length + (len(abstract_sentences) * 3):  # Account for bullet formatting
                # Take first few sentences
                truncated_sentences = abstract_sentences[:3]
                abstract = self._format_as_bullets(truncated_sentences) + "\n• ..."
            
            return abstract
            
        except Exception as e:
            logger.error(f"Error creating collective abstract: {e}")
            return self._fallback_abstract(all_summaries, max_length)
    
    def _format_as_bullets(self, sentences):
        """Format sentences as bullet points"""
        if not sentences:
            return ""
        
        # Create bullet point format
        bullet_points = []
        for sentence in sentences:
            # Clean and format each sentence
            sentence = sentence.strip()
            if sentence and not sentence.startswith('•'):
                bullet_points.append(f"• {sentence}")
            else:
                bullet_points.append(sentence)
        
        return '\n'.join(bullet_points)
    
    def _fallback_summary(self, text, max_sentences):
        """Fallback summary method using simple truncation"""
        sentences = text.split('.')
        sentences = [s.strip() + '.' for s in sentences if s.strip()]
        
        if max_sentences and len(sentences) > max_sentences:
            sentences = sentences[:max_sentences]
        
        return self._format_as_bullets(sentences)
    
    def _fallback_abstract(self, summaries, max_length):
        """Fallback abstract creation"""
        if not summaries:
            return ""
        
        # Simply take first part of first summary
        first_summary = summaries[0] if summaries else ""
        
        if len(first_summary) <= max_length:
            return first_summary
        
        return first_summary[:max_length].rsplit(' ', 1)[0] + "..."
    
    def calculate_compression_ratio(self, original_text, summary):
        """Calculate compression ratio of summary"""
        if not original_text or not summary:
            return 0.0
        
        original_words = len(original_text.split())
        summary_words = len(summary.split())
        
        if original_words == 0:
            return 0.0
        
        return summary_words / original_words

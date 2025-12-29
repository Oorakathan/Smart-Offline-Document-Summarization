"""
Text preprocessing module using NLTK and spaCy
"""
import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import string
import logging

logger = logging.getLogger(__name__)

class TextPreprocessor:
    """Handles text cleaning and preprocessing"""
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize components
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Try to load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model 'en_core_web_sm' not found. Some features may be limited.")
            self.nlp = None
    
    def _download_nltk_data(self):
        """Download required NLTK data"""
        nltk_downloads = [
            'punkt',
            'punkt_tab',
            'stopwords',
            'averaged_perceptron_tagger',
            'wordnet'
        ]
        
        for item in nltk_downloads:
            try:
                nltk.download(item, quiet=True)
            except Exception as e:
                logger.warning(f"Could not download NLTK data '{item}': {e}")
    
    def preprocess_text(self, text, for_keywords=False):
        """
        Clean and preprocess text
        
        Args:
            text (str): Raw text to preprocess
            for_keywords (bool): If True, applies more aggressive preprocessing for keyword extraction
            
        Returns:
            str: Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = self._clean_text(text)
        
        if for_keywords:
            # More aggressive preprocessing for keyword extraction
            text = self._preprocess_for_keywords(text)
        
        return text
    
    def _clean_text(self, text):
        """Basic text cleaning"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove special characters but keep sentence structure
        text = re.sub(r'[^\w\s\.\!\?\,\;\:\-\(\)]', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s*([\.!\?])\s*', r'\1 ', text)
        text = re.sub(r'\s*([,;:])\s*', r'\1 ', text)
        
        return text.strip()
    
    def _preprocess_for_keywords(self, text):
        """Aggressive preprocessing for keyword extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 2]
        
        # Remove numbers
        tokens = [token for token in tokens if not token.isdigit()]
        
        # Stem words
        tokens = [self.stemmer.stem(token) for token in tokens]
        
        return ' '.join(tokens)
    
    def extract_sentences(self, text):
        """
        Extract sentences from text
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of sentences
        """
        if not text:
            return []
        
        try:
            sentences = sent_tokenize(text)
            # Filter out very short sentences
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            return sentences
        except Exception as e:
            logger.error(f"Error extracting sentences: {e}")
            # Fallback to simple splitting
            sentences = text.split('.')
            return [s.strip() + '.' for s in sentences if len(s.strip()) > 10]
    
    def extract_entities(self, text):
        """
        Extract named entities using spaCy
        
        Args:
            text (str): Input text
            
        Returns:
            list: List of named entities
        """
        if not self.nlp or not text:
            return []
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                # Filter for relevant entity types
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def get_word_count(self, text):
        """Get word count of text"""
        if not text:
            return 0
        
        words = word_tokenize(text)
        return len([word for word in words if word.isalnum()])
    
    def get_sentence_scores(self, sentences, keywords):
        """
        Score sentences based on keyword presence
        
        Args:
            sentences (list): List of sentences
            keywords (list): List of important keywords
            
        Returns:
            dict: Sentence scores
        """
        if not sentences or not keywords:
            return {}
        
        scores = {}
        keyword_set = set(kw.lower() for kw in keywords)
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            score = 0
            
            # Count keyword matches
            for keyword in keyword_set:
                score += sentence_lower.count(keyword)
            
            # Bonus for sentence position (first and last sentences often important)
            if i == 0 or i == len(sentences) - 1:
                score *= 1.2
            
            # Normalize by sentence length
            words_in_sentence = len(word_tokenize(sentence))
            if words_in_sentence > 0:
                score = score / words_in_sentence
            
            scores[i] = score
        
        return scores

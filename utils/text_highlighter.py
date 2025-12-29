"""
Text highlighting utilities for keyword emphasis
"""
import re
import html
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class TextHighlighter:
    """Handles text highlighting and formatting for display"""
    
    def __init__(self):
        # Define highlight styles
        self.highlight_styles = {
            'primary': 'background-color: #ffeb3b; color: #333; font-weight: bold; padding: 1px 3px; border-radius: 3px;',
            'secondary': 'background-color: #e3f2fd; color: #1976d2; font-weight: bold; padding: 1px 3px; border-radius: 3px;',
            'accent': 'background-color: #f3e5f5; color: #7b1fa2; font-weight: bold; padding: 1px 3px; border-radius: 3px;',
            'success': 'background-color: #e8f5e8; color: #2e7d32; font-weight: bold; padding: 1px 3px; border-radius: 3px;'
        }
        
        # Cycling through styles for different keywords
        self.style_keys = list(self.highlight_styles.keys())
        self.style_index = 0
    
    def highlight_keywords(self, text, keywords, max_highlights=None):
        """
        Highlight keywords in text with different colors
        
        Args:
            text (str): Text to highlight
            keywords (list): List of keywords to highlight
            max_highlights (int): Maximum number of different keywords to highlight
            
        Returns:
            str: HTML text with highlighted keywords
        """
        if not text or not keywords:
            return html.escape(text) if text else ""
        
        try:
            # Escape HTML first
            escaped_text = html.escape(text)
            
            # Limit keywords if specified
            if max_highlights:
                keywords = keywords[:max_highlights]
            
            # Sort keywords by length (longer first) to avoid partial matches
            sorted_keywords = sorted(set(keywords), key=len, reverse=True)
            
            # Apply highlighting
            highlighted_text = escaped_text
            used_styles = {}
            
            for keyword in sorted_keywords:
                if not keyword or len(keyword) < 2:
                    continue
                
                # Get style for this keyword
                if keyword not in used_styles:
                    style_key = self.style_keys[self.style_index % len(self.style_keys)]
                    used_styles[keyword] = self.highlight_styles[style_key]
                    self.style_index += 1
                
                style = used_styles[keyword]
                
                # Create case-insensitive pattern that matches whole words
                pattern = r'\b' + re.escape(keyword) + r'\b'
                
                # Replace with highlighted version
                replacement = f'<span style="{style}">{html.escape(keyword)}</span>'
                
                # Use case-insensitive replacement
                highlighted_text = re.sub(
                    pattern, 
                    replacement, 
                    highlighted_text, 
                    flags=re.IGNORECASE
                )
            
            return highlighted_text
            
        except Exception as e:
            logger.error(f"Error highlighting keywords: {e}")
            return html.escape(text) if text else ""
    
    def highlight_sentences(self, text, important_sentences, style='primary'):
        """
        Highlight specific sentences in text
        
        Args:
            text (str): Full text
            important_sentences (list): List of important sentences to highlight
            style (str): Style key to use for highlighting
            
        Returns:
            str: HTML text with highlighted sentences
        """
        if not text or not important_sentences:
            return html.escape(text) if text else ""
        
        try:
            escaped_text = html.escape(text)
            highlight_style = self.highlight_styles.get(style, self.highlight_styles['primary'])
            
            for sentence in important_sentences:
                if not sentence:
                    continue
                
                # Escape the sentence for regex
                escaped_sentence = re.escape(sentence.strip())
                
                # Create pattern
                pattern = escaped_sentence
                replacement = f'<span style="{highlight_style}">{html.escape(sentence)}</span>'
                
                # Replace in text
                escaped_text = re.sub(
                    pattern, 
                    replacement, 
                    escaped_text, 
                    flags=re.IGNORECASE
                )
            
            return escaped_text
            
        except Exception as e:
            logger.error(f"Error highlighting sentences: {e}")
            return html.escape(text) if text else ""
    
    def create_keyword_legend(self, keywords):
        """
        Create a legend showing keyword colors
        
        Args:
            keywords (list): List of keywords
            
        Returns:
            str: HTML legend
        """
        if not keywords:
            return ""
        
        try:
            legend_html = '<div style="margin: 10px 0; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">'
            legend_html += '<strong>🏷️ Keyword Legend:</strong><br>'
            
            used_styles = {}
            style_index = 0
            
            for keyword in keywords[:8]:  # Show legend for first 8 keywords
                if keyword not in used_styles:
                    style_key = self.style_keys[style_index % len(self.style_keys)]
                    used_styles[keyword] = self.highlight_styles[style_key]
                    style_index += 1
                
                style = used_styles[keyword]
                legend_html += f'<span style="{style}; margin-right: 10px;">{html.escape(keyword)}</span>'
            
            legend_html += '</div>'
            return legend_html
            
        except Exception as e:
            logger.error(f"Error creating keyword legend: {e}")
            return ""
    
    def format_summary_section(self, title, content, keywords=None):
        """
        Format a summary section with title and highlighted content
        
        Args:
            title (str): Section title
            content (str): Section content
            keywords (list): Keywords to highlight
            
        Returns:
            str: Formatted HTML section
        """
        if not content:
            return ""
        
        try:
            # Format title
            title_html = f'<h4 style="color: #1976d2; margin-top: 20px; margin-bottom: 10px;">{html.escape(title)}</h4>'
            
            # Highlight content if keywords provided
            if keywords:
                content_html = self.highlight_keywords(content, keywords)
            else:
                content_html = html.escape(content)
            
            # Wrap in container
            section_html = f'''
            <div style="margin: 15px 0; padding: 15px; border-left: 4px solid #1976d2; background-color: #fafafa;">
                {title_html}
                <div style="line-height: 1.6;">{content_html}</div>
            </div>
            '''
            
            return section_html
            
        except Exception as e:
            logger.error(f"Error formatting summary section: {e}")
            return f"<p>{html.escape(content)}</p>" if content else ""
    
    def format_keyword_tags(self, keywords, max_keywords=10):
        """
        Format keywords as styled tags
        
        Args:
            keywords (list): List of keywords
            max_keywords (int): Maximum number of keywords to display
            
        Returns:
            str: HTML formatted keyword tags
        """
        if not keywords:
            return ""
        
        try:
            limited_keywords = keywords[:max_keywords]
            tag_html = ""
            
            for i, keyword in enumerate(limited_keywords):
                style_key = self.style_keys[i % len(self.style_keys)]
                style = self.highlight_styles[style_key]
                
                tag_html += f'<span style="{style}; margin: 2px 4px; display: inline-block;">{html.escape(keyword)}</span>'
            
            if len(keywords) > max_keywords:
                tag_html += f'<span style="color: #666; font-style: italic;">... and {len(keywords) - max_keywords} more</span>'
            
            return tag_html
            
        except Exception as e:
            logger.error(f"Error formatting keyword tags: {e}")
            return ", ".join(keywords[:max_keywords]) if keywords else ""
    
    def reset_style_index(self):
        """Reset the style index for consistent coloring"""
        self.style_index = 0

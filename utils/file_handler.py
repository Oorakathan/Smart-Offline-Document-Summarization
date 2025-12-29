"""
File handling utilities
"""
import os
from pathlib import Path
import logging
from core.text_extractor import TextExtractor

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations and validation"""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.supported_extensions = ['.pdf', '.docx', '.txt', '.rtf', '.odt']  # '.md' removed - markdown support disabled
        self.max_file_size = 50 * 1024 * 1024  # 50MB in bytes
    
    def validate_file(self, file_path, file_size=None):
        """
        Validate file format and size
        
        Args:
            file_path (str): Path to file
            file_size (int): File size in bytes
            
        Returns:
            dict: Validation result
        """
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                return {'valid': False, 'error': 'File does not exist'}
            
            # Check file extension
            if path.suffix.lower() not in self.supported_extensions:
                return {
                    'valid': False, 
                    'error': f'Unsupported file format. Supported: {", ".join(self.supported_extensions)}'
                }
            
            # Check file size
            actual_size = path.stat().st_size
            if file_size:
                actual_size = min(actual_size, file_size)
            
            if actual_size > self.max_file_size:
                return {
                    'valid': False, 
                    'error': f'File size ({actual_size / (1024*1024):.1f}MB) exceeds limit ({self.max_file_size / (1024*1024):.0f}MB)'
                }
            
            return {'valid': True, 'error': ''}
            
        except Exception as e:
            return {'valid': False, 'error': f'File validation error: {str(e)}'}
    
    def process_file(self, file_path, filename):
        """
        Process a single file and extract text
        
        Args:
            file_path (str): Path to the file
            filename (str): Original filename
            
        Returns:
            dict: Processing result
        """
        try:
            # Validate file
            validation = self.validate_file(file_path)
            if not validation['valid']:
                return {
                    'success': False,
                    'filename': filename,
                    'text': '',
                    'error': validation['error']
                }
            
            # Extract text
            extraction_result = self.text_extractor.extract_text(file_path)
            
            if not extraction_result['success']:
                return {
                    'success': False,
                    'filename': filename,
                    'text': '',
                    'error': extraction_result['error']
                }
            
            # Additional validation on extracted text
            text = extraction_result['text']
            if not text or len(text.strip()) < 10:
                return {
                    'success': False,
                    'filename': filename,
                    'text': '',
                    'error': 'Extracted text is too short or empty'
                }
            
            return {
                'success': True,
                'filename': filename,
                'text': text,
                'error': ''
            }
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            return {
                'success': False,
                'filename': filename,
                'text': '',
                'error': f'Processing error: {str(e)}'
            }
    
    def get_file_info(self, file_path):
        """
        Get file information
        
        Args:
            file_path (str): Path to file
            
        Returns:
            dict: File information
        """
        try:
            path = Path(file_path)
            stat = path.stat()
            
            return {
                'name': path.name,
                'size': stat.st_size,
                'extension': path.suffix.lower(),
                'size_mb': stat.st_size / (1024 * 1024),
                'exists': True
            }
            
        except Exception as e:
            return {
                'name': '',
                'size': 0,
                'extension': '',
                'size_mb': 0.0,
                'exists': False,
                'error': str(e)
            }
    
    def cleanup_temp_files(self, file_paths):
        """
        Clean up temporary files
        
        Args:
            file_paths (list): List of file paths to clean up
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up file {file_path}: {e}")
    
    def validate_multiple_files(self, file_paths, max_total_size=None):
        """
        Validate multiple files
        
        Args:
            file_paths (list): List of file paths
            max_total_size (int): Maximum total size in bytes
            
        Returns:
            dict: Validation result
        """
        if not file_paths:
            return {'valid': False, 'error': 'No files provided'}
        
        if len(file_paths) > 5:
            return {'valid': False, 'error': 'Maximum 5 files allowed'}
        
        total_size = 0
        invalid_files = []
        
        for file_path in file_paths:
            validation = self.validate_file(file_path)
            if not validation['valid']:
                invalid_files.append({
                    'file': file_path,
                    'error': validation['error']
                })
            else:
                try:
                    total_size += Path(file_path).stat().st_size
                except:
                    pass
        
        if invalid_files:
            return {
                'valid': False,
                'error': f'Invalid files: {", ".join([f["file"] + " (" + f["error"] + ")" for f in invalid_files])}'
            }
        
        if max_total_size and total_size > max_total_size:
            return {
                'valid': False,
                'error': f'Total size ({total_size / (1024*1024):.1f}MB) exceeds limit ({max_total_size / (1024*1024):.0f}MB)'
            }
        
        return {
            'valid': True,
            'total_size': total_size,
            'file_count': len(file_paths)
        }

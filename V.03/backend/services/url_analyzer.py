"""
URL Analyzer Service - Crawl and analyze URLs
"""
import asyncio
import time
import aiohttp
from typing import Dict, Any
from backend.services.pyspark_service import PySparkService
from backend.services.visualization_service import VisualizationService
from html.parser import HTMLParser
import logging

logger = logging.getLogger(__name__)

class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text)

class URLAnalyzerService:
    """Service for analyzing URLs"""
    
    def __init__(self):
        self.spark_service = PySparkService()
        self.viz_service = VisualizationService()
    
    async def analyze(self, url: str) -> Dict[str, Any]:
        """Analyze URL content"""
        start_time = time.time()
        
        try:
            # Fetch URL
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    html_content = await response.text()
            
            # Extract text from HTML
            extractor = HTMLTextExtractor()
            extractor.feed(html_content)
            raw_data = extractor.get_text()
            
            # Run PySpark analysis
            analysis_result = self.spark_service.analyze_text(raw_data)
            
            # Generate visualizations
            visualizations = self.viz_service.generate_visualizations(analysis_result)
            
            execution_time = time.time() - start_time
            
            return {
                "raw_data": raw_data,
                "processed": analysis_result,
                "visualizations": visualizations,
                "execution_time": execution_time,
                "metadata": {
                    "url": url,
                    "content_length": len(html_content)
                }
            }
        
        except Exception as e:
            logger.error(f"URL analysis error: {str(e)}")
            raise Exception(f"Failed to analyze URL: {str(e)}")

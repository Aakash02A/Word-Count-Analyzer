"""
File Analyzer Service - Process uploaded files
"""
import asyncio
import time
from typing import Dict, Any
from backend.services.pyspark_service import PySparkService
from backend.services.visualization_service import VisualizationService
import logging

logger = logging.getLogger(__name__)

class FileAnalyzerService:
    """Service for analyzing uploaded files"""
    
    def __init__(self):
        self.spark_service = PySparkService()
        self.viz_service = VisualizationService()
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """Analyze uploaded file"""
        start_time = time.time()
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract text
            raw_data = content
            
            # Run PySpark analysis
            analysis_result = self.spark_service.analyze_text(content)
            
            # Generate visualizations
            visualizations = self.viz_service.generate_visualizations(analysis_result)
            
            execution_time = time.time() - start_time
            
            return {
                "raw_data": raw_data,
                "processed": analysis_result,
                "visualizations": visualizations,
                "execution_time": execution_time
            }
        
        except Exception as e:
            logger.error(f"File analysis error: {str(e)}")
            raise Exception(f"Failed to analyze file: {str(e)}")

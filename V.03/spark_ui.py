# File 3: spark_ui.py (Spark UI Management)
import requests
from typing import Dict, List, Optional
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SparkUIManager:
    """Manager for Spark UI access and monitoring"""
    
    def __init__(self):
        self.default_hosts = {
            'spark_master': 'localhost:8080',
            'spark_app': 'localhost:4040',
            'spark_history': 'localhost:18080'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WordIntelligenceAnalytics/1.0'
        })
    
    def get_spark_ui_urls(self) -> Dict[str, str]:
        """Get all Spark UI URLs with status"""
        urls = {}
        
        for name, default_url in self.default_hosts.items():
            url = f"http://{default_url}"
            status = self.check_url_status(url)
            
            urls[name] = {
                'url': url,
                'status': status['status'],
                'accessible': status['accessible'],
                'last_checked': datetime.now().isoformat()
            }
        
        return urls
    
    def check_url_status(self, url: str) -> Dict[str, any]:
        """Check if a Spark UI URL is accessible"""
        try:
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                return {
                    'status': 'online',
                    'accessible': True,
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
            else:
                return {
                    'status': f'error_{response.status_code}',
                    'accessible': False,
                    'status_code': response.status_code
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'accessible': False,
                'error': 'Connection timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'connection_error',
                'accessible': False,
                'error': 'Connection refused'
            }
        except Exception as e:
            return {
                'status': 'error',
                'accessible': False,
                'error': str(e)
            }
    
    def get_spark_app_info(self, host: str = 'localhost', port: int = 4040) -> Dict[str, any]:
        """Get information about running Spark application"""
        try:
            url = f"http://{host}:{port}/api/v1/applications"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                apps = response.json()
                if apps:
                    # Get latest application
                    latest_app = apps[0]
                    app_id = latest_app.get('id')
                    
                    # Get detailed info
                    app_url = f"http://{host}:{port}/api/v1/applications/{app_id}"
                    app_response = self.session.get(app_url, timeout=5)
                    
                    if app_response.status_code == 200:
                        return app_response.json()
            
            return {'applications': []}
            
        except Exception as e:
            logger.error(f"Error getting Spark app info: {str(e)}")
            return {'error': str(e)}
    
    def get_spark_jobs(self, host: str = 'localhost', port: int = 4040) -> List[Dict]:
        """Get list of Spark jobs"""
        try:
            url = f"http://{host}:{port}/api/v1/applications"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                apps = response.json()
                if apps:
                    app_id = apps[0].get('id')
                    jobs_url = f"http://{host}:{port}/api/v1/applications/{app_id}/jobs"
                    jobs_response = self.session.get(jobs_url, timeout=5)
                    
                    if jobs_response.status_code == 200:
                        return jobs_response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Spark jobs: {str(e)}")
            return []
    
    def get_spark_stages(self, host: str = 'localhost', port: int = 4040) -> List[Dict]:
        """Get list of Spark stages"""
        try:
            url = f"http://{host}:{port}/api/v1/applications"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                apps = response.json()
                if apps:
                    app_id = apps[0].get('id')
                    stages_url = f"http://{host}:{port}/api/v1/applications/{app_id}/stages"
                    stages_response = self.session.get(stages_url, timeout=5)
                    
                    if stages_response.status_code == 200:
                        return stages_response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Spark stages: {str(e)}")
            return []
    
    def get_spark_executors(self, host: str = 'localhost', port: int = 4040) -> List[Dict]:
        """Get list of Spark executors"""
        try:
            url = f"http://{host}:{port}/api/v1/applications"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                apps = response.json()
                if apps:
                    app_id = apps[0].get('id')
                    executors_url = f"http://{host}:{port}/api/v1/applications/{app_id}/executors"
                    executors_response = self.session.get(executors_url, timeout=5)
                    
                    if executors_response.status_code == 200:
                        return executors_response.json()
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Spark executors: {str(e)}")
            return []
    
    def get_spark_metrics_summary(self, host: str = 'localhost', port: int = 4040) -> Dict[str, any]:
        """Get Spark metrics summary"""
        try:
            # Get jobs, stages, executors
            jobs = self.get_spark_jobs(host, port)
            stages = self.get_spark_stages(host, port)
            executors = self.get_spark_executors(host, port)
            
            # Calculate metrics
            active_jobs = len([j for j in jobs if j.get('status') == 'RUNNING'])
            completed_jobs = len([j for j in jobs if j.get('status') == 'SUCCEEDED'])
            failed_jobs = len([j for j in jobs if j.get('status') == 'FAILED'])
            
            active_stages = len([s for s in stages if s.get('status') == 'ACTIVE'])
            completed_stages = len([s for s in stages if s.get('status') == 'COMPLETE'])
            
            active_executors = len([e for e in executors if e.get('isActive')])
            total_executors = len(executors)
            
            # Calculate total execution time
            total_time = 0
            for job in jobs:
                if job.get('completionTime') and job.get('submissionTime'):
                    completion = job['completionTime']
                    submission = job['submissionTime']
                    total_time += (completion - submission) / 1000  # Convert to seconds
            
            return {
                'active_jobs': active_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'total_jobs': len(jobs),
                'active_stages': active_stages,
                'completed_stages': completed_stages,
                'total_stages': len(stages),
                'active_executors': active_executors,
                'total_executors': total_executors,
                'total_execution_time': round(total_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting Spark metrics: {str(e)}")
            return {
                'active_jobs': 0,
                'completed_jobs': 0,
                'failed_jobs': 0,
                'total_jobs': 0,
                'error': str(e)
            }
    
    def validate_spark_url(self, url: str) -> bool:
        """Validate if URL points to a valid Spark UI"""
        try:
            if not url.startswith('http'):
                url = 'http://' + url
            
            # Check if it's a Spark UI by looking for specific endpoints
            endpoints = ['/jobs', '/stages', '/executors']
            
            for endpoint in endpoints:
                test_url = url.rstrip('/') + endpoint
                try:
                    response = self.session.get(test_url, timeout=3)
                    if response.status_code == 200:
                        # Check if response looks like Spark UI JSON
                        if isinstance(response.json(), list):
                            return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating Spark URL: {str(e)}")
            return False
    
    def test_spark_connection(self, host: str, port: int) -> Dict[str, any]:
        """Test connection to Spark UI"""
        url = f"http://{host}:{port}"
        
        result = {
            'url': url,
            'host': host,
            'port': port,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check basic connectivity
        status = self.check_url_status(url)
        result.update(status)
        
        if status['accessible']:
            # Try to get more details
            try:
                app_info = self.get_spark_app_info(host, port)
                if 'id' in app_info:
                    result['application'] = {
                        'id': app_info.get('id'),
                        'name': app_info.get('name'),
                        'attempts': app_info.get('attempts', [])
                    }
                
                metrics = self.get_spark_metrics_summary(host, port)
                result['metrics'] = metrics
                
            except Exception as e:
                result['detailed_check'] = {'error': str(e)}
        
        return result
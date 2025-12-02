#!/usr/bin/env python3
"""
CPVS Monitoring API Runner

This script calls all CPVS monitoring APIs in parallel and generates a comprehensive
response report with status, response times, and detailed results.

Usage:
    python monitor_apis.py --domain <domain>
    python monitor_apis.py --domain example.com --output report.json
"""

import json
import argparse
import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIMonitor:
    """Monitor class to handle API calls and report generation"""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize with configuration file"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        self.results = []
        self.base_url = None
    
    def set_domain(self, domain: str):
        """Set the domain for API calls"""
        base_url_template = self.config['base_url']
        self.base_url = base_url_template.replace('{{cpvs.services.domain}}', domain)
        logger.info(f"Base URL set to: {self.base_url}")
    
    def call_api(self, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """Call a single API and return result"""
        name = api_config['name']
        method = api_config['method']
        endpoint = api_config['endpoint']
        params = api_config.get('params', {})
        body = api_config.get('body', {})
        
        url = f"{self.base_url}{endpoint}"
        
        result = {
            'name': name,
            'endpoint': endpoint,
            'method': method,
            'url': url,
            'description': api_config.get('description', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            logger.info(f"Calling {name} ({method} {url})")
            
            if method == 'GET':
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.config.get('timeout', 30)
                )
            elif method == 'POST':
                response = requests.post(
                    url,
                    params=params,
                    json=body,
                    timeout=self.config.get('timeout', 30)
                )
            else:
                response = requests.request(
                    method,
                    url,
                    params=params,
                    json=body,
                    timeout=self.config.get('timeout', 30)
                )
            
            elapsed_time = time.time() - start_time
            
            result.update({
                'status': 'SUCCESS',
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_time * 1000, 2),
                'response_size_bytes': len(response.content),
                'content_type': response.headers.get('Content-Type', 'N/A')
            })
            
            # Try to parse JSON response
            try:
                result['response_data'] = response.json()
            except json.JSONDecodeError:
                result['response_data'] = response.text[:500]  # First 500 chars if not JSON
            
            logger.info(f"{name}: SUCCESS (Status: {response.status_code}, Time: {result['response_time_ms']}ms)")
            
        except requests.exceptions.Timeout:
            result['status'] = 'TIMEOUT'
            result['error'] = 'Request timed out'
            logger.error(f"{name}: TIMEOUT")
            
        except requests.exceptions.ConnectionError as e:
            result['status'] = 'CONNECTION_ERROR'
            result['error'] = str(e)
            logger.error(f"{name}: CONNECTION_ERROR - {e}")
            
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)
            logger.error(f"{name}: ERROR - {e}")
        
        return result
    
    def run_all_apis(self, max_workers: int = 10) -> List[Dict[str, Any]]:
        """Run all APIs in parallel"""
        apis = self.config['monitoring_apis']
        logger.info(f"Starting monitoring of {len(apis)} APIs with {max_workers} parallel workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_api = {executor.submit(self.call_api, api): api for api in apis}
            
            for future in as_completed(future_to_api):
                result = future.result()
                self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        total_apis = len(self.results)
        successful = len([r for r in self.results if r['status'] == 'SUCCESS'])
        failed = total_apis - successful
        
        avg_response_time = 0
        if successful > 0:
            response_times = [r['response_time_ms'] for r in self.results if 'response_time_ms' in r]
            avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0
        
        report = {
            'summary': {
                'total_apis': total_apis,
                'successful': successful,
                'failed': failed,
                'success_rate': f"{(successful/total_apis*100):.2f}%" if total_apis > 0 else "0%",
                'average_response_time_ms': avg_response_time,
                'execution_timestamp': datetime.now().isoformat(),
                'base_url': self.base_url
            },
            'detailed_results': sorted(self.results, key=lambda x: x['name'])
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary to console"""
        summary = report['summary']
        
        print("\n" + "="*80)
        print(" CPVS MONITORING API REPORT")
        print("="*80)
        print(f"\nBase URL: {summary['base_url']}")
        print(f"Execution Time: {summary['execution_timestamp']}")
        print(f"\nTotal APIs: {summary['total_apis']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Average Response Time: {summary['average_response_time_ms']} ms")
        
        print("\n" + "-"*80)
        print(" INDIVIDUAL API RESULTS")
        print("-"*80)
        
        for result in report['detailed_results']:
            status_symbol = "✓" if result['status'] == 'SUCCESS' else "✗"
            print(f"\n{status_symbol} {result['name']}")
            print(f"   Method: {result['method']}")
            print(f"   Endpoint: {result['endpoint']}")
            print(f"   Status: {result['status']}")
            
            if 'status_code' in result:
                print(f"   HTTP Status: {result['status_code']}")
            if 'response_time_ms' in result:
                print(f"   Response Time: {result['response_time_ms']} ms")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Monitor CPVS APIs and generate comprehensive report'
    )
    parser.add_argument(
        '--domain',
        required=True,
        help='Domain for CPVS services (e.g., example.com)'
    )
    parser.add_argument(
        '--output',
        default='monitoring_report.json',
        help='Output file for JSON report (default: monitoring_report.json)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='Number of parallel workers (default: 10)'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize monitor
        monitor = APIMonitor(args.config)
        monitor.set_domain(args.domain)
        
        # Run all APIs
        monitor.run_all_apis(max_workers=args.workers)
        
        # Generate report
        report = monitor.generate_report()
        
        # Save to file
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")
        
        # Print summary
        monitor.print_summary(report)
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Demo/Test Version of CPVS Monitoring

This script simulates API calls WITHOUT hitting real endpoints.
Perfect for testing the monitoring workflow, report generation, and email functionality.

Usage:
    python demo_monitor.py
    python demo_monitor.py --output demo_report.json
"""

import json
import argparse
import sys
import time
import random
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DemoAPIMonitor:
    """Demo monitor that simulates API calls"""
    
    def __init__(self):
        self.results = []
        self.base_url = "https://demo.cpvs-services.com"
        
        # Demo API configurations
        self.demo_apis = [
            {
                "name": "Fund-Value-Exp",
                "method": "GET",
                "endpoint": "/fundvalue-nyl-exp/api/fundUnitValues",
                "description": "Fund Value Export API",
                "simulate_success": True,
                "response_time_range": (100, 300)
            },
            {
                "name": "Fund-Value-Reload",
                "method": "GET",
                "endpoint": "/fundvalue-nyl-reload/api/fundUnitValues",
                "description": "Fund Value Reload API",
                "simulate_success": True,
                "response_time_range": (150, 350)
            },
            {
                "name": "LTC_COSTS",
                "method": "GET",
                "endpoint": "/ltc-costs-nyl-exp/api/costs",
                "description": "LTC Costs API",
                "simulate_success": True,
                "response_time_range": (80, 200)
            },
            {
                "name": "LTC-Costs-Load",
                "method": "POST",
                "endpoint": "/ltc-costs-nyl-load/api/costs",
                "description": "LTC Costs Load API",
                "simulate_success": False,  # Simulate one failure
                "response_time_range": (200, 400)
            },
            {
                "name": "Producer-Search-P1.0",
                "method": "GET",
                "endpoint": "/producer-nyl-exp/api/1.0/producerProfile",
                "description": "Producer Search API Version 1.0",
                "simulate_success": True,
                "response_time_range": (120, 280)
            },
            {
                "name": "Producer-Search-withEmail-P1.0",
                "method": "GET",
                "endpoint": "/producer-nyl-exp/api/1.0/producerProfile",
                "description": "Producer Search with Email API Version 1.0",
                "simulate_success": True,
                "response_time_range": (130, 290)
            },
            {
                "name": "Producer-Search-P2.0",
                "method": "GET",
                "endpoint": "/producer-nyl-exp/api/2.0/producerProfile",
                "description": "Producer Search API Version 2.0",
                "simulate_success": True,
                "response_time_range": (110, 270)
            },
            {
                "name": "Producer-Search-withEmail-P2.0",
                "method": "GET",
                "endpoint": "/producer-nyl-exp/api/2.0/producerProfile",
                "description": "Producer Search with Email API Version 2.0",
                "simulate_success": True,
                "response_time_range": (140, 300)
            },
            {
                "name": "Producer-With-Mock",
                "method": "GET",
                "endpoint": "/producer-nyl-exp/api/mock/producerProfile",
                "description": "Producer Mock API",
                "simulate_success": True,
                "response_time_range": (50, 150)
            }
        ]
    
    def simulate_api_call(self, api_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a single API call"""
        name = api_config['name']
        method = api_config['method']
        endpoint = api_config['endpoint']
        url = f"{self.base_url}{endpoint}"
        
        result = {
            'name': name,
            'endpoint': endpoint,
            'method': method,
            'url': url,
            'description': api_config['description'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\ud83d\udd39 Simulating {name} ({method} {url})")
        
        # Simulate network delay
        min_time, max_time = api_config['response_time_range']
        response_time = random.uniform(min_time, max_time)
        time.sleep(response_time / 1000)  # Convert ms to seconds
        
        if api_config['simulate_success']:
            # Simulate successful response
            result.update({
                'status': 'SUCCESS',
                'status_code': 200,
                'response_time_ms': round(response_time, 2),
                'response_size_bytes': random.randint(500, 5000),
                'content_type': 'application/json',
                'response_data': {
                    'status': 'ok',
                    'message': 'Demo data - API working correctly',
                    'data': {
                        'id': random.randint(1000, 9999),
                        'timestamp': datetime.now().isoformat(),
                        'records': random.randint(10, 100)
                    }
                }
            })
            logger.info(f"\u2705 {name}: SUCCESS (Status: 200, Time: {result['response_time_ms']}ms)")
        else:
            # Simulate failure (timeout)
            result.update({
                'status': 'TIMEOUT',
                'error': 'Request timed out - Demo simulation'
            })
            logger.error(f"\u274c {name}: TIMEOUT (Simulated failure)")
        
        return result
    
    def run_all_apis(self) -> List[Dict[str, Any]]:
        """Run all demo API simulations"""
        logger.info(f"\n\ud83c\udf89 Starting DEMO monitoring of {len(self.demo_apis)} APIs")
        logger.info("\u26a0\ufe0f  Note: This is a DEMO - no real APIs are being called\n")
        
        for api in self.demo_apis:
            result = self.simulate_api_call(api)
            self.results.append(result)
            print()  # Blank line for readability
        
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
                'base_url': self.base_url,
                'mode': 'DEMO'
            },
            'detailed_results': sorted(self.results, key=lambda x: x['name'])
        }
        
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary to console"""
        summary = report['summary']
        
        print("\n" + "="*80)
        print(" \ud83c\udfad DEMO MODE - CPVS MONITORING API REPORT")
        print("="*80)
        print(f"\n\u26a0\ufe0f  Mode: {summary['mode']} (Simulated - No real APIs called)")
        print(f"Base URL: {summary['base_url']}")
        print(f"Execution Time: {summary['execution_timestamp']}")
        print(f"\nTotal APIs: {summary['total_apis']}")
        print(f"Successful: \033[92m{summary['successful']}\033[0m")
        print(f"Failed: \033[91m{summary['failed']}\033[0m")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Average Response Time: {summary['average_response_time_ms']} ms")
        
        print("\n" + "-"*80)
        print(" INDIVIDUAL API RESULTS")
        print("-"*80)
        
        for result in report['detailed_results']:
            status_symbol = "\u2713" if result['status'] == 'SUCCESS' else "\u2717"
            status_color = "\033[92m" if result['status'] == 'SUCCESS' else "\033[91m"
            
            print(f"\n{status_symbol} {result['name']}")
            print(f"   Method: {result['method']}")
            print(f"   Endpoint: {result['endpoint']}")
            print(f"   Status: {status_color}{result['status']}\033[0m")
            
            if 'status_code' in result:
                print(f"   HTTP Status: {result['status_code']}")
            if 'response_time_ms' in result:
                print(f"   Response Time: {result['response_time_ms']} ms")
            if 'error' in result:
                print(f"   Error: {result['error']}")
        
        print("\n" + "="*80)
        print("\n\u2705 Demo completed successfully!")
        print("\ud83d\udcca Report saved. You can now test the email functionality with this report.")
        print("\n")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Demo CPVS API Monitor - Simulates API calls without hitting real endpoints'
    )
    parser.add_argument(
        '--output',
        default='demo_report.json',
        help='Output file for JSON report (default: demo_report.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize demo monitor
        monitor = DemoAPIMonitor()
        
        # Run all simulated APIs
        monitor.run_all_apis()
        
        # Generate report
        report = monitor.generate_report()
        
        # Save to file
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\ud83d\udcbe Report saved to {args.output}")
        
        # Print summary
        monitor.print_summary(report)
        
        # Print next steps
        print("\ud83d\ude80 Next Steps:")
        print(f"   1. Review the report: {args.output}")
        print("   2. Test email functionality:")
        print(f"      python email_report.py --report {args.output} --recipients your@email.com \\")
        print("        --sender-email sender@gmail.com --sender-password 'your-password' --attach")
        
        # Exit with appropriate code
        sys.exit(0 if report['summary']['failed'] == 0 else 1)
        
    except Exception as e:
        logger.error(f"\u274c Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

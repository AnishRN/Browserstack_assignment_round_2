"""
BrowserStack Integration Module for Cross-Browser Testing
"""
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests


class BrowserStackConfig:
    """BrowserStack configuration"""
    
    # Default configuration - user should set these environment variables
    USERNAME = os.environ.get('BROWSERSTACK_USERNAME', '')
    ACCESS_KEY = os.environ.get('BROWSERSTACK_ACCESS_KEY', '')
    LOCAL_IDENTIFIER = os.environ.get('BROWSERSTACK_LOCAL_IDENTIFIER', '')
    
    # API endpoints
    API_URL = "https://api.browserstack.com"
    AUTOMATE_URL = f"{API_URL}/automate"
    
    @classmethod
    def is_configured(cls):
        """Check if BrowserStack is properly configured"""
        return bool(cls.USERNAME and cls.ACCESS_KEY)
    
    @classmethod
    def get_credentials(cls):
        """Get BrowserStack credentials"""
        return {
            'username': cls.USERNAME,
            'access_key': cls.ACCESS_KEY
        }


class BrowserStackDriver:
    """BrowserStack WebDriver manager"""
    
    # Browser combinations for testing
    BROWSER_CONFIG = [
        # Desktop browsers
        {
            'browser': 'Chrome',
            'browser_version': 'latest',
            'os': 'Windows',
            'os_version': '10',
            'name': 'Chrome on Windows 10'
        },
        {
            'browser': 'Firefox',
            'browser_version': 'latest',
            'os': 'Windows',
            'os_version': '10',
            'name': 'Firefox on Windows 10'
        },
        {
            'browser': 'Safari',
            'browser_version': 'latest',
            'os': 'macOS',
            'os_version': 'Monterey',
            'name': 'Safari on macOS Monterey'
        },
        # Mobile browsers
        {
            'browser': 'iPhone',
            'device': 'iPhone 14 Pro',
            'os': 'iOS',
            'os_version': '16',
            'name': 'iPhone 14 Pro (iOS 16)'
        },
        {
            'browser': 'Samsung Galaxy',
            'device': 'Samsung Galaxy S22',
            'os': 'Android',
            'os_version': '12',
            'name': 'Samsung Galaxy S22 (Android 12)'
        }
    ]
    
    def __init__(self, config=None):
        self.config = config or BrowserStackDriver.BROWSER_CONFIG[0]
        self.driver = None
    
    def create_driver(self):
        """Create a BrowserStack WebDriver"""
        credentials = BrowserStackConfig.get_credentials()
        
        if not BrowserStackConfig.is_configured():
            raise ValueError("BrowserStack credentials not configured. Set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY environment variables.")
        
        # Build capabilities
        caps = {
            'browserName': self.config.get('browser'),
            'browserVersion': self.config.get('browser_version'),
            'bstack:options': {
                'os': self.config.get('os'),
                'osVersion': self.config.get('os_version'),
                'buildName': 'ElPais Scraper Test',
                'projectName': 'ElPais Article Scraper',
                'sessionName': self.config.get('name', 'Test'),
                'local': False,
                'localIdentifier': BrowserStackConfig.LOCAL_IDENTIFIER,
                'networkLogs': True,
                'consoleLogs': 'errors'
            }
        }
        
        # Add device for mobile
        if 'device' in self.config:
            caps['deviceName'] = self.config['device']
        
        # Create driver
        driver = webdriver.Remote(
            command_executor=f"https://{credentials['username']}:{credentials['access_key']}@hub.browserstack.com/wd/hub",
            desired_capabilities=caps
        )
        
        self.driver = driver
        return driver
    
    def test_url(self, url, timeout=30):
        """Test loading a URL and verify elements"""
        result = {
            'config': self.config.get('name'),
            'success': False,
            'error': None,
            'page_title': None,
            'load_time': None
        }
        
        try:
            driver = self.create_driver()
            
            # Measure load time
            start_time = time.time()
            driver.get(url)
            load_time = time.time() - start_time
            
            # Wait for page to load
            WebDriverWait(driver, timeout).until(
                EC.title_contains('El País') or EC.title_contains('opinión')
            )
            
            result['success'] = True
            result['page_title'] = driver.title
            result['load_time'] = round(load_time, 2)
            
            print(f"✓ {result['config']}: Page loaded successfully in {result['load_time']}s")
            
        except TimeoutException:
            result['error'] = 'Page load timeout'
            print(f"✗ {result['config']}: Page load timeout")
            
        except WebDriverException as e:
            result['error'] = str(e)
            print(f"✗ {result['config']}: {e}")
            
        finally:
            if self.driver:
                self.driver.quit()
        
        return result
    
    def cleanup(self):
        """Clean up driver"""
        if self.driver:
            self.driver.quit()


def run_parallel_tests(url, num_threads=5):
    """
    Run tests on multiple browsers in parallel
    
    Args:
        url: URL to test
        num_threads: Number of parallel threads
    
    Returns:
        List of test results
    """
    # Get browser configs (limited by num_threads)
    configs = BrowserStackDriver.BROWSER_CONFIG[:num_threads]
    
    results = []
    
    print(f"\nRunning parallel tests on {len(configs)} browsers...")
    print("="*60)
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit all tasks
        future_to_config = {}
        for config in configs:
            bs_driver = BrowserStackDriver(config)
            future = executor.submit(bs_driver.test_url, url)
            future_to_config[future] = config
        
        # Collect results
        for future in as_completed(future_to_config):
            config = future_to_config[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    'config': config.get('name'),
                    'success': False,
                    'error': str(e)
                })
    
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    for result in results:
        status = "✓ PASS" if result['success'] else "✗ FAIL"
        print(f"  {status}: {result['config']}")
        if result.get('load_time'):
            print(f"      Load time: {result['load_time']}s")
        if result.get('error'):
            print(f"      Error: {result['error']}")
    
    return results


def run_local_test(url):
    """Run a local test without BrowserStack (for local verification)"""
    print("Running local verification test...")
    
    try:
        # Use local Chrome/Firefox
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        start_time = time.time()
        driver.get(url)
        load_time = time.time() - start_time
        
        title = driver.title
        driver.quit()
        
        print(f"✓ Local test successful!")
        print(f"  Page title: {title}")
        print(f"  Load time: {round(load_time, 2)}s")
        
        return {
            'success': True,
            'page_title': title,
            'load_time': round(load_time, 2)
        }
        
    except Exception as e:
        print(f"✗ Local test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def verify_browserstack_connection():
    """Verify BrowserStack API connection"""
    if not BrowserStackConfig.is_configured():
        return False, "BrowserStack credentials not configured"
    
    credentials = BrowserStackConfig.get_credentials()
    
    try:
        # Test API connection
        response = requests.get(
            f"{BrowserStackConfig.AUTOMATE_URL}/plan.json",
            auth=(credentials['username'], credentials['access_key']),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Connected. Available runs: {data.get('automate_plan', {}).get('available_runs', 'N/A')}"
        else:
            return False, f"API error: {response.status_code}"
            
    except Exception as e:
        return False, f"Connection error: {str(e)}"


if __name__ == "__main__":
    # Test BrowserStack connection
    print("Testing BrowserStack connection...")
    connected, message = verify_browserstack_connection()
    print(f"Connection status: {message}")

"""
API Hunter - Capture and extract JSON API calls
"""

from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtCore import QObject
import requests
import pandas as pd
import json


class APIRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Intercepts network requests to capture API calls
    
    NOTE: This is a stubbed implementation. Full implementation would require:
    1. QWebEngineProfile setup with custom URL scheme handler
    2. Network access manager to capture responses
    3. More complex signal/slot connections
    
    For production use, consider using browser DevTools protocol or
    a headless browser library like Playwright for complete network monitoring.
    """
    
    def __init__(self, api_hunter):
        super().__init__()
        self.api_hunter = api_hunter
    
    def interceptRequest(self, info):
        """Intercept network requests"""
        url = info.requestUrl().toString()
        
        # Check if this looks like an API call
        if self.is_api_request(url):
            self.api_hunter.add_api_url(url)
    
    def is_api_request(self, url):
        """Determine if URL is likely an API endpoint"""
        # Simple heuristics - can be improved
        api_indicators = ['/api/', '/json', '/data/', 'format=json', 
                         'ajax', '/v1/', '/v2/', '/rest/']
        
        url_lower = url.lower()
        return any(indicator in url_lower for indicator in api_indicators)


class APIHunter:
    """Captures and analyzes JSON API calls from web pages"""
    
    def __init__(self):
        self.captured_apis = set()
        self.interceptor = None
    
    def setup_for_page(self, web_page):
        """
        Setup API hunting for a web page
        
        Args:
            web_page: QWebEnginePage instance
        
        NOTE: This is a basic stub. Full implementation requires:
        - QWebEngineProfile.setUrlRequestInterceptor()
        - Custom response capture mechanism
        - Signal connections for network events
        
        For now, this demonstrates the structure. In production:
        1. Use QWebEngineProfile.defaultProfile().setUrlRequestInterceptor()
        2. Implement proper response body capture
        3. Consider using Chrome DevTools Protocol for full control
        """
        # Stub implementation
        # In production, you would do:
        # profile = web_page.profile()
        # self.interceptor = APIRequestInterceptor(self)
        # profile.setUrlRequestInterceptor(self.interceptor)
        
        # For demonstration, we'll add some mock API endpoints
        # Real implementation would capture these from actual network traffic
        pass
    
    def add_api_url(self, url):
        """Add a captured API URL"""
        self.captured_apis.add(url)
    
    def get_captured_apis(self):
        """Get list of captured API URLs"""
        return list(self.captured_apis)
    
    def fetch_api_data(self, url):
        """
        Fetch data from an API endpoint
        
        Args:
            url: API endpoint URL
            
        Returns:
            pandas DataFrame with API data
        """
        try:
            # Make HTTP request
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            # Convert to DataFrame
            df = self.json_to_dataframe(data)
            
            return df
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            raise Exception(f"Failed to fetch API: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON parse failed: {e}")
            raise Exception("Response is not valid JSON")
        except Exception as e:
            print(f"API fetch error: {e}")
            raise
    
    def json_to_dataframe(self, data):
        """
        Convert JSON data to pandas DataFrame
        
        Handles various JSON structures:
        - List of objects: directly to DataFrame
        - Single object: wrap in list
        - Nested structure: try to find array data
        """
        if isinstance(data, list):
            # List of objects - ideal case
            if data and isinstance(data[0], dict):
                return pd.DataFrame(data)
            else:
                # List of primitives
                return pd.DataFrame({'value': data})
        
        elif isinstance(data, dict):
            # Try to find array data in dict
            # Common patterns: data.results, data.items, data.data, etc.
            for key in ['results', 'items', 'data', 'list', 'records']:
                if key in data and isinstance(data[key], list):
                    return self.json_to_dataframe(data[key])
            
            # If no array found, convert dict to single-row DataFrame
            # Flatten nested dicts
            flat_data = self.flatten_dict(data)
            return pd.DataFrame([flat_data])
        
        else:
            # Primitive value
            return pd.DataFrame({'value': [data]})
    
    def flatten_dict(self, d, parent_key='', sep='_'):
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert list to string representation
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        
        return dict(items)
    
    def clear_captured_apis(self):
        """Clear all captured APIs"""
        self.captured_apis.clear()
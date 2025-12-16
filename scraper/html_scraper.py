"""
HTML Scraper - Extract data from HTML content
"""

from bs4 import BeautifulSoup
import pandas as pd
import re

# Fail-fast check for lxml parser at module load time
try:
    import lxml
except ImportError:
    raise RuntimeError("Required parser 'lxml' is not installed. Install it with: pip install lxml")


class HTMLScraper:
    """Scrapes HTML content and extracts structured data"""
    
    def __init__(self):
        self.soup = None
    
    def scrape(self, html_content, config):
        """
        Main scraping method
        
        Args:
            html_content: HTML string
            config: Dictionary with scraping configuration
            
        Returns:
            pandas DataFrame with scraped data
        """
        self.soup = BeautifulSoup(html_content, "lxml")
        
        all_data = []
        
        # Extract different types of data based on config
        if config.get('tables', False):
            all_data.extend(self.extract_tables())
        
        if config.get('text', False):
            all_data.extend(self.extract_text())
        
        if config.get('links', False):
            all_data.extend(self.extract_links())
        
        if config.get('images', False):
            all_data.extend(self.extract_images())
        
        # Convert to DataFrame
        if not all_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_data)
        
        # Apply filters
        df = self.apply_filters(df, config)
        
        # Remove duplicates if requested
        if config.get('remove_duplicates', False):
            df = df.drop_duplicates()
        
        return df
    
    def extract_tables(self):
        """Extract all HTML tables"""
        data = []
        tables = self.soup.find_all('table')
        
        for table_idx, table in enumerate(tables):
            # Try to find headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            else:
                # Try first row
                first_row = table.find('tr')
                if first_row:
                    potential_headers = first_row.find_all('th')
                    if potential_headers:
                        headers = [th.get_text(strip=True) for th in potential_headers]
            
            # Extract rows
            rows = table.find_all('tr')
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = {
                        'type': 'table',
                        'table_index': table_idx,
                        'row_index': row_idx
                    }
                    
                    # Add cell data
                    for cell_idx, cell in enumerate(cells):
                        if headers and cell_idx < len(headers):
                            col_name = headers[cell_idx]
                        else:
                            col_name = f'column_{cell_idx}'
                        
                        row_data[col_name] = cell.get_text(strip=True)
                    
                    data.append(row_data)
        
        return data
    
    def extract_text(self):
        """Extract text content from paragraphs and main content"""
        data = []
        
        # Extract from paragraphs
        paragraphs = self.soup.find_all('p')
        for idx, p in enumerate(paragraphs):
            text = p.get_text(strip=True)
            if text:
                data.append({
                    'type': 'text',
                    'index': idx,
                    'content': text,
                    'tag': 'p'
                })
        
        # Extract from headings
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            headings = self.soup.find_all(heading_tag)
            for idx, heading in enumerate(headings):
                text = heading.get_text(strip=True)
                if text:
                    data.append({
                        'type': 'text',
                        'index': idx,
                        'content': text,
                        'tag': heading_tag
                    })
        
        # Extract from divs with substantial text
        divs = self.soup.find_all('div')
        for idx, div in enumerate(divs):
            # Only include divs with direct text (not nested)
            text = div.get_text(strip=True)
            if text and len(text) > 50:  # Minimum length threshold
                data.append({
                    'type': 'text',
                    'index': idx,
                    'content': text,
                    'tag': 'div'
                })
        
        return data
    
    def extract_links(self):
        """Extract all links from the page"""
        data = []
        links = self.soup.find_all('a', href=True)
        
        for idx, link in enumerate(links):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            title = link.get('title', '')
            
            data.append({
                'type': 'link',
                'index': idx,
                'text': text,
                'url': href,
                'title': title
            })
        
        return data
    
    def extract_images(self):
        """Extract all images from the page"""
        data = []
        images = self.soup.find_all('img', src=True)
        
        for idx, img in enumerate(images):
            src = img.get('src', '')
            alt = img.get('alt', '')
            title = img.get('title', '')
            
            data.append({
                'type': 'image',
                'index': idx,
                'src': src,
                'alt': alt,
                'title': title
            })
        
        return data
    
    def apply_filters(self, df, config):
        """Apply keyword and regex filters to DataFrame"""
        if df.empty:
            return df
        
        # Keyword filter
        keyword = config.get('keyword_filter', '').strip()
        if keyword:
            # Split by comma for multiple keywords
            keywords = [k.strip() for k in keyword.split(',')]
            
            # Create filter mask
            mask = pd.Series([False] * len(df))
            
            for kw in keywords:
                if kw:
                    # Check all columns for keyword
                    for col in df.columns:
                        if df[col].dtype == 'object':  # Only search in string columns
                            mask |= df[col].astype(str).str.contains(
                                kw, case=False, na=False, regex=False)
            
            df = df[mask]
        
        # Regex filter
        regex_pattern = config.get('regex_filter', '').strip()
        if regex_pattern:
            try:
                # Create filter mask
                mask = pd.Series([False] * len(df))
                
                # Check all columns for regex match
                for col in df.columns:
                    if df[col].dtype == 'object':  # Only search in string columns
                        mask |= df[col].astype(str).str.contains(
                            regex_pattern, case=False, na=False, regex=True)
                
                df = df[mask]
            except re.error as e:
                print(f"Invalid regex pattern: {e}")
        
        return df
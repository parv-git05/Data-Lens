"""
Icons - Base64 encoded SVG icons for the application
File: utils/icons.py
"""

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import Qt


class Icons:
    """Provides base64-encoded SVG icons for the application"""
    
    # Simple SVG icons encoded as inline strings
    # These are clean, scalable vector graphics that work at any size
    ICONS = {
        'back': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 18L9 12L15 6" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'forward': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18L15 12L9 6" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'reload': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21.5 2V8H15.5" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2.5 22V16H8.5" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M19.5 8.5C18.5 6 16 4 13 3.5C8.5 2.5 4 5 2.5 9.5" stroke="#333333" stroke-width="2" stroke-linecap="round"/>
                <path d="M4.5 15.5C5.5 18 8 20 11 20.5C15.5 21.5 20 19 21.5 14.5" stroke="#333333" stroke-width="2" stroke-linecap="round"/>
            </svg>
        ''',
        
        'home': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 22V12H15V22" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'bookmark': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'notes': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 13H8" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 17H8" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 9H8" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'bookmarks_menu': '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 19.5C4 18.837 4.26339 18.2011 4.73223 17.7322C5.20107 17.2634 5.83696 17 6.5 17H20" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M6.5 2H20V22H6.5C5.83696 22 5.20107 21.7366 4.73223 21.2678C4.26339 20.7989 4 20.163 4 19.5V4.5C4 3.83696 4.26339 3.20107 4.73223 2.73223C5.20107 2.26339 5.83696 2 6.5 2Z" stroke="#333333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',
        
        'scrape': '''
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="11" cy="11" r="8" stroke="white" stroke-width="2"/>
                <path d="M21 21L16.65 16.65" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M11 8V14" stroke="white" stroke-width="2" stroke-linecap="round"/>
                <path d="M8 11H14" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
        '''
    }
    
    @staticmethod
    def svg_to_pixmap(svg_string, width=24, height=24):
        """
        Convert SVG string to QPixmap
        
        This method takes an SVG string and renders it to a QPixmap
        at the specified dimensions. The pixmap can then be used to
        create QIcons for buttons and actions.
        
        Args:
            svg_string: SVG XML string
            width: Target width in pixels
            height: Target height in pixels
            
        Returns:
            QPixmap object containing the rendered SVG
        """
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtGui import QPainter
        
        # Create SVG renderer from string
        svg_bytes = QByteArray(svg_string.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        # Create pixmap with transparency
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)  # Transparent background (ARGB)
        
        # Render SVG onto pixmap
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
    
    @staticmethod
    def get_icon(name, width=24, height=24):
        """
        Get QIcon for the given icon name
        
        This is the main method to use when you need an icon.
        It looks up the icon by name, renders it to the specified size,
        and returns a QIcon that can be used in buttons, actions, etc.
        
        Args:
            name: Icon name (must be in ICONS dictionary)
            width: Icon width in pixels (default 24)
            height: Icon height in pixels (default 24)
            
        Returns:
            QIcon object, or empty QIcon if name not found
            
        Example usage:
            back_icon = Icons.get_icon("back")
            back_button.setIcon(back_icon)
            
            large_scrape_icon = Icons.get_icon("scrape", 32, 32)
            scrape_button.setIcon(large_scrape_icon)
        """
        if name in Icons.ICONS:
            svg = Icons.ICONS[name]
            pixmap = Icons.svg_to_pixmap(svg, width, height)
            return QIcon(pixmap)
        else:
            # Return empty icon if not found
            print(f"Warning: Icon '{name}' not found")
            return QIcon()
    
    @staticmethod
    def get_available_icons():
        """
        Get list of all available icon names
        
        Returns:
            List of icon names that can be used with get_icon()
        """
        return list(Icons.ICONS.keys())
    
    @staticmethod
    def add_custom_icon(name, svg_string):
        """
        Add a custom icon at runtime
        
        This allows you to add new icons without modifying this file.
        Useful for plugins or dynamic icon generation.
        
        Args:
            name: Icon name to register
            svg_string: SVG XML string
            
        Example:
            custom_svg = '<svg>...</svg>'
            Icons.add_custom_icon('my_icon', custom_svg)
            icon = Icons.get_icon('my_icon')
        """
        Icons.ICONS[name] = svg_string
        print(f"Added custom icon: {name}")
"""
MainWindow - Core browser window with tabbed interface
File: ui/main_window.py

This is the main application window that handles:
- Multi-tab browsing
- Navigation toolbar
- URL bar with search
- Bookmarks and notes
- Floating scrape button
- Integration with scrape panel
"""

from PyQt5.QtWidgets import (QMainWindow, QToolBar, QLineEdit, QAction, 
                             QTabWidget, QWidget, QVBoxLayout, QPushButton,
                             QMessageBox)
from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView

from ui.scrape_panel import ScrapePanel
from ui.notes_dialog import NotesDialog
from ui.bookmarks_manager import BookmarksManager
from utils.icons import Icons
import os


class MainWindow(QMainWindow):
    """
    Main browser window with navigation and scraping capabilities
    
    This class manages the entire application window including:
    - Tabbed web browser interface
    - Navigation controls
    - Bookmarks and notes
    - Scraping functionality
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataLens - Web Scraping Browser")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize managers
        self.bookmarks_manager = BookmarksManager()
        self.notes_dialog = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load homepage in first tab
        self.add_new_tab(self.get_homepage_url(), "Home")
    
    def setup_ui(self):
        """Initialize all UI components"""
        # Create tab widget for multiple browser tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        
        # Connect tab signals
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        
        # Set tabs as central widget
        self.setCentralWidget(self.tabs)
        
        # Create navigation toolbar
        self.create_navbar()
        
        # Create scrape panel (initially hidden)
        self.scrape_panel = ScrapePanel(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.scrape_panel)
        self.scrape_panel.hide()
        
        # Create floating scrape button
        self.create_floating_scrape_button()
    
    def create_navbar(self):
        """Create navigation toolbar with buttons and URL bar"""
        navbar = QToolBar("Navigation")
        navbar.setIconSize(QSize(24, 24))
        navbar.setMovable(False)
        self.addToolBar(navbar)
        
        # Back button
        back_btn = QAction(Icons.get_icon("back"), "Back", self)
        back_btn.setStatusTip("Go back to previous page")
        back_btn.triggered.connect(lambda: self.current_webview().back())
        navbar.addAction(back_btn)
        
        # Forward button
        forward_btn = QAction(Icons.get_icon("forward"), "Forward", self)
        forward_btn.setStatusTip("Go forward to next page")
        forward_btn.triggered.connect(lambda: self.current_webview().forward())
        navbar.addAction(forward_btn)
        
        # Reload button
        reload_btn = QAction(Icons.get_icon("reload"), "Reload", self)
        reload_btn.setStatusTip("Reload current page")
        reload_btn.triggered.connect(lambda: self.current_webview().reload())
        navbar.addAction(reload_btn)
        
        # Home button
        home_btn = QAction(Icons.get_icon("home"), "Home", self)
        home_btn.setStatusTip("Go to homepage")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        
        # Separator
        navbar.addSeparator()
        
        # URL bar (line edit for entering URLs)
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setPlaceholderText("Enter URL or search...")
        navbar.addWidget(self.url_bar)
        
        # Separator
        navbar.addSeparator()
        
        # Bookmark button
        bookmark_btn = QAction(Icons.get_icon("bookmark"), "Bookmark", self)
        bookmark_btn.setStatusTip("Bookmark this page")
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)
        
        # Notes button
        notes_btn = QAction(Icons.get_icon("notes"), "Notes", self)
        notes_btn.setStatusTip("Open notes for this page")
        notes_btn.triggered.connect(self.show_notes)
        navbar.addAction(notes_btn)
        
        # Bookmarks menu button
        bookmarks_menu_btn = QAction(Icons.get_icon("bookmarks_menu"), "View Bookmarks", self)
        bookmarks_menu_btn.setStatusTip("View all bookmarks")
        bookmarks_menu_btn.triggered.connect(self.show_bookmarks)
        navbar.addAction(bookmarks_menu_btn)
    
    def create_floating_scrape_button(self):
        """Create floating scrape button that overlays the browser"""
        self.scrape_float_btn = QPushButton(self)
        self.scrape_float_btn.setIcon(Icons.get_icon("scrape", 32, 32))
        self.scrape_float_btn.setIconSize(QSize(32, 32))
        self.scrape_float_btn.setFixedSize(60, 60)
        
        # Style the button with rounded corners and blue background
        self.scrape_float_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 30px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        self.scrape_float_btn.clicked.connect(self.toggle_scrape_panel)
        self.scrape_float_btn.setToolTip("Open Scrape Panel (Extract web data)")
        
        # Position in bottom-right corner
        self.position_floating_button()
    
    def position_floating_button(self):
        """Position floating button in bottom-right corner"""
        x = self.width() - 80
        y = self.height() - 100
        self.scrape_float_btn.move(x, y)
        self.scrape_float_btn.raise_()  # Bring to front
    
    def resizeEvent(self, event):
        """Handle window resize - reposition floating button"""
        super().resizeEvent(event)
        if hasattr(self, 'scrape_float_btn'):
            self.position_floating_button()
    
    def add_new_tab(self, qurl=None, label="New Tab"):
        """
        Add a new browser tab
        
        Args:
            qurl: URL to load (can be QUrl or string)
            label: Tab label text
            
        Returns:
            QWebEngineView instance for the new tab
        """
        # Default to homepage if no URL provided
        if qurl is None:
            qurl = QUrl(self.get_homepage_url())
        
        # Convert string to QUrl if needed
        if isinstance(qurl, str):
            qurl = QUrl(qurl)
        
        # Create web view
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Add tab
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Connect signals for this browser
        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.update_urlbar(qurl, browser)
        )
        browser.loadFinished.connect(
            lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()[:30])
        )
        browser.loadFinished.connect(lambda: self.update_title())
        
        return browser
    
    def tab_open_doubleclick(self, i):
        """Handle double click on tab bar to open new tab"""
        if i == -1:  # Clicked on empty area of tab bar
            self.add_new_tab()
    
    def current_tab_changed(self, i):
        """Handle tab change - update URL bar and title"""
        if i >= 0:
            qurl = self.current_webview().url()
            self.update_urlbar(qurl, self.current_webview())
            self.update_title()
    
    def close_current_tab(self, i):
        """Close a tab (keep at least one open)"""
        if self.tabs.count() < 2:
            return  # Keep at least one tab open
        
        self.tabs.removeTab(i)
    
    def current_webview(self):
        """Get the currently active web view"""
        return self.tabs.currentWidget()
    
    def update_urlbar(self, qurl, browser=None):
        """Update URL bar with current page URL"""
        # Only update if this is the current tab
        if browser != self.current_webview():
            return
        
        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)
    
    def update_title(self):
        """Update window title with current page title"""
        title = self.current_webview().page().title()
        self.setWindowTitle(f"{title} - DataLens")
    
    def navigate_to_url(self):
        """Navigate to URL entered in address bar"""
        url = self.url_bar.text().strip()
        
        if not url:
            return
        
        # Check if it's a search query or URL
        if not url.startswith("http") and not url.startswith("file://"):
            # Check if it looks like a domain (has dot, no spaces)
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                # Treat as Google search query
                url = f"https://www.google.com/search?q={url}"
        
        self.current_webview().setUrl(QUrl(url))
    
    def navigate_home(self):
        """Navigate to home page"""
        self.current_webview().setUrl(QUrl(self.get_homepage_url()))

        """
MainWindow - Part 2: Homepage and Feature Methods
File: ui/main_window.py (continuation)

IMPORTANT: This is the continuation of main_window.py
Append this code to the end of Part 1 (after navigate_home method)
"""

    def get_homepage_url(self):
        """
        Get homepage URL (local HTML file)
        
        Returns path to assets/home.html, creating it if it doesn't exist.
        """
        home_path = os.path.abspath("assets/home.html")
        
        if os.path.exists(home_path):
            return f"file:///{home_path}"
        else:
            # Create default home page if it doesn't exist
            self.create_default_homepage()
            return f"file:///{home_path}"
    
    def create_default_homepage(self):
        """Create default homepage HTML with Google-style search"""
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>DataLens Home</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow-x: hidden;
        }
        
        .container {
            text-align: center;
            color: white;
            max-width: 800px;
            padding: 20px;
        }
        
        h1 {
            font-size: 4em;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeIn 1s ease-in;
        }
        
        .search-container {
            margin: 30px auto;
            max-width: 600px;
        }
        
        .search-box {
            background: white;
            border-radius: 28px;
            padding: 14px 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            transition: transform 0.2s;
        }
        
        .search-box:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        
        .search-icon {
            font-size: 20px;
            color: #666;
            margin-right: 12px;
        }
        
        input {
            flex: 1;
            border: none;
            outline: none;
            font-size: 16px;
            padding: 8px;
            color: #333;
        }
        
        input::placeholder {
            color: #999;
        }
        
        .subtitle {
            margin-top: 30px;
            font-size: 1.3em;
            opacity: 0.95;
            animation: fadeIn 1.5s ease-in;
        }
        
        .features {
            margin-top: 60px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            animation: fadeIn 2s ease-in;
        }
        
        .feature {
            background: rgba(255,255,255,0.15);
            padding: 30px 20px;
            border-radius: 16px;
            backdrop-filter: blur(10px);
            transition: all 0.3s;
            cursor: default;
        }
        
        .feature:hover {
            background: rgba(255,255,255,0.25);
            transform: translateY(-5px);
        }
        
        .feature-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .feature-text {
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .tip {
            margin-top: 50px;
            font-size: 0.9em;
            opacity: 0.8;
            animation: fadeIn 2.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 DataLens</h1>
        
        <div class="search-container">
            <div class="search-box">
                <span class="search-icon">🔎</span>
                <input type="text" 
                       id="searchInput"
                       placeholder="Search the web or enter URL..." 
                       autofocus>
            </div>
        </div>
        
        <div class="subtitle">
            Web Scraping Browser for Data Scientists
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-text">Extract Tables</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🔗</div>
                <div class="feature-text">Capture Links</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📝</div>
                <div class="feature-text">Scrape Text</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🖼️</div>
                <div class="feature-text">Get Images</div>
            </div>
        </div>
        
        <div class="tip">
            💡 Tip: Click the blue floating button (bottom-right) to start scraping any page
        </div>
    </div>
    
    <script>
        // Handle search on Enter key
        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const query = this.value.trim();
                if (query) {
                    // Check if it looks like a URL
                    if (query.includes('.') && !query.includes(' ')) {
                        // Add https if no protocol
                        if (!query.startsWith('http')) {
                            window.location.href = 'https://' + query;
                        } else {
                            window.location.href = query;
                        }
                    } else {
                        // Google search
                        window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(query);
                    }
                }
            }
        });
    </script>
</body>
</html>"""
        
        # Create assets directory and save homepage
        os.makedirs("assets", exist_ok=True)
        try:
            with open("assets/home.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Created default homepage: assets/home.html")
        except Exception as e:
            print(f"Error creating homepage: {e}")
    
    def toggle_scrape_panel(self):
        """Toggle scrape panel visibility"""
        if self.scrape_panel.isVisible():
            self.scrape_panel.hide()
        else:
            self.scrape_panel.show()
            # Pass current webview to scrape panel
            self.scrape_panel.set_webview(self.current_webview())
    
    def add_bookmark(self):
        """Add current page to bookmarks"""
        try:
            url = self.current_webview().url().toString()
            title = self.current_webview().page().title()
            
            if self.bookmarks_manager.add_bookmark(url, title):
                QMessageBox.information(
                    self, 
                    "Bookmark Added", 
                    f"✅ Added to bookmarks:\n\n{title}"
                )
            else:
                QMessageBox.information(
                    self,
                    "Already Bookmarked",
                    "This page is already in your bookmarks!"
                )
        except Exception as e:
            print(f"Error adding bookmark: {e}")
            QMessageBox.warning(
                self, 
                "Error", 
                "Failed to add bookmark. Please try again."
            )
    
    def show_bookmarks(self):
        """Show bookmarks dialog"""
        self.bookmarks_manager.show_bookmarks_dialog(self)
    
    def show_notes(self):
        """Show notes dialog for current page"""
        try:
            url = self.current_webview().url().toString()
            
            # Create notes dialog if it doesn't exist
            if self.notes_dialog is None:
                self.notes_dialog = NotesDialog(self)
            
            # Load notes for current URL and show dialog
            self.notes_dialog.load_notes(url)
            self.notes_dialog.exec_()
            
        except Exception as e:
            print(f"Error showing notes: {e}")
            QMessageBox.warning(
                self,
                "Error",
                "Failed to open notes. Please try again."
            )


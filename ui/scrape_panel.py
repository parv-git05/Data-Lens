"""
Scrape Panel - Side panel for web scraping controls
"""

from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QCheckBox, QPushButton, QLabel, 
                             QLineEdit, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QListWidget, QTextEdit,
                             QProgressBar, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView

from scraper.html_scraper import HTMLScraper
from scraper.api_hunter import APIHunter
from utils.recipe_manager import RecipeManager
import pandas as pd
import traceback


class ScrapeThread(QThread):
    """Thread for performing scraping operations"""
    finished = pyqtSignal(object)  # Emits DataFrame or error
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, webview, config):
        super().__init__()
        self.webview = webview
        self.config = config
    
    def run(self):
        """Run scraping in background thread"""
        try:
            self.progress.emit("Retrieving page HTML...")
            
            # Get HTML content (this is synchronous in thread context)
            scraper = HTMLScraper()
            
            # We'll use a callback approach
            html_content = [None]
            
            def html_callback(html):
                html_content[0] = html
            
            # Request HTML from main thread
            self.webview.page().toHtml(html_callback)
            
            # Wait for HTML (simple polling - in production, use proper sync)
            import time
            timeout = 10
            elapsed = 0
            while html_content[0] is None and elapsed < timeout:
                time.sleep(0.1)
                elapsed += 0.1
            
            if html_content[0] is None:
                raise Exception("Timeout waiting for HTML content")
            
            self.progress.emit("Parsing HTML...")
            
            # Scrape data
            df = scraper.scrape(html_content[0], self.config)
            
            self.progress.emit(f"Scraped {len(df)} rows")
            
            self.finished.emit(df)
            
        except Exception as e:
            print(f"Scrape error: {traceback.format_exc()}")
            self.error.emit(str(e))


class ScrapePanel(QDockWidget):
    """Dockable scrape panel with all scraping controls"""
    
    def __init__(self, parent=None):
        super().__init__("Scrape Panel", parent)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.setMinimumWidth(400)
        
        self.webview = None
        self.current_df = None
        self.api_hunter = APIHunter()
        self.recipe_manager = RecipeManager()
        self.scrape_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup scrape panel UI"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(main_widget)
        self.setWidget(scroll)
        
        # Section 1: What to Scrape
        scrape_group = QGroupBox("What to Scrape")
        scrape_layout = QVBoxLayout()
        
        self.cb_tables = QCheckBox("Extract Tables")
        self.cb_tables.setChecked(True)
        self.cb_text = QCheckBox("Extract Text Content")
        self.cb_links = QCheckBox("Extract Links")
        self.cb_images = QCheckBox("Extract Images")
        
        scrape_layout.addWidget(self.cb_tables)
        scrape_layout.addWidget(self.cb_text)
        scrape_layout.addWidget(self.cb_links)
        scrape_layout.addWidget(self.cb_images)
        scrape_group.setLayout(scrape_layout)
        main_layout.addWidget(scrape_group)
        
        # Section 2: Dynamic Content & API
        dynamic_group = QGroupBox("Dynamic Content & API")
        dynamic_layout = QVBoxLayout()
        
        self.cb_auto_scroll = QCheckBox("Auto-Scroll (Infinite Scroll)")
        self.cb_auto_scroll.setToolTip("Automatically scroll page to load all content")
        dynamic_layout.addWidget(self.cb_auto_scroll)
        
        dynamic_layout.addWidget(QLabel("API Hunter (JSON Endpoints):"))
        self.api_list = QListWidget()
        self.api_list.setMaximumHeight(100)
        self.api_list.itemDoubleClicked.connect(self.fetch_api_data)
        dynamic_layout.addWidget(self.api_list)
        
        btn_refresh_api = QPushButton("Refresh API List")
        btn_refresh_api.clicked.connect(self.refresh_api_list)
        dynamic_layout.addWidget(btn_refresh_api)
        
        dynamic_group.setLayout(dynamic_layout)
        main_layout.addWidget(dynamic_group)
        
        # Section 3: Filters & Cleanup
        filter_group = QGroupBox("Filters & Cleanup")
        filter_layout = QVBoxLayout()
        
        filter_layout.addWidget(QLabel("Keyword Filter:"))
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Enter keywords to include (comma-separated)")
        filter_layout.addWidget(self.keyword_input)
        
        filter_layout.addWidget(QLabel("Regex Filter:"))
        self.regex_input = QLineEdit()
        self.regex_input.setPlaceholderText("Enter regex pattern")
        filter_layout.addWidget(self.regex_input)
        
        self.cb_remove_duplicates = QCheckBox("Remove Duplicate Rows")
        self.cb_remove_duplicates.setChecked(True)
        filter_layout.addWidget(self.cb_remove_duplicates)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Scrape button
        self.btn_scrape = QPushButton("🔍 Start Scraping")
        self.btn_scrape.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_scrape.clicked.connect(self.start_scraping)
        main_layout.addWidget(self.btn_scrape)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        # Section 4: Preview & Export
        preview_group = QGroupBox("Data Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(300)
        preview_layout.addWidget(self.preview_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.clicked.connect(lambda: self.export_data("csv"))
        self.btn_export_csv.setEnabled(False)
        
        self.btn_export_json = QPushButton("Export JSON")
        self.btn_export_json.clicked.connect(lambda: self.export_data("json"))
        self.btn_export_json.setEnabled(False)
        
        self.btn_export_excel = QPushButton("Export Excel")
        self.btn_export_excel.clicked.connect(lambda: self.export_data("excel"))
        self.btn_export_excel.setEnabled(False)
        
        export_layout.addWidget(self.btn_export_csv)
        export_layout.addWidget(self.btn_export_json)
        export_layout.addWidget(self.btn_export_excel)
        
        preview_layout.addLayout(export_layout)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)
        
        # Recipe Management
        recipe_layout = QHBoxLayout()
        
        self.btn_save_recipe = QPushButton("Save Recipe")
        self.btn_save_recipe.clicked.connect(self.save_recipe)
        
        self.btn_load_recipe = QPushButton("Load Recipe")
        self.btn_load_recipe.clicked.connect(self.load_recipe)
        
        recipe_layout.addWidget(self.btn_save_recipe)
        recipe_layout.addWidget(self.btn_load_recipe)
        
        main_layout.addLayout(recipe_layout)
        
        # Add stretch at bottom
        main_layout.addStretch()
    
    def set_webview(self, webview):
        """Set the current webview to scrape"""
        self.webview = webview
        
        # Setup API hunter for this webview
        if webview:
            self.api_hunter.setup_for_page(webview.page())
    
    def start_scraping(self):
        """Start the scraping process"""
        if not self.webview:
            QMessageBox.warning(self, "No Page", 
                               "No web page is loaded")
            return
        
        # Get configuration
        config = self.get_scrape_config()
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.btn_scrape.setEnabled(False)
        self.status_label.setText("Scraping in progress...")
        
        # Start scraping thread
        self.scrape_thread = ScrapeThread(self.webview, config)
        self.scrape_thread.finished.connect(self.scraping_finished)
        self.scrape_thread.error.connect(self.scraping_error)
        self.scrape_thread.progress.connect(self.update_progress)
        self.scrape_thread.start()
    
    def get_scrape_config(self):
        """Get current scraping configuration"""
        return {
            'tables': self.cb_tables.isChecked(),
            'text': self.cb_text.isChecked(),
            'links': self.cb_links.isChecked(),
            'images': self.cb_images.isChecked(),
            'auto_scroll': self.cb_auto_scroll.isChecked(),
            'keyword_filter': self.keyword_input.text(),
            'regex_filter': self.regex_input.text(),
            'remove_duplicates': self.cb_remove_duplicates.isChecked()
        }
    
    def update_progress(self, message):
        """Update progress message"""
        self.status_label.setText(message)
    
    def scraping_finished(self, df):
        """Handle scraping completion"""
        self.progress_bar.setVisible(False)
        self.btn_scrape.setEnabled(True)
        
        if df is not None and not df.empty:
            self.current_df = df
            self.display_preview(df)
            self.status_label.setText(f"✅ Successfully scraped {len(df)} rows")
            
            # Enable export buttons
            self.btn_export_csv.setEnabled(True)
            self.btn_export_json.setEnabled(True)
            self.btn_export_excel.setEnabled(True)
        else:
            self.status_label.setText("⚠️ No data found")
            QMessageBox.information(self, "No Data", 
                                   "No data was found matching your criteria")
    
    def scraping_error(self, error_msg):
        """Handle scraping error"""
        self.progress_bar.setVisible(False)
        self.btn_scrape.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_msg}")
        
        QMessageBox.critical(self, "Scraping Error", 
                            f"An error occurred while scraping:\n{error_msg}")
    
    def display_preview(self, df):
        """Display DataFrame in preview table"""
        # Set up table
        self.preview_table.setRowCount(min(len(df), 100))  # Show max 100 rows
        self.preview_table.setColumnCount(len(df.columns))
        self.preview_table.setHorizontalHeaderLabels(df.columns.tolist())
        
        # Fill table
        for i in range(min(len(df), 100)):
            for j, col in enumerate(df.columns):
                value = str(df.iloc[i, j])
                item = QTableWidgetItem(value)
                self.preview_table.setItem(i, j, item)
        
        self.preview_table.resizeColumnsToContents()
    
    def export_data(self, format_type):
        """Export scraped data"""
        if self.current_df is None:
            return
        
        # Get save file path
        if format_type == "csv":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export CSV", "data/scraped_data.csv", 
                "CSV Files (*.csv)")
        elif format_type == "json":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export JSON", "data/scraped_data.json", 
                "JSON Files (*.json)")
        elif format_type == "excel":
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Excel", "data/scraped_data.xlsx", 
                "Excel Files (*.xlsx)")
        else:
            return
        
        if not file_path:
            return
        
        try:
            # Export data
            if format_type == "csv":
                self.current_df.to_csv(file_path, index=False)
            elif format_type == "json":
                self.current_df.to_json(file_path, orient='records', indent=2)
            elif format_type == "excel":
                self.current_df.to_excel(file_path, index=False, engine='openpyxl')
            
            QMessageBox.information(self, "Export Successful", 
                                   f"Data exported to:\n{file_path}")
        except Exception as e:
            print(f"Export error: {traceback.format_exc()}")
            QMessageBox.critical(self, "Export Failed", 
                                f"Failed to export data:\n{str(e)}")
    
    def save_recipe(self):
        """Save current scraping configuration as recipe"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Recipe", "data/recipe.json", 
            "Recipe Files (*.json)")
        
        if file_path:
            config = self.get_scrape_config()
            if self.recipe_manager.save_recipe(file_path, config):
                QMessageBox.information(self, "Recipe Saved", 
                                       f"Recipe saved to:\n{file_path}")
    
    def load_recipe(self):
        """Load a scraping recipe"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Recipe", "data/", 
            "Recipe Files (*.json)")
        
        if file_path:
            config = self.recipe_manager.load_recipe(file_path)
            if config:
                # Ask user what to do
                reply = QMessageBox.question(
                    self, "Load Recipe",
                    "Recipe loaded successfully!\n\nWhat would you like to do?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                # Apply configuration
                self.apply_config(config)
                
                # If user clicked Yes, run scraping
                if reply == QMessageBox.Yes:
                    self.start_scraping()
    
    def apply_config(self, config):
        """Apply configuration to UI"""
        self.cb_tables.setChecked(config.get('tables', True))
        self.cb_text.setChecked(config.get('text', False))
        self.cb_links.setChecked(config.get('links', False))
        self.cb_images.setChecked(config.get('images', False))
        self.cb_auto_scroll.setChecked(config.get('auto_scroll', False))
        self.keyword_input.setText(config.get('keyword_filter', ''))
        self.regex_input.setText(config.get('regex_filter', ''))
        self.cb_remove_duplicates.setChecked(config.get('remove_duplicates', True))
    
    def refresh_api_list(self):
        """Refresh API endpoints list"""
        # Get captured APIs from API Hunter
        apis = self.api_hunter.get_captured_apis()
        
        self.api_list.clear()
        for api_url in apis:
            self.api_list.addItem(api_url)
        
        if not apis:
            self.status_label.setText("No API endpoints detected yet")
    
    def fetch_api_data(self, item):
        """Fetch data from selected API endpoint"""
        url = item.text()
        
        try:
            # Use API hunter to fetch data
            df = self.api_hunter.fetch_api_data(url)
            
            if df is not None and not df.empty:
                self.current_df = df
                self.display_preview(df)
                self.status_label.setText(f"✅ Fetched {len(df)} rows from API")
                
                # Enable export buttons
                self.btn_export_csv.setEnabled(True)
                self.btn_export_json.setEnabled(True)
                self.btn_export_excel.setEnabled(True)
            else:
                QMessageBox.information(self, "No Data", 
                                       "API returned no data or invalid format")
        except Exception as e:
            print(f"API fetch error: {traceback.format_exc()}")
            QMessageBox.critical(self, "API Error", 
                                f"Failed to fetch API data:\n{str(e)}")
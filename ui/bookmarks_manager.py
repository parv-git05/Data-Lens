"""
Bookmarks Manager - Manage saved bookmarks
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QPushButton, QMessageBox, QListWidgetItem, QLabel)
from PyQt5.QtCore import Qt
import json
import os


class BookmarksManager:
    """Manages bookmarks storage and retrieval"""
    
    def __init__(self, bookmarks_file="data/bookmarks.json"):
        self.bookmarks_file = bookmarks_file
        self.bookmarks = self.load_bookmarks()
    
    def load_bookmarks(self):
        """Load bookmarks from file"""
        if os.path.exists(self.bookmarks_file):
            try:
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                return []
        return []
    
    def save_bookmarks(self):
        """Save bookmarks to file"""
        try:
            os.makedirs(os.path.dirname(self.bookmarks_file), exist_ok=True)
            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                json.dump(self.bookmarks, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
            return False
    
    def add_bookmark(self, url, title):
        """Add a new bookmark"""
        # Check if already bookmarked
        for bookmark in self.bookmarks:
            if bookmark['url'] == url:
                return False  # Already exists
        
        self.bookmarks.append({
            'url': url,
            'title': title
        })
        self.save_bookmarks()
        return True
    
    def remove_bookmark(self, url):
        """Remove a bookmark"""
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.save_bookmarks()
    
    def get_bookmarks(self):
        """Get all bookmarks"""
        return self.bookmarks
    
    def show_bookmarks_dialog(self, parent):
        """Show bookmarks dialog"""
        dialog = BookmarksDialog(parent, self)
        dialog.exec_()


class BookmarksDialog(QDialog):
    """Dialog for viewing and managing bookmarks"""
    
    def __init__(self, parent, bookmarks_manager):
        super().__init__(parent)
        self.bookmarks_manager = bookmarks_manager
        self.parent_window = parent
        
        self.setWindowTitle("Bookmarks")
        self.setMinimumSize(600, 400)
        
        self.setup_ui()
        self.load_bookmarks()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("📚 Your Bookmarks")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Bookmarks list
        self.bookmarks_list = QListWidget()
        self.bookmarks_list.itemDoubleClicked.connect(self.open_bookmark)
        layout.addWidget(self.bookmarks_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_open = QPushButton("Open")
        btn_open.clicked.connect(self.open_selected)
        
        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_selected)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        
        button_layout.addWidget(btn_open)
        button_layout.addWidget(btn_delete)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_bookmarks(self):
        """Load bookmarks into list"""
        self.bookmarks_list.clear()
        
        bookmarks = self.bookmarks_manager.get_bookmarks()
        
        if not bookmarks:
            item = QListWidgetItem("No bookmarks yet")
            item.setFlags(Qt.NoItemFlags)
            self.bookmarks_list.addItem(item)
        else:
            for bookmark in bookmarks:
                title = bookmark.get('title', 'Untitled')
                url = bookmark.get('url', '')
                
                item = QListWidgetItem(f"{title}\n{url}")
                item.setData(Qt.UserRole, bookmark)
                self.bookmarks_list.addItem(item)
    
    def open_bookmark(self, item):
        """Open bookmark in browser"""
        bookmark = item.data(Qt.UserRole)
        if bookmark:
            from PyQt5.QtCore import QUrl
            url = bookmark.get('url', '')
            
            # Get parent window's current webview and navigate
            if hasattr(self.parent_window, 'current_webview'):
                self.parent_window.current_webview().setUrl(QUrl(url))
                self.close()
    
    def open_selected(self):
        """Open selected bookmark"""
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            self.open_bookmark(current_item)
    
    def delete_selected(self):
        """Delete selected bookmark"""
        current_item = self.bookmarks_list.currentItem()
        if current_item:
            bookmark = current_item.data(Qt.UserRole)
            if bookmark:
                reply = QMessageBox.question(
                    self, "Delete Bookmark",
                    f"Delete bookmark: {bookmark.get('title')}?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.bookmarks_manager.remove_bookmark(bookmark.get('url'))
                    self.load_bookmarks()
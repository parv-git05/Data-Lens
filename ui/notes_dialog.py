"""
Notes Dialog - Take notes for web pages
File: ui/notes_dialog.py
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton,
                             QHBoxLayout, QLabel, QMessageBox)
import json
import os


class NotesDialog(QDialog):
    """Dialog for taking notes on web pages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Notes")
        self.setMinimumSize(500, 400)
        
        self.notes_file = "data/notes.json"
        self.current_url = None
        self.all_notes = self.load_all_notes()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        layout = QVBoxLayout()
        
        # URL label
        self.url_label = QLabel("No URL")
        self.url_label.setWordWrap(True)
        self.url_label.setStyleSheet("font-weight: bold; padding: 10px; background: #f0f0f0;")
        layout.addWidget(self.url_label)
        
        # Notes text area
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter your notes here...")
        layout.addWidget(self.notes_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("💾 Save")
        btn_save.clicked.connect(self.save_notes)
        
        btn_clear = QPushButton("🗑️ Clear")
        btn_clear.clicked.connect(self.clear_notes)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)
        
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_clear)
        button_layout.addStretch()
        button_layout.addWidget(btn_close)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_all_notes(self):
        """Load all notes from file"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading notes: {e}")
                return {}
        return {}
    
    def save_all_notes(self):
        """Save all notes to file"""
        try:
            os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_notes, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
    
    def load_notes(self, url):
        """Load notes for a specific URL"""
        self.current_url = url
        self.url_label.setText(f"Notes for: {url}")
        
        # Load existing notes for this URL
        notes = self.all_notes.get(url, "")
        self.notes_edit.setPlainText(notes)
    
    def save_notes(self):
        """Save current notes"""
        if self.current_url:
            notes_text = self.notes_edit.toPlainText().strip()
            
            if notes_text:
                self.all_notes[self.current_url] = notes_text
            else:
                # Remove entry if notes are empty
                self.all_notes.pop(self.current_url, None)
            
            if self.save_all_notes():
                QMessageBox.information(self, "Notes Saved", 
                                       "Your notes have been saved successfully!")
            else:
                QMessageBox.warning(self, "Save Failed", 
                                   "Failed to save notes")
    
    def clear_notes(self):
        """Clear current notes"""
        reply = QMessageBox.question(
            self, "Clear Notes",
            "Are you sure you want to clear these notes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.notes_edit.clear()
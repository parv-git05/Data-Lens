"""
Recipe Manager - Save and load scraping recipes
"""

import json
import os


class RecipeManager:
    """Manages scraping recipe configurations"""
    
    def __init__(self):
        pass
    
    def save_recipe(self, file_path, config):
        """
        Save a scraping recipe
        
        Args:
            file_path: Path to save recipe file
            config: Dictionary with scraping configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata
            recipe = {
                'version': '1.0',
                'config': config
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(recipe, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving recipe: {e}")
            return False
    
    def load_recipe(self, file_path):
        """
        Load a scraping recipe
        
        Args:
            file_path: Path to recipe file
            
        Returns:
            dict: Configuration dictionary, or None if failed
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                recipe = json.load(f)
            
            # Return config (handle old format without version)
            if 'config' in recipe:
                return recipe['config']
            else:
                # Old format - entire file is config
                return recipe
                
        except Exception as e:
            print(f"Error loading recipe: {e}")
            return None
    
    def validate_recipe(self, config):
        """
        Validate a recipe configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            tuple: (is_valid, error_message)
        """
        required_keys = ['tables', 'text', 'links', 'images']
        
        for key in required_keys:
            if key not in config:
                return False, f"Missing required key: {key}"
        
        return True, None
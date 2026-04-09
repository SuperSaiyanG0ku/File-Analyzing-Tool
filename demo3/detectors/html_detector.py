import os
import re

class HTMLDetector:
    def __init__(self):
        self.html_tags = [
            re.compile(r'<!DOCTYPE\s+html', re.IGNORECASE),
            re.compile(r'<html', re.IGNORECASE),
            re.compile(r'<body', re.IGNORECASE),
            re.compile(r'<head', re.IGNORECASE),
            re.compile(r'<title', re.IGNORECASE)
        ]

    def is_html(self, file_path):
        """
        Detects if a file is an HTML file based on extension and content.
        """
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in ['.html', '.htm']:
            return False

        # Check content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2048)  # Read first 2KB for performance
                for tag in self.html_tags:
                    if tag.search(content):
                        return True
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return False

        return False

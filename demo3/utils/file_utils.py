import os
import pandas as pd
import logging
from datetime import datetime

class FileUtils:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Setup logging
        log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger()

    def get_file_type(self, file_path):
        """
        Identify file type based on extension.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in ['.pdf']: return 'PDF'
        if ext in ['.docx', '.doc']: return 'Word Document'
        if ext in ['.xlsx', '.xls']: return 'Excel Spreadsheet'
        if ext in ['.jpg', '.jpeg', '.png']: return 'Image'
        if ext in ['.html', '.htm']: return 'HTML'
        
        return 'Unknown'

    def export_results_to_csv(self, results, output_path=None):
        """
        Export analysis results to a CSV file.
        """
        if output_path is None:
            output_path = os.path.join(self.log_dir, f'analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)
        self.logger.info(f"Results exported to {output_path}")
        return output_path

    def log_analysis(self, file_path, result):
        """
        Log analysis result for a single file.
        """
        self.logger.info(f"Analyzed: {file_path} - Result: {result}")

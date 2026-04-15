import os
import re
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

    def clean_excel_data(self, results):
        """
        Remove emojis and clean data for Excel export.
        """
        clean_results = []
        for row in results:
            clean_row = {}
            for key, value in row.items():
                if isinstance(value, str):
                    # Remove emojis (common emoji ranges)
                    value = re.sub(r'[\U0001F600-\U0001F64F'
                                   r'\U0001F300-\U0001F5FF'
                                   r'\U0001F680-\U0001F6FF'
                                   r'\U0001F1E0-\U0001F1FF'
                                   r'\U00002702-\U000027B0'
                                   r'\U000024C2-\U0001F251]+', '', value)
                    # Clean up extra spaces
                    value = ' '.join(value.split())
                clean_row[key] = value
            clean_results.append(clean_row)
        return clean_results

    def export_results_to_excel(self, results, output_path=None, sheet_name=None):
        """
        Export analysis results to a properly formatted Excel file.
        """
        if output_path is None:
            output_path = os.path.join(self.log_dir, f'analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')

        if not sheet_name or sheet_name.strip() == "":
            sheet_name = 'Analysis Results'
            
        # Clean data (remove emojis)
        clean_results = self.clean_excel_data(results)

        # Define exact column order
        columns = [
            'File Name', 'Type', 'HTML', 'Protected', 'Blurry',
            'Cropped', 'File Date', 'Age (Days)', 'Eligibility',
            'Final Status', 'Reason'
        ]

        # Create DataFrame with exact columns
        df = pd.DataFrame(clean_results)

        # Ensure only specified columns exist (in case new keys were added)
        existing_cols = [col for col in columns if col in df.columns]
        df = df[existing_cols]

        # Write to Excel with formatting
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)

            # Access workbook and worksheet for auto-adjustment
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]

            # Auto-adjust column width
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 chars
                worksheet.column_dimensions[column_letter].width = adjusted_width

        self.logger.info(f"Results exported to {output_path}")
        return output_path

    def export_results_to_csv(self, results, output_path=None):
        """
        Export analysis results to a CSV file.
        """
        if output_path is None:
            output_path = os.path.join(self.log_dir, f'analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

        clean_results = self.clean_excel_data(results)
        df = pd.DataFrame(clean_results)
        df.to_csv(output_path, index=False)
        self.logger.info(f"Results exported to {output_path}")
        return output_path

    def log_analysis(self, file_path, result):
        """
        Log analysis result for a single file.
        """
        self.logger.info(f"Analyzed: {file_path} - Result: {result}")

import os
import PyPDF2
import msoffcrypto
import docx
import openpyxl

class PasswordDetector:
    def is_protected(self, file_path):
        """
        Check if a file (PDF, Word, or Excel) is password protected.
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            return self._check_pdf(file_path)
        elif ext in ['.docx', '.doc']:
            return self._check_office(file_path)
        elif ext in ['.xlsx', '.xls']:
            return self._check_office(file_path)
        
        return False

    def _check_pdf(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return reader.is_encrypted
        except Exception as e:
            print(f"Error checking PDF protection: {e}")
            return False

    def _check_office(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                office_file = msoffcrypto.OfficeFile(f)
                return office_file.is_encrypted()
        except Exception as e:
            # msoffcrypto might fail if it's not a valid OLE or OOXML file
            # In that case, we can try to open it normally with docx/openpyxl
            # which will raise an error if it's protected.
            try:
                if file_path.endswith('.docx'):
                    docx.Document(file_path)
                elif file_path.endswith('.xlsx'):
                    openpyxl.load_workbook(file_path)
                return False # If it opens, it's not protected
            except Exception:
                return True # If it fails to open, it might be protected or corrupted
        return False

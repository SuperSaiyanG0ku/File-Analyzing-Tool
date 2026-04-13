import os
from datetime import datetime

class AgeValidator:
    def check_file_age(self, file_path):
        """
        Detect file date, calculate age in days, and determine eligibility.
        Eligibility: Eligible if age <= 365 days.
        """
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}

            # Extract modification timestamp
            timestamp = os.path.getmtime(file_path)
            file_date = datetime.fromtimestamp(timestamp)
            current_date = datetime.now()
            
            # Calculate age in days
            age_delta = current_date - file_date
            age_days = age_delta.days
            
            # Formatting
            formatted_date = file_date.strftime("%Y-%m-%d")
            is_eligible = age_days <= 365
            
            return {
                "file_date": formatted_date,
                "age_days": age_days,
                "is_eligible": is_eligible,
                "status": "Eligible" if is_eligible else "Not Eligible"
            }
        except Exception as e:
            return {"error": str(e)}

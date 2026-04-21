import pandas as pd
import re
from google import genai
import time
import hashlib

# Gemini Setup
GEMINI_API_KEY = "AIzaSyAZKd5EXhVJ24y95XKZKUWi8XGkohG5nlc"
client = genai.Client(api_key=GEMINI_API_KEY)

# Cache for AI results
ai_cache = {}

def mask_sensitive_data(text):
    """Simple masking for sensitive patterns like SSN in text if they appear."""
    if not isinstance(text, str):
        return text
    # Mask SSN-like patterns
    return re.sub(r'\d{3}-\d{2}-\d{4}', 'XXX-XX-XXXX', text)

def validate_with_ai(question, answer):
    """
    Validates an answer using Gemini AI with retry logic and throttling.
    """
    # Create a unique key for caching
    cache_key = hashlib.md5(f"{question}:{answer}".encode()).hexdigest()
    if cache_key in ai_cache:
        return ai_cache[cache_key]

    # Mask data before sending to AI (Security)
    masked_answer = mask_sensitive_data(answer)
    
    prompt = f"""
You are a strict compliance validation system.

Question: {question}
Answer: {masked_answer}

Validation Rules:
- The answer MUST directly and specifically address the question.
- The answer MUST be meaningful, professional, and complete.
- REJECT vague, one-word, or filler answers like "ok", "fine", "done", "test", "n/a" unless they are truly appropriate for the question.
- If the answer is unrelated, nonsensical, or fails to provide the requested information → Status: Invalid.

Return ONLY in this strict format:
Status: Valid or Invalid
Reason: [A brief 1-sentence explanation of why it passed or failed]
"""
    
    max_retries = 3
    retry_delay = 5  # Seconds to wait on 429
    
    for attempt in range(max_retries + 1):
        try:
            # Mandatory 1s delay between calls (Throttling)
            time.sleep(1)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            response_text = response.text.strip()
            
            # Parse response
            status = "Invalid"
            reason = "Invalid AI response"
            
            status_match = re.search(r'Status:\s*(Valid|Invalid)', response_text, re.IGNORECASE)
            reason_match = re.search(r'Reason:\s*(.*)', response_text, re.IGNORECASE)
            
            if status_match:
                status = status_match.group(1).strip().capitalize()
            if reason_match:
                reason = reason_match.group(1).strip()
            
            result = {"Status": status, "Category": "Answer Given", "Reason": reason}
            ai_cache[cache_key] = result
            return result

        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries:
                # Rate limit hit, wait and retry
                time.sleep(retry_delay)
                continue
            elif attempt == max_retries:
                return {"Status": "Invalid", "Category": "Answer Given", "Reason": "Rate limit exceeded"}
            else:
                return {"Status": "Invalid", "Category": "Answer Given", "Reason": f"Validation failed (API error): {error_str}"}

def validate_excel(df):
    """
    Validates the input DataFrame using rule-based and AI-based methods.
    """
    results = []
    
    for index, row in df.iterrows():
        question_orig = str(row.get('Question', ''))
        question_lower = question_orig.lower()
        answer = row.get('Answer', '')
        
        # Step 1: Missing Check
        if pd.isna(answer) or str(answer).strip() == "":
            results.append({
                'Question': question_orig,
                'Answer': answer,
                'Status': "Missing",
                'Category': "Not Answered",
                'Reason': "Answer not provided"
            })
            continue
            
        answer_str = str(answer).strip()
        answer_words = answer_str.split()
        
        status = None
        category = "OK"
        reason = ""
        
        # Step 2: Rule-Based Validation (NO AI for these)
        if "ssn" in question_lower:
            if not re.match(r'^\d{3}-\d{2}-\d{4}$', answer_str):
                status = "Invalid"
                category = "Format Error"
                reason = "Invalid SSN format (Expected: XXX-XX-XXXX)"
            else:
                status = "Valid"
        
        elif "zip" in question_lower:
            if not re.match(r'^\d{5}$', answer_str):
                status = "Invalid"
                category = "Format Error"
                reason = "Invalid ZIP format (Expected: 5 digits)"
            else:
                status = "Valid"
                
        elif "yes" in question_lower or "no" in question_lower:
            if answer_str.lower() not in ['yes', 'no', 'y', 'n']:
                status = "Invalid"
                category = "Value Error"
                reason = "Invalid Yes/No answer (Expected: yes, no, y, n)"
            else:
                status = "Valid"
                
        elif "income" in question_lower or "salary" in question_lower:
            try:
                float(answer_str.replace('$', '').replace(',', ''))
                status = "Valid"
            except ValueError:
                status = "Invalid"
                category = "Type Error"
                reason = "Invalid amount (Expected: numeric value)"
        
        # Step 3: AI Validation Trigger
        # Use Gemini ONLY when:
        # - Question type = unknown (status is still None)
        # - AND answer length > 3 words (sentence)
        if status is None:
            if len(answer_words) > 3:
                ai_result = validate_with_ai(question_orig, answer_str)
                status = ai_result["Status"]
                category = ai_result["Category"]
                reason = ai_result["Reason"]
            else:
                # Short unknown answers default to Valid/Unknown to save calls
                status = "Valid"
                category = "OK"
                reason = "Validated as Unknown type"

        # Final Cleanup
        if status == "Valid" and reason == "":
            reason = "OK"

        results.append({
            'Question': question_orig,
            'Answer': answer,
            'Status': status,
            'Category': category,
            'Reason': reason
        })
        
    return pd.DataFrame(results)

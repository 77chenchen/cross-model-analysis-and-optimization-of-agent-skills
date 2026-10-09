def transform(request):
    text = request.get("text", "")
    
    # Handle null/empty input
    if not text or len(text.strip()) == 0:
        return None
    
    # Extract only digit characters from the string (removes spaces, dashes, parens etc)
    digits_only = ''.join(c for c in text if c.isdigit())
    
    # Remove leading '1' that might be country code indicator written without +
    normalized_digits = digits_only.lstrip('1')
    
    # Must have exactly 10 remaining digits (area code of 3 + subscriber number of 7)
    if len(normalized_digits) == 10:
        return f"+{normalized_digits}"
    
    # Invalid format - not enough or too many valid phone number digits
    return None

"""Utility functions for text filtering."""

import re


def filter_hidden_text(text, should_filter=True):
    """
    Filter out text between -- markers for non-DM users.
    
    Text between -- markers is considered hidden and should only be visible to DMs.
    For non-DM users, the hidden text is completely removed without leaving any trace.
    
    Args:
        text (str): The text to filter
        should_filter (bool): Whether to filter hidden text (True for non-DM users)
        
    Returns:
        str: The filtered text if should_filter is True, otherwise the original text
        
    Examples:
        >>> filter_hidden_text("This is visible --this is hidden-- and this is visible", True)
        'This is visible and this is visible'
        
        >>> filter_hidden_text("This is visible --this is hidden-- and this is visible", False)
        'This is visible --this is hidden-- and this is visible'
    """
    if not text or not should_filter:
        return text
    
    # Remove text between -- markers, including the markers themselves
    # Using non-greedy matching to handle multiple separate hidden sections
    pattern = r'--.*?--'
    filtered_text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # Clean up extra whitespace that may result from removing hidden text
    # Replace multiple spaces with a single space
    filtered_text = re.sub(r' +', ' ', filtered_text)
    # Clean up extra newlines - replace 2 or more consecutive newlines with a single newline
    filtered_text = re.sub(r'\n\s*\n+', '\n', filtered_text)
    
    return filtered_text

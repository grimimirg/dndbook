"""PDF style constants for campaign export."""

from enum import Enum


class PdfStyle(Enum):
    """Available PDF export styles."""
    CLASSIC = 'classic'
    DARK = 'dark'
    FANTASY = 'fantasy'
    
    @classmethod
    def get_all_styles(cls):
        """Get list of all available style values."""
        return [style.value for style in cls]
    
    @classmethod
    def is_valid(cls, style_name):
        """Check if a style name is valid."""
        return style_name in cls.get_all_styles()

import enum

class SourceType(enum.Enum):
    """Enum para representar los tipos de fuentes."""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LANDING_PAGE = "landing_page"
    REFERRED = "referred"
    OTHER = "other"
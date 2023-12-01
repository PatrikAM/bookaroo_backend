from src.schemas.book import book_tag
from src.schemas.library import library_tag
from src.schemas.user import user_tag
from src.schemas.badge import badge_tag

tags = [
    book_tag,
    library_tag,
    user_tag,
    badge_tag,
    {
        "name": "admin",
        "description": "admin only"
    }
]

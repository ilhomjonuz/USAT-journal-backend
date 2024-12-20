from .accounts.apps import AccountsConfig
from .articles.apps import ArticlesConfig
from .archive.apps import ArchiveConfig
from .categories.apps import CategoriesConfig
from .journals.apps import JournalsConfig
from .reviews.apps import ReviewsConfig

__all__ = [
    "AccountsConfig",
    "ArticlesConfig",
    "ArchiveConfig",
    "CategoriesConfig",
    "JournalsConfig",
    "ReviewsConfig",
]
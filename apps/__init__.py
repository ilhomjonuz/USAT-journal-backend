from .accounts.apps import AccountsConfig
from .notification.apps import NotificationConfig
from .articles.apps import ArticlesConfig
from .authors.apps import AuthorsConfig
from .categories.apps import CategoriesConfig
from .dashboard.apps import DashboardConfig
from .journals.apps import JournalsConfig
from .reviews.apps import ReviewsConfig

__all__ = [
    "AccountsConfig",
    "NotificationConfig",
    "ArticlesConfig",
    "AuthorsConfig",
    "CategoriesConfig",
    "DashboardConfig",
    "JournalsConfig",
    "ReviewsConfig",
]
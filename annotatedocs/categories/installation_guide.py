from .base import Category
from ..metrics import Stemmer


__all__ = ('InstallationGuide',)


class InstallationGuide(Category):
    required_metrics = [
        Stemmer,
    ]

from abc import ABC, abstractmethod
import pandas as pd


class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    @abstractmethod
    def fetch(self, **kwargs) -> pd.DataFrame:
        """Fetch raw data and return a DataFrame."""
        pass
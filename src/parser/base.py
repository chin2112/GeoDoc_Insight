from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseParser(ABC):
    """Base interface for document parsers."""
    
    @abstractmethod
    def parse(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Parse a file and return a list of dictionaries representing cases.
        
        Args:
            filepath: Path to the target file.
            
        Returns:
            List of dictionaries matching the database schema.
        """
        pass

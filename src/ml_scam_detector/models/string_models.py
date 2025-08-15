import re
from abc import ABC, abstractmethod

class FormatEnforcedStr(ABC):
    def __init__(self, value: str):
        self.value = value
        self._validate()

    @abstractmethod
    def valid_format_regex_pattern(self) -> str:
        """Return the regex pattern that value must match."""
        pass

    def _validate(self):
        if not re.fullmatch(self.valid_format_regex_pattern(), self.value):
            raise ValueError(f"Value '{self.value}' does not match required format: {self.valid_format_regex_pattern()}")

    def __str__(self):
        return self.value

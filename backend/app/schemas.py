from enum import Enum

class RiskLevel(str, Enum):
    VERY_HIGH = "VERY_HIGH"
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    VERY_LOW = "VERY_LOW"

class ConfidenceLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ProductType(str, Enum):
    PROGRESSIVE_MICROLOAN = "progressive_microloan"
    STANDARD_MICROLOAN = "standard_microloan"
    GROWTH_MICROLOAN = "growth_microloan"

class Direction(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"

class Severity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
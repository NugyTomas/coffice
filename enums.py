from enum import Enum as PythonEnum

class WifiQuality(PythonEnum):
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    SLOW = "slow"
    STABLE = "stable"
    FAST = "fast"

class PowerOutlets(PythonEnum):
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    LIMITED = "limited"
    EVERYWHERE = "everywhere"

class NoiseLevel(PythonEnum):
    UNKNOWN = "unknown"
    NOISY = "noisy"
    MODERATE = "moderate"
    QUIET = "quiet"

class Seating(PythonEnum):
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    BAR_LIKE = "bar-like"
    CASUAL = "casual"
    WORK_FRIENDLY = "work-friendly"

class TypicalOccupancy(PythonEnum):
    UNKNOWN = "unknown"
    LOW = "low"
    MODERATE = "moderate"
    BUSY = "busy"

class FoodOptions(PythonEnum):
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    SNACKS = "snacks"
    GOOD_VARIETY = "good-variety"

class VegetarianOptions(PythonEnum):
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    SNACKS = "snacks"
    GOOD_VARIETY = "good-variety"

class OpeningDayStatus(PythonEnum):
    UNKNOWN = "unknown"
    CLOSED = "closed"
    OPEN = "open"




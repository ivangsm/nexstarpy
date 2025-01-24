class NexStarError(Exception):
    """Base exception for all NexStar communication errors"""

class InvalidTrackingMode(NexStarError):
    """Raised when an invalid tracking mode is specified"""

class InvalidSlewRate(NexStarError):
    """Raised when an invalid slew rate is specified"""

class CommunicationError(NexStarError):
    """Raised when a communication error occurs"""

class ProtocolError(NexStarError):
    """Raised when a protocol violation is detected"""
from enum import IntEnum, Enum

class CommandPrefix(bytes, Enum):
    """NexStar command prefixes from protocol tables (Pages 1-8)"""
    PASS_THROUGH = b'P'           # 0x50: Pass-through command prefix (Page 3)
    GET_POSITION_PRECISE = b'e'   # 0x65: Get precise RA/DEC (Page 1)
    GET_POSITION_STANDARD = b'E'  # 0x45: Get standard RA/DEC (Page 1)
    GET_AZM_ALT_PRECISE = b'z'    # 0x7A: Get precise AZM/ALT (Page 1)
    GET_AZM_ALT_STANDARD = b'Z'   # 0x5A: Get standard AZM/ALT (Page 1)
    GOTO_RA_DEC = b'R'            # 0x52: GOTO RA/DEC (Page 1)
    GOTO_PRECISE_RA_DEC = b'r'    # 0x72: Precise GOTO RA/DEC (Page 1)
    GOTO_AZM_ALT = b'B'           # 0x42: GOTO AZM/ALT (Page 1)
    SET_TRACKING_MODE = b'T'      # 0x54: Set tracking mode (Page 2)
    GET_TRACKING_MODE = b't'      # 0x74: Get tracking mode (Page 2)
    SET_LOCATION = b'W'           # 0x57: Set location (Page 4)
    GET_LOCATION = b'w'           # 0x77: Get location (Page 5)
    SET_TIME = b'H'               # 0x48: Set time (Page 4)
    GET_TIME = b'h'               # 0x68: Get time (Page 5)
    GET_VERSION = b'V'            # 0x56: Get version (Page 7)
    CANCEL_GOTO = b'M'            # 0x4D: Cancel GOTO (Page 8)
    GET_MODEL = b'm'              # 0x6D: Get telescope model (Page 8)
    ECHO = b'K'                   # 0x4B: Echo command (Page 8)
    GOTO_IN_PROGRESS = b'L'       # 0x4C: Check GOTO status (Page 8)

class DeviceID(IntEnum):
    """Device identifiers for pass-through commands (Pages 5-7)"""
    AZM_RA_MOTOR = 0x10    # 16: AZM/RA motor controller
    ALT_DEC_MOTOR = 0x11    # 17: ALT/DEC motor controller
    GPS_UNIT = 0xB0        # 176: GPS unit
    RTC = 0xB2             # 178: Real-Time Clock (CGE only)

class SlewDirection(IntEnum):
    """Slew direction codes from protocol tables (Page 3)"""
    POSITIVE = 0x06        # 6: Variable positive direction
    NEGATIVE = 0x07        # 7: Variable negative direction
    POSITIVE_FIXED = 0x24  # 36: Fixed positive direction
    NEGATIVE_FIXED = 0x25  # 37: Fixed negative direction

class Axis(IntEnum):
    """Axis identifiers from slewing commands (Page 3)"""
    AZM_RA = 0x10          # 16: AZM/RA axis
    ALT_DEC = 0x11         # 17: ALT/DEC axis

class TrackingMode(IntEnum):
    """Tracking modes from protocol §Tracking Commands (Page 2)"""
    OFF = 0                # Tracking disabled
    ALT_AZ = 1             # Altitude-Azimuth tracking
    EQ_NORTH = 2           # Equatorial North
    EQ_SOUTH = 3           # Equatorial South

class Hemisphere(IntEnum):
    """Hemisphere indicators from location commands (Page 4)"""
    NORTH = 0              # Northern latitude
    SOUTH = 1              # Southern latitude
    EAST = 0               # Eastern longitude
    WEST = 1               # Western longitude

class CommandTerminator:
    """Communication constants from developer notes (Page 8)"""
    END = b'#'             # 0x23: Command termination character
    TIMEOUT = 3.5          # Maximum response wait time in seconds

class Revolution:
    """Position conversion constants from precision notes (Page 1)"""
    STANDARD = 0x10000     # 65536: 16-bit resolution
    PRECISE = 0x1000000    # 16777216: 24-bit resolution
    PRECISE_SHIFT = 8      # Bits to shift for precise values

class RateMultiplier:
    """Slew rate conversion from protocol §Slewing (Page 2)"""
    VARIABLE = 4           # Rate multiplier for variable slewing

class Model(IntEnum):
    """Telescope models from Get Model command (Page 8)"""
    GPS_SERIES = 1
    I_SERIES = 3
    I_SERIES_SE = 4
    CGE = 5
    ADVANCED_GT = 6
    SLT = 7
    CPC = 9
    GT = 10
    SE_4_5 = 11
    SE_6_8 = 12
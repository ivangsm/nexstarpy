import serial
from typing import Tuple, Optional, Union
import time
from . import constants
from .exceptions import (
    CommunicationError,
    InvalidTrackingMode,
    InvalidSlewRate,
    ProtocolError,
    NexStarError
)

class NexStar:
    def __init__(self, port: str, timeout: float = constants.CommandTerminator.TIMEOUT):
        self.ser = serial.Serial(
            port=port,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout,
        )

    def _send_command(self, command: bytes) -> bytes:
        """Send command and read response until terminator"""
        self.ser.write(command)
        response = b''
        start_time = time.time()
        
        while time.time() - start_time < self.ser.timeout:
            char = self.ser.read(1)
            if char == constants.CommandTerminator.END:
                return response
            response += char
        
        raise CommunicationError("Command timeout")

    #region Position Commands
    @staticmethod
    def _hex_to_degrees(hex_str: str, precise: bool) -> float:
        """Convert hexadecimal position to degrees (Page 1)"""
        value = int(hex_str, 16)
        if precise:
            value >>= constants.Revolution.PRECISE_SHIFT
            divisor = constants.Revolution.PRECISE
        else:
            divisor = constants.Revolution.STANDARD
        return (value / divisor) * 360

    def get_radec(self, precise: bool = False) -> Tuple[float, float]:
        """Get RA/DEC coordinates (Page 1)"""
        cmd = (constants.CommandPrefix.GET_POSITION_PRECISE if precise 
               else constants.CommandPrefix.GET_POSITION_STANDARD)
        response = self._send_command(cmd.value).decode().split(',')
        return (self._hex_to_degrees(response[0], precise),
                self._hex_to_degrees(response[1], precise))

    def get_azm_alt(self, precise: bool = False) -> Tuple[float, float]:
        """Get Alt/Azm coordinates (Page 1)"""
        cmd = (constants.CommandPrefix.GET_AZM_ALT_PRECISE if precise 
               else constants.CommandPrefix.GET_AZM_ALT_STANDARD)
        response = self._send_command(cmd.value).decode().split(',')
        return (self._hex_to_degrees(response[0], precise),
                self._hex_to_degrees(response[1], precise))
    #endregion

    #region GOTO Commands
    @staticmethod
    def _degrees_to_hex(degrees: float, precise: bool) -> str:
        """Convert degrees to protocol hexadecimal format (Page 1)"""
        rev = degrees / 360
        if precise:
            value = int(rev * constants.Revolution.PRECISE)
            return f"{value:08X}"
        return f"{int(rev * constants.Revolution.STANDARD):04X}"

    def goto_radec(self, ra: float, dec: float, precise: bool = False) -> None:
        """Slew to RA/DEC coordinates (Page 1)"""
        prefix = (constants.CommandPrefix.GOTO_PRECISE_RA_DEC if precise 
                  else constants.CommandPrefix.GOTO_RA_DEC)
        cmd = f"{prefix.value.decode()}{self._degrees_to_hex(ra, precise)}," \
              f"{self._degrees_to_hex(dec, precise)}".encode()
        self._send_command(cmd)

    def goto_azm_alt(self, azm: float, alt: float) -> None:
        """Slew to Alt/Azm coordinates (Page 1)"""
        cmd = f"{constants.CommandPrefix.GOTO_AZM_ALT.value.decode()}" \
              f"{self._degrees_to_hex(azm, False)}," \
              f"{self._degrees_to_hex(alt, False)}".encode()
        self._send_command(cmd)
    #endregion

    #region Tracking Commands
    def set_tracking_mode(self, mode: constants.TrackingMode) -> None:
        """Set tracking mode (Page 2)"""
        if not isinstance(mode, constants.TrackingMode):
            raise InvalidTrackingMode("Use TrackingMode enum")
        self._send_command(constants.CommandPrefix.SET_TRACKING_MODE.value + str(mode.value).encode())

    def get_tracking_mode(self) -> constants.TrackingMode:
        """Get current tracking mode (Page 2)"""
        response = self._send_command(constants.CommandPrefix.GET_TRACKING_MODE.value)
        return constants.TrackingMode(int(response.decode()))
    #endregion

    #region Slewing Commands
    def _variable_rate_cmd(self, axis: constants.Axis, direction: constants.SlewDirection, rate: float) -> None:
        """Build variable rate command (Pages 2-3)"""
        rate_int = int(rate * constants.RateMultiplier.VARIABLE)
        cmd = bytes([
            constants.CommandPrefix.PASS_THROUGH.value[0],  # 0x50
            0x03,  # Fixed length
            axis.value,
            direction.value,
            (rate_int >> 8) & 0xFF,  # High byte
            rate_int & 0xFF,         # Low byte
            0x00,  # Padding
            0x00   # Padding
        ])
        self._send_command(cmd)

    def slew_variable(self, axis: constants.Axis, direction: constants.SlewDirection, rate: float) -> None:
        """Variable rate slew (Page 2)"""
        if rate < 0 or rate > 150:
            raise InvalidSlewRate("Rate must be 0-150 arcsec/sec")
        self._variable_rate_cmd(axis, direction, rate)

    def slew_fixed(self, axis: constants.Axis, direction: constants.SlewDirection, rate: int) -> None:
        """Fixed rate slew (Page 3)"""
        if rate < 0 or rate > 9:
            raise InvalidSlewRate("Rate must be 0-9")
        cmd = bytes([
            constants.CommandPrefix.PASS_THROUGH.value[0],  # 0x50
            0x02,  # Fixed length
            axis.value,
            direction.value,
            rate,
            0x00,  # Padding
            0x00,  # Padding
            0x00   # Padding
        ])
        self._send_command(cmd)
    #endregion

    #region Time/Location Commands
    def set_location(self, lat: Tuple[int, int, int, constants.Hemisphere],
                    lon: Tuple[int, int, int, constants.Hemisphere]) -> None:
        """Set location (Page 4)"""
        cmd = bytes([constants.CommandPrefix.SET_LOCATION.value[0]])  # 0x57
        cmd += bytes(lat[:3]) + bytes([lat[3].value])
        cmd += bytes(lon[:3]) + bytes([lon[3].value])
        self._send_command(cmd)

    def set_time(self, time_data: Tuple[int, int, int, int, int, int, int, int]) -> None:
        """Set time (Page 4)"""
        cmd = bytes([constants.CommandPrefix.SET_TIME.value[0]])  # 0x48
        cmd += bytes(time_data)
        self._send_command(cmd)
    #endregion

    #region GPS Commands
    def is_gps_linked(self) -> bool:
        """Check GPS link status (Page 5)"""
        cmd = bytes([
            constants.CommandPrefix.PASS_THROUGH.value[0],  # 0x50
            0x01,
            constants.DeviceID.GPS_UNIT.value,  # 0xB0
            0x37, 0x00, 0x00, 0x00, 0x01
        ])
        response = self._send_command(cmd)
        return response[0] > 0 if response else False
    #endregion

    #region Miscellaneous Commands
    def get_version(self) -> Tuple[int, int]:
        """Get firmware version (Page 7)"""
        response = self._send_command(constants.CommandPrefix.GET_VERSION.value)
        return (response[0], response[1])

    def get_model(self) -> constants.Model:
        """Get telescope model (Page 8)"""
        response = self._send_command(constants.CommandPrefix.GET_MODEL.value)
        return constants.Model(response[0])

    def cancel_goto(self) -> None:
        """Cancel current GOTO operation (Page 8)"""
        self._send_command(constants.CommandPrefix.CANCEL_GOTO.value)

    def close(self) -> None:
        """Close serial connection"""
        self.ser.close()
    #endregion
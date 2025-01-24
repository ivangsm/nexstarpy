import pytest
from unittest.mock import Mock, patch
from nexstarpy import NexStar
from nexstarpy.constants import *
from nexstarpy.exceptions import *

@pytest.fixture
def mock_serial():
    """Mock serial port with default response"""
    with patch('serial.Serial') as mock:
        # Configure default mock behaviors
        mock.return_value.timeout = 3.5
        mock.return_value.read.side_effect = [b'#']  # Default successful response
        yield mock

def test_initialization(mock_serial):
    """Test serial port configuration"""
    telescope = NexStar(port="/dev/ttyUSB0", timeout=2.0)
    
    mock_serial.assert_called_once_with(
        port="/dev/ttyUSB0",
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=2.0
    )

def test_get_version(mock_serial):
    """Test version command parsing"""
    # Mock version response: 4.1
    mock_serial.return_value.read.side_effect = [b'\x04', b'\x01', b'#']
    
    telescope = NexStar(port="COM1")
    assert telescope.get_version() == (4, 1)

def test_radec_conversion():
    """Test position conversion logic"""
    # Test standard precision (16-bit)
    hex_str = "12CE"
    degrees = NexStar._hex_to_degrees(hex_str, precise=False)
    assert pytest.approx(degrees, 0.001) == 26.4441

    # Test precise mode (24-bit)
    hex_str = "12CE0500"
    degrees = NexStar._hex_to_degrees(hex_str, precise=True)
    assert pytest.approx(degrees, 0.001) == 26.4441

def test_tracking_mode_handling(mock_serial):
    """Test tracking mode validation"""
    # Mock responses for 4 valid modes + invalid mode check
    mock_serial.return_value.read.side_effect = [b'#', b'#', b'#', b'#']
    
    telescope = NexStar(port="COM1")
    
    # Test valid modes
    for mode in TrackingMode:
        telescope.set_tracking_mode(mode)
    
    # Verify command count matches mode count
    assert mock_serial.return_value.write.call_count == len(TrackingMode)
    
    # Test invalid mode
    with pytest.raises(InvalidTrackingMode):
        telescope.set_tracking_mode(5)

def test_slew_rate_validation(mock_serial):
    """Test slew rate boundary checks"""
    telescope = NexStar(port="COM1")
    
    # Valid variable rate (150 arcsec/s)
    telescope.slew_variable(
        axis=Axis.AZM_RA,
        direction=SlewDirection.POSITIVE,
        rate=150.0
    )
    
    # Verify command structure
    expected_cmd = bytes([
        0x50, 0x03, 0x10, 0x06,
        (150*4) >> 8 & 0xFF,  # High byte: (600 >> 8) = 2
        (150*4) & 0xFF,       # Low byte: 600 % 256 = 88
        0x00, 0x00
    ])
    assert mock_serial.return_value.write.call_args[0][0] == expected_cmd
    
    # Invalid variable rate
    with pytest.raises(InvalidSlewRate):
        telescope.slew_variable(
            axis=Axis.AZM_RA,
            direction=SlewDirection.POSITIVE,
            rate=151.0
        )

def test_communication_timeout(mock_serial):
    """Test timeout handling"""
    # Simulate no response and immediate timeout
    mock_serial.return_value.read.side_effect = lambda _: b''  # Always return empty
    mock_serial.return_value.timeout = 0.1
    
    # Mock time progression
    with patch('time.time') as mock_time:
        mock_time.side_effect = [0.0, 0.0 + 0.2]  # 200ms elapsed
        
        telescope = NexStar(port="COM1", timeout=0.1)
        
        with pytest.raises(CommunicationError) as exc_info:
            telescope.get_radec()
        
        assert "Command timeout" in str(exc_info.value)

def test_model_detection(mock_serial):
    """Test model enumeration parsing"""
    mock_serial.return_value.read.side_effect = [b'\x05', b'#']  # CGE model
    telescope = NexStar(port="COM1")
    assert telescope.get_model() == Model.CGE

def test_gps_status_check(mock_serial):
    """Test GPS link detection"""
    # Linked state
    mock_serial.return_value.read.side_effect = [b'\x01', b'#']
    assert NexStar(port="COM1").is_gps_linked() is True
    
    # Not linked
    mock_serial.return_value.read.side_effect = [b'\x00', b'#']
    assert NexStar(port="COM1").is_gps_linked() is False

def test_degrees_to_hex_conversion():
    """Test degree to hexadecimal conversion"""
    # Standard precision
    assert NexStar._degrees_to_hex(0.0, False) == "0000"
    assert NexStar._degrees_to_hex(359.9787, False) == "FFFC"
    
    # Precise mode (using example from protocol docs)
    assert NexStar._degrees_to_hex(26.2520, True) == "0012AB07"

def test_get_tracking_mode(mock_serial):
    """Test tracking mode retrieval"""
    mock_serial.return_value.read.side_effect = [b'2', b'#']  # EQ North
    telescope = NexStar(port="COM1")
    assert telescope.get_tracking_mode() == TrackingMode.EQ_NORTH

def test_fixed_rate_slew(mock_serial):
    """Test fixed rate slewing commands"""
    telescope = NexStar(port="COM1")
    
    # Test positive AZM slew
    telescope.slew_fixed(Axis.AZM_RA, SlewDirection.POSITIVE_FIXED, 5)
    expected_cmd = bytes([0x50, 0x02, 0x10, 0x24, 0x05, 0x00, 0x00, 0x00])
    mock_serial.return_value.write.assert_called_with(expected_cmd)

def test_set_location(mock_serial):
    """Test location configuration"""
    telescope = NexStar(port="COM1")
    telescope.set_location(
        lat=(19, 25, 57, Hemisphere.NORTH),
        lon=(99, 7, 59, Hemisphere.WEST)
    )
    expected_cmd = bytes([
        0x57, 19, 25, 57, 0, 99, 7, 59, 1
    ])
    mock_serial.return_value.write.assert_called_with(expected_cmd)

def test_set_time(mock_serial):
    """Test time configuration"""
    telescope = NexStar(port="COM1")
    telescope.set_time((15, 30, 0, 4, 6, 5, 248, 1))
    expected_cmd = bytes([0x48, 15, 30, 0, 4, 6, 5, 248, 1])
    mock_serial.return_value.write.assert_called_with(expected_cmd)

def test_cancel_goto(mock_serial):
    """Test GOTO cancellation"""
    telescope = NexStar(port="COM1")
    telescope.cancel_goto()
    mock_serial.return_value.write.assert_called_with(b'M')

def test_close(mock_serial):
    """Test serial port closure"""
    telescope = NexStar(port="COM1")
    telescope.close()
    mock_serial.return_value.close.assert_called_once()
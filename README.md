# NexStarPy 🌌

Python 3.13+ interface for Celestron NexStar telescopes using the official serial communication protocol.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features ✨

- **Full Protocol Implementation**: Supports all documented commands from NexStar Communication Protocol V1.2
- **Precision Control**: Both standard (16-bit) and precise (24-bit) positioning modes
- **Modern API**: Type hints and enum-driven interfaces
- **Safety First**: Robust error handling with custom exceptions
- **Cross-Model Support**: Compatible with multiple NexStar telescope models

## Installation 📦

```bash
pip install nexstarpy
```

## Requirements 🔧

| Requirement | Details |
|------------|---------|
| Python Version | 3.13+ |
| Dependencies | pyserial |

## Quick Start 🔭

```python
from nexstarpy import NexStar, constants

# Connect to telescope
telescope = NexStar(port="/dev/ttyUSB0")  # Use actual serial port

# Basic operations
print(f"Firmware: {telescope.get_version()}")
print(f"Model: {telescope.get_model().name}")

# Get current position
ra, dec = telescope.get_radec(precise=True)
print(f"Current RA/DEC: {ra:.6f}°, {dec:.6f}°")

# Slew to M31 (Andromeda Galaxy)
telescope.goto_radec(10.6847, 41.2689, precise=True)

# Set tracking mode
telescope.set_tracking_mode(constants.TrackingMode.EQ_NORTH)

# Close connection
telescope.close()
```

## Core Functionality 🛠️

### Position Control

```python
# Get Alt/Azm coordinates
azm, alt = telescope.get_azm_alt(precise=True)

# GOTO Alt/Azm coordinates
telescope.goto_azm_alt(145.22, 60.78)

# Sync to current position (after manual alignment)
telescope.sync_to_position()
```

### Tracking & Slewing

```python
# Variable rate slew
telescope.slew_variable(
    axis=constants.Axis.AZM_RA,
    direction=constants.SlewDirection.POSITIVE,
    rate=45.5  # arcseconds/sec
)

# Fixed rate slew
telescope.slew_fixed(
    axis=constants.Axis.ALT_DEC,
    direction=constants.SlewDirection.NEGATIVE_FIXED,
    rate=5  # 0-9
)
```

### Time & Location

```python
# Set location (Guadalajara, JAL, México)
telescope.set_location(
    lat=(20, 40, 23, constants.Hemisphere.NORTH),    # 20°40'23" N
    lon=(103, 20, 58, constants.Hemisphere.WEST)     # 103°20'58" W
)

# Set time (24h format, UTC-8 with DST)
telescope.set_time((15, 30, 0, 4, 6, 5, 248, 1))  # April 6 3:30PM PDT
```

## Error Handling ⚠️

```python
try:
    telescope.goto_radec(400, 100)  # Invalid coordinates
except InvalidPositionError as e:
    print(f"GOTO failed: {e}")

try:
    telescope.set_tracking_mode(5)  # Invalid mode
except InvalidTrackingMode:
    print("Use TrackingMode enum values")
```

### Supported Exceptions

| Exception | Description |
|-----------|-------------|
| `CommunicationError` | Serial port issues |
| `ProtocolError` | Invalid responses |
| `InvalidSlewRate` | Rate out of bounds |
| `AlignmentError` | GOTO before alignment |

## API Reference 📚

### Core Classes

| Class | Description |
|-------|-------------|
| `NexStar` | Main telescope interface |
| `constants` | Protocol enums and configuration |
| `exceptions` | Custom error hierarchy |

### Key Methods

| Method | Description |
|--------|-------------|
| `get_radec()` | Get RA/DEC coordinates |
| `goto_azm_alt()` | Slew to Alt/Azm position |
| `set_tracking_mode()` | Configure tracking behavior |
| `slew_variable()` | Start variable rate motion |
| `set_location()` | Configure geographic position |

## Troubleshooting 🔧

### Common Issues

```bash
# Serial port permissions
sudo chmod 666 /dev/ttyUSB0

# Timeout errors
telescope = NexStar(port="COM3", timeout=5.0)

# Protocol version mismatches
if telescope.get_version() < (1, 6):
    print("Precision commands unavailable")
```

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Open Pull Request

## License 📄

MIT License - See LICENSE for details

## Acknowledgments

Protocol documentation courtesy of Celestron LLC

---

Developed with 🔭 by Iván Salazar

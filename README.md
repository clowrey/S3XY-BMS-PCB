# isoSPI-M3Y-BMS-PCB

**Hardware Design for Tesla Model 3/Y Battery Management System**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![KiCad](https://img.shields.io/badge/KiCad-8.0+-blue.svg)](https://www.kicad.org/)
[![RP2350A](https://img.shields.io/badge/MCU-RP2350A-green.svg)](https://www.raspberrypi.com/products/rp2350/)

This repository contains the **KiCad PCB design files** for a replacement Battery Management System (BMS) designed for Tesla Model 3 and Model Y battery packs. This hardware interfaces with high-voltage (400V) battery modules using the isoSPI protocol and provides comprehensive monitoring, control, and safety features.

🔗 **Companion Firmware Repository:** [isoSPI-M3Y-BMS](https://github.com/clowrey/isoSPI-M3Y-BMS)

---

## ⚡ Overview

This PCB design implements a complete BMS controller capable of:

- **Direct BMB Communication**: isoSPI master interface for Battery Management Boards
- **High Precision Monitoring**: Current, voltage, temperature, and power measurement
- **CAN Bus Integration**: 500kbps communication with vehicle systems and inverters
- **Contactor Control**: Safe sequenced activation of high-voltage contactors
- **Cell Balancing**: Individual cell balancing control through BMB modules
- **Safety Features**: Overcurrent, overvoltage, undervoltage, and thermal protection

### 🔋 Tesla Model 3/Y Battery Pack Architecture

Tesla Model 3 and Model Y battery packs utilize a modular architecture:

- **Cell Configuration:** 4416 cells (96s46p) in 4 modules
- **Module Configuration:** 24 cells in series per module (96 total series groups)
- **Nominal Voltage:** ~350V (fully charged: ~400V, discharged: ~280V)
- **Capacity:** Varies by pack (50-82 kWh depending on model/year)
- **Battery Management Boards (BMBs):** Each module contains BMBs that monitor cell groups
- **Communication:** Original packs use proprietary Tesla BMS; this project replaces it

**Why Replace the BMS?**
- Reuse Tesla packs in DIY electric vehicle conversions
- Second-life energy storage systems
- Research and educational purposes
- Open-source alternative to proprietary systems

### 🔌 Key Hardware Features

| Feature | Implementation |
|---------|----------------|
| **Microcontroller** | Raspberry Pi RP2350A (dual Cortex-M33, 150MHz) |
| **Current Sensing** | Texas Instruments INA228 (20-bit ADC) |
| **Pack Voltage** | 4-channel ADC with precision voltage dividers |
| **CAN Interface** | Hardware CAN transceiver (500kbps) |
| **isoSPI** | Differential Manchester encoding, galvanic isolation |
| **Contactor Drivers** | 4-channel PWM with inrush control |
| **Operating Voltage** | 12V nominal input |
| **High Voltage Rating** | Up to 400V DC battery pack |

---

## 📁 Repository Structure

```
isoSPI-M3Y-BMS-PCB/
├── isoSPI-M3Y-BMS-PCB.kicad_pro    # KiCad project file
├── isoSPI-M3Y-BMS-PCB.kicad_sch    # Main schematic design
├── isoSPI-M3Y-BMS-PCB.kicad_pcb    # PCB layout
├── BMS_Library/                     # Custom component library
│   ├── BMS_Library.kicad_sym        # Symbol library
│   └── BMS_Library.pretty/          # Footprint library
├── RP2350_KiCad/                    # RP2350 MCU resources
│   ├── RP2350A_QFN-60*.kicad_mod    # Footprints
│   ├── RP2350A-QFN60.step           # 3D model
│   └── rp2350a-qfn60.kicad_sym      # Symbol
├── bms.3dshapes/                    # 3D models for connectors
├── reassociate_components.py        # Component re-linking utility
├── apply_mapping.py                 # Reference mapping tool
└── fabrication-toolkit-options.json # Manufacturing outputs config
```

---

## 🚀 Getting Started

### Prerequisites

- **KiCad 8.0+** - [Download here](https://www.kicad.org/download/)
- **Python 3.7+** (for utility scripts)
- Basic understanding of PCB design and high-voltage safety

### Opening the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/clowrey/isoSPI-M3Y-BMS-PCB.git
   cd isoSPI-M3Y-BMS-PCB
   ```

2. **Open in KiCad:**
   - Launch KiCad
   - Open `isoSPI-M3Y-BMS-PCB.kicad_pro`

3. **Library Configuration:**
   - Libraries are configured in local `sym-lib-table` and `fp-lib-table`
   - Project-specific libraries (`BMS_Library`, `RP2350_KiCad`) should load automatically
   - If missing components appear, verify library paths in KiCad preferences

### Viewing the Design

- **Schematic:** Open `isoSPI-M3Y-BMS-PCB.kicad_sch` to view circuit design
- **PCB Layout:** Open `isoSPI-M3Y-BMS-PCB.kicad_pcb` to view board layout
- **3D View:** Press `Alt+3` in PCB editor to visualize the assembled board

---

## 🛠️ Design Sections

### Power Supply
- 12V input with protection and filtering
- 3.3V LDO for MCU and logic
- Isolated power for isoSPI interface

### Microcontroller (RP2350A)
- QFN-60 package with thermal pad
- Crystal oscillator for precision timing
- JTAG/SWD debug interface
- Boot mode selection

### Current Sensing (INA228)
- Shunt resistor-based measurement
- 20-bit delta-sigma ADC
- Bidirectional current monitoring
- I2C interface to MCU

### Voltage Monitoring
- 4-channel pack voltage measurement
- Precision resistor dividers (high voltage to ADC range)
- Individual cell voltages via isoSPI
- 12-bit internal ADC

### isoSPI Interface
- Differential transformer coupling
- Manchester encoding via PIO
- Galvanic isolation from high voltage
- Master and snooper mode support

### CAN Bus
- Hardware CAN transceiver
- 120Ω termination (configurable)
- PIO-based CAN 2.0B implementation
- 500kbps operation

### Contactor Control
- 4 independent high-current outputs
- PWM inrush current limiting
- Sequenced activation logic
- Flyback protection diodes

### Connectors
- High-voltage battery pack connector
- 12V power input
- CAN bus connector
- USB programming interface
- Debug headers

---

## 🔧 Utility Scripts

### `reassociate_components.py`

Re-links PCB footprints to schematic symbols after copying design sections. This is essential when:
- Copying and pasting PCB sections (breaks UUID links)
- Duplicating circuits for multi-channel designs
- Recovering from schematic/PCB desynchronization

**Usage:**
```bash
python reassociate_components.py
```

The script:
1. Parses both `.kicad_sch` and `.kicad_pcb` files
2. Matches components by reference designator and type
3. Updates PCB footprints with correct schematic UUIDs
4. Creates backup before modification

### `apply_mapping.py`

Applies specific component reference remapping (e.g., when renaming U11→U27). Updates both reference designators and UUID linkages.

**Usage:**
```bash
python apply_mapping.py
```

---

## 📦 Manufacturing

### Generating Production Files

The project includes `fabrication-toolkit-options.json` for automated manufacturing output generation.

**Recommended manufacturers:**
- JLCPCB
- PCBWay
- OSH Park
- Any PCB fab supporting 4+ layer boards

### PCB Specifications

| Parameter | Value |
|-----------|-------|
| **Layers** | 4 (or as designed) |
| **PCB Thickness** | 1.6mm standard |
| **Copper Weight** | 2oz for power traces |
| **Min Trace/Space** | 6/6 mil (typical) |
| **Solder Mask** | Green (or preference) |
| **Silkscreen** | White |
| **Surface Finish** | ENIG or HASL |

### High-Voltage Considerations

⚠️ **CRITICAL SAFETY REQUIREMENTS:**

- **Clearances:** Maintain minimum 4mm creepage distance for 400V
- **Isolation:** isoSPI and current sensing must maintain galvanic isolation
- **Testing:** All HV sections require hi-pot testing before energization
- **Conformal Coating:** Recommended for high-voltage traces
- **Certifications:** May require UL/CE certification for commercial use

---

## 🔌 Assembly Notes

### Component Sourcing

- Most components available from Digi-Key, Mouser, or LCSC
- RP2350A: Available from Raspberry Pi approved distributors
- INA228: Texas Instruments or authorized distributors
- Connectors: Match to Tesla pack interface specifications

### Assembly Sequence

1. **SMD Components:** Reflow solder all surface mount parts
2. **Through-hole:** Hand solder connectors and large components
3. **Inspection:** Verify all solder joints and orientation
4. **Testing:** Low-voltage functional testing before HV connection
5. **Programming:** Flash firmware via USB or SWD
6. **Calibration:** ADC and current sensing calibration routines

---

## 🔗 Firmware Integration

This PCB is designed to work with the companion firmware:

📦 **[isoSPI-M3Y-BMS Firmware](https://github.com/clowrey/isoSPI-M3Y-BMS)**

### ✅ Implemented Features (v2.0.0)

**Hardware Drivers:**
- RP2350A microcontroller with dual Cortex-M33 cores
- INA228 current/voltage/power sensor driver
- Internal ADC for pack voltage monitoring (4 channels)
- Contactor control (4 channels, sequenced activation)
- Serial command processing (30+ commands)
- CAN bus interface (can2040, 500kbps broadcast)
- isoSPI PIO master implementation
- isoSPI passive bus snooper
- Unified BMB test interface
- Runtime interface switching (Batman/isoSPI)

**System Features:**
- Parameter system with 108+ BMS parameters
- Coulomb counting for SOC tracking
- Automatic 10Hz pack status CAN broadcasting
- Statistics tracking for TX/RX/errors
- Configurable message IDs and data formatting

### 🚧 In Progress (Phase 3)

- BATMan/isoSPI interface switching
- Runtime interface control (automatic disable/enable)
- Full BMS state machine
- Cell voltage reading via isoSPI
- Cell balancing control
- Temperature monitoring

### 📋 Pending (Phases 4-6)

- Hardware testing and validation
- Calibration routines for ADC
- Flash storage for calibration data
- Error handling and recovery
- Extended testing (24+ hours)
- Performance optimization
- Documentation completion

### Getting Started with Firmware

1. Clone the firmware repository
2. Install Pico SDK and build tools (CMake-based)
3. Build the project:
   ```bash
   cd isoSPI-M3Y-BMS
   mkdir build && cd build
   cmake ..
   make
   ```
4. Flash to RP2350A via USB or SWD
5. Connect via serial interface (115200 baud)
6. Configure using serial commands
7. Optional: Integrate with ESPHome for monitoring and display

### Optional: ESPHome Display Integration

The firmware supports integration with ESPHome for advanced monitoring via touchscreen displays:

**ESPHome Features:**
- **Three-Page Display Interface:**
  - Main overview with key parameters
  - Detailed battery information
  - Cell voltage graph (all 108 cells visualized)
- **Real-time Monitoring:** Live parameter updates every 5-10 seconds
- **Touch Controls:** Balance on/off, page navigation
- **Home Assistant Integration:** All BMS parameters as HA entities
- **Professional UI:** LVGL-based interface optimized for 480x320 displays

**Supported Hardware:**
- JC4832W535 480x320 QSPI touchscreen
- ESP32-S3 based display modules
- WiFi connectivity for OTA updates

See the [ESPHome interface documentation](https://github.com/clowrey/isoSPI-M3Y-BMS/tree/main/esphome-interface) in the firmware repository for setup instructions.

---

## ⚠️ Hardware Safety

### ⚡ HIGH VOLTAGE WARNING ⚡

**This system interfaces with 400V battery packs that can deliver LETHAL current.**

- **Only qualified personnel should work on high-voltage systems**
- **Proper isolation and safety measures required**
- **Use appropriate personal protection equipment (PPE)**
- **Follow all electrical safety protocols**
- **Discharge pack completely before service**
- **EV battery systems can deliver lethal current**
- **Follow all lockout/tagout procedures**

### ⚠️ DEVELOPMENT STATUS

- **This is a development version (v2.0.0)**
- **isoSPI implementation is experimental**
- **BATMan protocol partially implemented**
- **Extensive testing required before production use**
- **USE AT YOUR OWN RISK**
- No warranty expressed or implied
- Not certified for commercial EV use
- User assumes all responsibility for safety

### Recommended Safety Equipment

- Insulated high-voltage gloves (Class 00 minimum)
- Safety glasses with side shields
- Insulated tools rated for 1000V
- Multimeter rated for CAT III 600V or higher
- Isolation transformer for bench testing
- Emergency shutdown procedures
- First aid and emergency response plan

---

## 📚 Documentation

### Related Resources

- **Firmware Repository:** [isoSPI-M3Y-BMS](https://github.com/clowrey/isoSPI-M3Y-BMS)
- **RP2350A Datasheet:** [Raspberry Pi Documentation](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf)
- **INA228 Datasheet:** [Texas Instruments](https://www.ti.com/product/INA228)
- **Pico SDK:** [Raspberry Pi Pico SDK](https://github.com/raspberrypi/pico-sdk)
- **can2040 Library:** [Kevin O'Connor's can2040](https://github.com/KevinOConnor/can2040)
- **Original BATMan BMS:** Damien Maguire & Tom de Bree

### Additional Documentation

- Schematic PDF exports (generate from KiCad)
- Bill of Materials (generate from KiCad BOM tool)
- Assembly drawings (generate from KiCad fabrication outputs)
- Test procedures (in firmware repository)
- CAN message format documentation (in firmware repo)
- Calibration procedures (in firmware repo)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes with clear commit messages
4. Test thoroughly (especially high-voltage sections)
5. Submit a pull request with detailed description

**Areas for contribution:**
- Schematic improvements
- PCB layout optimization
- Additional protection circuits
- Manufacturing DFM improvements
- Documentation enhancements
- Test jig designs

---

## 📝 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

**In summary:**
- ✅ Free to use, modify, and distribute
- ✅ Must disclose source code
- ✅ Must use same GPL-3.0 license
- ✅ State changes made to original
- ❌ No warranty provided

---

## 🙏 Acknowledgments

- **Damien Maguire & Tom de Bree** - Original BATMan BMS software
- **ESPHome Community** - Framework and component support
- **Kevin O'Connor** - can2040 library for RP2040/RP2350
- **Raspberry Pi Foundation** - Pico SDK and excellent documentation
- **Texas Instruments** - INA228 current sensing IC
- **KiCad Community** - Excellent open-source EDA tools
- **Analog Devices** - isoSPI protocol and reference designs
- **Tesla Motors** - Battery module architecture reference

---

## 📧 Support & Contact

- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** GitHub Discussions for general questions
- **Pull Requests:** Contributions welcome via GitHub PR

---

## 📋 Changelog

### Hardware Version 2.0 (December 2025) - RP2350A Platform

**Complete platform migration supporting firmware v2.0.0:**

#### **Major Hardware Changes**

* **Microcontroller:** Migrated from ESP32 to Raspberry Pi RP2350A
  - Dual Cortex-M33 cores @ 150MHz
  - QFN-60 package with thermal management
  - Native USB support for programming and debugging
  - Hardware SWD debug interface

* **Current Sensing:** Replaced AS8510 with Texas Instruments INA228
  - 20-bit delta-sigma ADC
  - High-side and low-side sensing capability
  - I2C interface with configurable address
  - Integrated power calculation

* **Pack Voltage Monitoring:** Added 4-channel internal ADC monitoring
  - Precision voltage dividers for 400V → 3.3V range
  - 12-bit resolution
  - Individual channel filtering

* **CAN Bus:** Integrated hardware CAN transceiver
  - Native CAN 2.0B support via PIO
  - 500kbps operation
  - Configurable termination (120Ω)

#### **New Features**

* **isoSPI Implementation:**
  - Differential transformer coupling with galvanic isolation
  - PIO-based Manchester encoding/decoding
  - Master mode for direct BMB communication
  - Passive snooper mode for bus monitoring
  - Runtime switching between BATMan SPI and isoSPI

* **Enhanced Contactor Control:**
  - 4-channel PWM drivers with inrush limiting
  - Sequenced activation logic in hardware
  - Flyback protection for inductive loads

* **Unified Testing Interface:**
  - Single test connector for both BATMan and isoSPI modes
  - Automatic interface detection

#### **Firmware Compatibility**

This hardware revision requires **firmware v2.0.0 or later** from the companion repository:
- [isoSPI-M3Y-BMS v2.0.0 Changelog](https://github.com/clowrey/isoSPI-M3Y-BMS#changelog)

### Hardware Version 1.x (2024-2025) - ESP32 Platform

**Original ESP32-based design:**
- ESP32-WROOM-32 microcontroller
- AS8510 current sensor
- Arduino framework
- BATMan SPI communication only
- ESPHome integration support

---

## ⚙️ Project Status

**Current Hardware Version:** v2.0 (RP2350A-based design)

**PCB Development Status:**
- ✅ Schematic design complete
- ✅ Component selection finalized
- 🔄 PCB layout in progress
- ⏳ Design rule check (DRC) pending
- ⏳ Prototype fabrication pending
- ⏳ Hardware validation pending
- ⏳ Production testing pending

**Companion Firmware Status:** 
- **Version:** v2.0.0 (November 2025)
- **Status:** Active development
- **Phase:** isoSPI implementation in progress (Phase 3)
- **See:** [Firmware Repository](https://github.com/clowrey/isoSPI-M3Y-BMS) for detailed status

---

## 🔮 Future Enhancements

- [ ] Enhanced thermal management
- [ ] Additional redundant safety circuits
- [ ] Wireless monitoring interface
- [ ] Integrated display option
- [ ] Automotive-grade component variants
- [ ] Extended temperature range support
- [ ] Multi-pack support with CAN bridging
- [ ] Production test fixture design

---

**⚡ Building the future of open-source battery management systems ⚡**

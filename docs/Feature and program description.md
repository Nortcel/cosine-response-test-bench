# Feature and program description

Text transcribed from the author-supplied V26.7 document. Embedded illustrations remain in the original document.

Cosine Response Test Bench Controller

Feature and Program Description

Revised for the V26.7 final release

This document describes the released V26.7 application as it is currently presented to the operator. It supersedes earlier descriptions that referenced interface elements and behaviours that are no longer part of the final build.

Figure 1. V26.7 interface during a completed measurement session. The ready / idle state uses the same overall layout with reference curves and empty measurement fields before a scan is run.

The Cosine Response Test Bench Controller is a desktop application for operating an Arduino-based angular optical test bench, capturing detector measurements, comparing the measured response with an ideal cosine, monitoring live alignment, reviewing repeated scans, and exporting figures and datasets for analysis and reporting.

The software is designed to provide a clear, reproducible, and operator-guided cosine response measurement workflow, prioritising transparency, manual control, and traceability over hidden automation.

System at a glance

1. Main window layout

The released interface is organised as a graph workspace on the left, a compact operational column on the right, and a serial log strip at the far right.

The left side contains Graph 1: Cosine Response, Graph 2: Cosine Response Scan Comparison, and Cosine Error. Each graph has its own local settings panel and a dedicated Export button.

The right-side column groups Connection and Device, Measurement Setup, Controls, Measurement, and Alignment into stacked framed modules. This layout keeps all operational functions visible without needing a separate top settings ribbon.

2. Connection, setup, and control modules

2.1 Connection and Device

The Connection and Device module contains the serial port selector, Refresh, and Connect / Disconnect controls.

Its status line reports the current connection state and baud rate.

The device details area is used for traceability and typically shows model, port, manufacturer, firmware, connected-at timestamp, and hardware ID.

When the firmware reports version, board, and build details, those values appear here and help confirm software–firmware compatibility.

2.2 Measurement Setup

Measurement Setup is shown on the main screen as a compact summary card and is edited through the Edit setup dialog.

The current release uses this module to record diode model, operator, diode type, diffuser used, bench configuration, test ID, measurement notes, and output folder.

The software also shows an export filename preview derived from the diode model and timestamp. It is a preview, not a separate manual file-name field.

Exported files are automatically named using timestamps and optional metadata such as the diode model, and are written to the selected output folder.

V26.7 uses manual export actions. The earlier auto-save option is not part of the released build.

2.3 Controls

The Controls module is divided into Scanning control, Positioning and Laser, Motion control, and Session actions.

Scanning control contains Start Scan, the scans selector (1 to 8), and Stop Scan. In practical use, repeated scans can be accumulated and reviewed on Graph 2 without a separate Compare Scan button on the main screen.

Positioning and Laser provides Home position, End position, a laser toggle control (label switches between Laser On and Laser Off), and Status. Home and End buttons can be highlighted to indicate active position state.

Motion control is summarised on the main screen and opened in detail through Edit control. The dialog contains scan speed, return speed, signal polarity, motion presets, and speed synchronisation functions such as Read speeds and Apply speeds.

Session actions contains Clear Plot and Clear Session. Clear Plot removes plotted scan content, while Clear Session also resets broader session state including stored comparisons and alignment history.

3. Graph and analysis workspace

3.1 Graph 1 – Cosine Response

Graph 1 is dedicated to the current scan and is used to judge whether the latest run is acceptable.

It can display the ideal cosine reference, the current scan, a mirrored curve for symmetry review, the grid, and an optional error band.

The graph supports Normalised and Raw voltage modes. In normalised mode it focuses on cosine-response shape; in raw mode it exposes the detector voltage scale directly.

3.2 Graph 2 – Cosine Response Scan Comparison

Graph 2 is used to retain and compare scans. It supports repeatability checks, before-versus-after studies, and comparison of different detector or diffuser configurations.

The adjacent Scans manager allows stored scans to be shown or hidden, renamed, recoloured, deleted, or cleared.

Each stored scan is automatically assigned a unique label and display colour so repeated runs remain easy to distinguish in comparison mode.

Graph 2 export is scoped to the scans currently displayed and can also generate an averaged CSV of the visible comparison set.

3.3 Cosine Error

The Cosine Error graph shows measured minus ideal deviation as a percentage.

It is used to identify whether mismatch is concentrated near the edges, biased to one side, or centred around the optical axis.

3.4 Local graph settings and export

Each graph has a local settings panel so display choices remain predictable and graph-specific.

Graph 1 settings include ideal cosine, current scan, mirrored curve, grid, error band, and normalise mode.

Graph 2 settings include ideal cosine, grid, error band, normalise mode, and scan-visibility management.

Each graph has a local Export control. Graph 1 and Cosine Error export PNG and CSV, while Graph 2 supports PNG, displayed-scan CSV, and average-scan CSV.

4. Measurement and Alignment panels

4.1 Measurement

The Measurement module provides the operator with a compact scan dashboard rather than a full text report.

It shows the current measurement Status, the 0/101 style progress counter, the progress bar, temperature, humidity, and the scan information block.

The scan information block includes RMSE within ±80°, symmetry error, Response at 0° (normalised), peak offset from 0° (maximum response), finished timestamp, and duration.

Earlier experimental fields such as a subjective Quality line are not part of the released V26.7 measurement panel.

4.2 Alignment

The Alignment module is used before or between scans to optimise the optical setup.

It contains the Live value mode selector, Live Measure, Stop, Reset best, the Trend On checkbox, the Signal Voltage | Best bar, and the Live Alignment Trend graph.

The signal bar shows the current value and retains a best-value marker. The trend graph displays recent samples on a 101-sample X-axis for stable visual comparison.

The current release does not include a Find best alignment button; alignment is guided through live feedback.

5. Menu bar, dialogs, and saved settings

The File menu provides Save CSV, Save PNG, Export report set, and Exit.

The Tools menu provides Read speeds, Apply speeds, Show log, Clear log, Clear session, Settings, and Reset all settings.

The Help menu provides How to use, What's new, Full changelog, and About.

Measurement Setup and Motion Control are intentionally edited through popup dialogs so the main interface stays compact while still exposing full configuration when needed.

The software stores its persistent settings in a JSON file placed alongside the application. Saved values can include serial settings, metadata, motion settings, window geometry, splitter positions, graph preferences, and alignment display preferences.

The interface uses a responsive layout with adjustable panels. Window size, splitter positions, and display preferences are preserved between sessions so the software reopens close to the previous working state.

6. Exports and data products

Manual PNG export preserves the visible graph state for reports, presentations, and publication figures.

Standard CSV export captures the active measurement dataset in a tabular form suitable for spreadsheet analysis.

Graph-specific CSV exports can include metadata and full per-sample columns such as sample number, angle, raw voltage, dark offset, reference voltage, corrected voltage, normalised response, and ideal cosine, and apply to the currently displayed graph or comparison set.

Graph 2 can export all displayed scans together and can also export an averaged comparison dataset.

Export report set creates a grouped output package that includes measurement CSV, graph PNG, alignment PNG, and a short summary text file.

The serial log can be saved as a plain-text record of the controller communication for debugging and traceability.

The Serial Log supports live streaming, pause and resume, and automatic scrolling so the latest controller messages remain visible during operation.

7. Typical workflow

8. Device operation and firmware behaviour

8.1 Standby mode

When powered and connected, the system enters Standby mode. The arm is at the null or home position and waits for commands from the software.

In this state there is no scan motion, and manual actions such as status requests, homing, end positioning, or laser control can be issued from the interface.

8.2 Automated measurement sequence

Environmental values are read where available.

The laser is activated for the scan.

The arm rotates across the measurement arc from approximately −90° to +90° in defined increments.

At each step the controller captures and transmits detector voltage data.

After the scan, the arm returns to the null position and the laser is switched off.

8.3 Live Measure mode

Live Measure is a setup mode rather than a full angular scan. The operator uses it to observe the live signal while adjusting alignment.

The software displays the current reading, the best retained reading, and the recent-sample trend so the user can optimise the setup without starting a scan.

8.4 Stop and safety behaviour

Stop Scan interrupts active motion or live measurement. The software and firmware cooperate to halt the process and return the bench to a stable state where appropriate.

The disabled state of scan and live controls also helps prevent invalid actions when the bench is idle or already in motion.

Home and end detection are also reflected in the interface so the operator can see position state while avoiding mechanical overrun.

8.5 Data transmission and traceability

During measurement, the firmware streams angle, voltage, and status information to the software, which converts it into live graphs, progress updates, and result metrics.

Firmware version, board identity, and build information are used by the software for traceability and to reduce the risk of mismatched software and controller builds.

Current-release corrections reflected in this revision
The current interface no longer uses the older top Test Bench Settings bar.
There is no main-window Compare Scan button in the released workflow; repeat and multi-scan comparison is handled through Start Scan, retained scans, and Graph 2 management.
Auto-save after scan is not part of V26.7, and the Alignment panel no longer includes a Find best alignment control.

Module / area | Primary purpose | Typical use

Graph workspace | Display the current scan, stored comparison scans, and cosine error. | Review measurement shape, repeatability, and deviation from the ideal cosine.

Connection and Device | Connect to the controller and confirm device identity. | Select the COM port, connect, and verify board / firmware details.

Measurement Setup | Store per-test metadata and output location. | Record diode, operator, test ID, notes, and output folder.

Controls | Run scans and operate bench hardware. | Start or stop a scan, choose scan count, home the arm, move to end position, use the laser toggle, and clear session state.

Measurement | Summarise progress and scan quality metrics. | Check status, progress, environment, RMSE, symmetry, response at 0°, peak offset, completion time, and duration.

Alignment | Provide live setup feedback. | Use Live Measure, Stop, Reset best, the signal bar, and the trend graph while aligning the detector.

Serial log | Display raw communication with the controller. | Inspect commands, responses, and save a session log when debugging.

Step | Typical operator action

1 | Select the COM port, connect to the controller, and verify the board / firmware information.

2 | Open Measurement Setup, enter the test metadata, and confirm the output folder.

3 | Open Edit control if needed and set scan speed, return speed, presets, and signal polarity.

4 | Use Live Measure to optimise detector alignment before running a scan.

5 | Choose the scan count and run Start Scan. Use Stop Scan if the process must be interrupted.

6 | Review Graph 1, Graph 2, Cosine Error, and the Measurement panel.

7 | Export the required graphs, datasets, report set, or serial log.

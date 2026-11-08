# User manual

Text transcribed from the author-supplied V26.7 document. Embedded illustrations remain in the original document.

Cosine Response Test Bench Controller

User Manual
Version 26.7

Setup, operation, export workflow, and troubleshooting

This manual applies to the latest stable controller software baseline, V26.7. It covers normal setup and operation with the stable one way scanning workflow.

Contents

• 1. Purpose and scope

• 2. System overview

• 3. Software and hardware requirements

• 4. Installation and first time setup

• 5. Interface overview

• 6. Normal operating workflow

• 7. Alignment workflow

• 8. Exporting data and files

• 9. Settings and session behaviour

• 10. Keyboard shortcuts

• 11. Troubleshooting

• 12. Good practice and maintenance

1. Purpose and scope

The Cosine Response Test Bench Controller is used to operate the cosine response bench, connect to the controller over serial, run scans, monitor live alignment, compare completed scans, and export graphs and data files. The software is designed for detector cosine response testing and setup work where repeatability, traceability, and clear visual feedback are important.

• Use this manual for the stable V26.7 desktop controller workflow.

• This version assumes the stable firmware branch and the standard one way scanning method.

• The future bidirectional scan concept is not part of this final stable baseline.

2. System overview

The application is organised around three graph areas on the left and a stacked control column on the right. Graph 1 shows the current cosine response scan. Graph 2 compares stored scans. The Cosine Error graph shows deviation from the ideal cosine. The right column provides connection controls, measurement setup, motion control summary, live measurement status, and alignment tools.

3. Software and hardware requirements

Minimum practical setup

• Windows PC or laptop

• Cosine Response Test Bench Controller V26.7 software

• Compatible bench controller firmware on the connected microcontroller

• USB serial connection to the bench controller

• Python runtime with PySide6, pyserial, and matplotlib if running from source

Recommended operating conditions

• Use a laptop or monitor where the full interface is visible without heavy scaling.

• Keep Windows display scaling at 100% where possible for the intended layout.

• Use a stable USB cable and avoid loose serial connections during scans.

• Ensure the bench arm can move freely to home and end positions.

4. Installation and first time setup

Install and launch

1. Install the required runtime if you are using the Python version of the software.

2. Connect the test bench controller to the PC by USB.

3. Start the software. The main window opens with three graph panels and the right side control column.

4. Check that the correct COM port is visible in the serial port drop down.

First connection

1. Select the correct COM port in Connection and Device.

2. Click Refresh if the port list needs updating.

3. Click Connect.

4. After connection, confirm that device information populates and the serial log starts responding.

5. Use Tools > Read speeds if you want to query the current firmware motion settings.

Initial setup fields

• Open Measurement Setup with Edit setup.

• Fill in the diode model before important test runs.

• Add operator, diode type, diffuser used, bench configuration, and test ID where applicable.

• Choose the output folder for exports and enable Auto save after scan only if you want automatic file generation after each completed scan.

Persistent settings

V26.7 stores software settings in a JSON settings file placed in the same folder as the software. This includes items such as the selected serial port, metadata fields, graph settings, window size, and splitter positions.

5. Interface overview

Top menus

Right side control column

• Connection and Device: serial selection, refresh, connect or disconnect, and device information.

• Measurement Setup: compact summary with Edit setup for full metadata entry.

• Controls: scan start and stop, number of scans, positioning and laser controls, motion control summary, and session actions.

• Measurement: status, progress bar, temperature, humidity, and scan information fields.

• Alignment: live value mode, Live Measure, Stop, Reset best, Trend On, and the Live Alignment Trend graph.

Serial log panel

• The log panel shows incoming firmware messages and sent commands.

• Use Pause to freeze the log display while keeping the software running.

• Use Save log to export the serial log as a text file.

• Use Clear log to clear the displayed log contents.

6. Normal operating workflow

Recommended sequence

1. Connect to the controller.

2. Check that the arm is at home or send Home position if required.

3. Open Edit setup and confirm the test metadata.

4. Review motion control values and polarity in Edit control.

5. Use the alignment tools to optimise the signal if required.

6. Select the required number of scans.

7. Click Start Scan.

8. Watch progress, environment readings, and the serial log until the scan completes.

9. Review Graph 1, Graph 2, and Cosine Error.

10. Export or save the required results.

During scanning

• Stop Scan interrupts the active measurement.

• The Measurement panel shows progress as a count out of 101 samples.

• Graph 1 is the current scan view.

• Graph 2 can retain completed scans for comparison, depending on what is currently stored and visible.

After scanning

• Review RMSE, symmetry error, response at 0°, peak offset from 0°, finished time, and duration.

• Check Cosine Error before accepting the run.

• Use Clear Plot to clear the active plot data.

• Use Clear Session only when you want to clear the full session state.

7. Alignment workflow

The Alignment section is for setup and live optimisation rather than formal scan acquisition. It shows the live signal value, the best tracked value, and a live trend graph.

How to use alignment mode

1. Choose a live value mode: Raw live value, 5 sample average, or 10 sample average.

2. Click Live Measure to start live monitoring.

3. Adjust the detector or bench alignment while watching the signal and the trend graph.

4. Use Reset best when you want to clear the stored best reading and begin tracking again.

5. Use Stop to exit live mode.

6. Leave Trend On checked if you want to see the trend graph update in real time.

Interpretation note

Signal behaviour depends on the selected polarity. In the standard lower voltage equals more light mode, a lower voltage indicates stronger alignment. Always verify that the polarity setting matches the detector and measurement logic in use.

8. Exporting data and files

Quick exports

• Each graph has its own Export button.

• Graph 1 export is for the current cosine response view.

• Graph 2 export is for the comparison graph and the scans currently displayed.

• Cosine Error export is for the error graph and its data.

File menu exports

• Save CSV saves the current measurement data to CSV.

• Save PNG saves the main cosine response graph to PNG.

• Export report set saves a report package including CSV, PNG, alignment PNG, and a summary text file.

Export guidance

• Use a clear diode model and test ID before exporting so file names and metadata are meaningful.

• Set the output folder in Measurement Setup.

• If Auto save after scan is enabled, files are saved automatically after a completed scan.

9. Settings and session behaviour

Saved items

• Serial port selection

• Diode model and other metadata fields

• Output folder and notes

• Scan and return speed values

• Polarity selection

• Graph settings

• Live alignment display settings

• Window size and splitter widths

Session controls

• Clear log only affects the serial log display.

• Clear Plot removes current plot data without resetting everything else.

• Clear Session clears the broader session state and should be used deliberately.

Settings menu

• Use Tools > Settings to review how settings are stored.

• Use Tools > Reset all settings if you want to return to the default software state.

10. Keyboard shortcuts

11. Troubleshooting

Connection issues

• No COM port shown: reconnect the controller, click Refresh, and check the USB cable.

• Connect fails: confirm that the correct COM port is selected and that no other software is using the port.

• Device info stays blank: confirm the firmware is running and the serial baud rate is correct.

Motion and scan issues

• Arm does not stop correctly at home or end: verify the home and end sensors, mechanical free movement, and firmware side behaviour.

• Stop Scan does not respond immediately: review the serial log and verify that the controller is still connected.

• Scan looks incomplete: check for interruption messages and confirm the arm reached the expected positions.

Graph and display issues

• Graph text is clipped: reduce display scaling, enlarge the window, or restore the saved layout.

• Graph 2 comparison looks empty: check the Scans list visibility and whether stored scans are present.

• Live Alignment Trend is blank: confirm that Live Measure is active and Trend On is enabled.

Export and file issues

• No files are exported: confirm the output folder is valid and writable.

• Auto save does not create files: verify that the scan completed and Auto save after scan is enabled.

• Saved names are unclear: update diode model, test ID, and metadata before exporting.

Startup and environment issues

• Software does not start from source: confirm PySide6, pyserial, and matplotlib are installed.

• Window layout looks wrong after reopening: use Tools > Reset all settings if the saved layout needs clearing.

• If the application fails on startup, review the generated error log file in the software folder.

Serial log clues worth checking

• Connection accepted and device info responses

• Measurement started or stopped messages

• Nullpoint or home related messages

• Any repeated timeout, unknown command, or disconnect messages

12. Good practice and maintenance

• Fill in diode model and test metadata before important runs.

• Confirm polarity before alignment and scanning.

• Use the same motion settings for comparable test series unless you intentionally change the method.

• Keep the optical path clean and the arm movement unobstructed.

• Review Graph 2 and Cosine Error, not only Graph 1, before accepting a result.

• Save raw evidence, PNGs, and serial logs for significant test campaigns.

• Do not change firmware or software versions mid series without recording the change.

End of manual

Area | Function

Graph 1: Cosine Response | Shows the current scan against the ideal cosine reference.

Graph 2: Cosine Response Scan Comparison | Displays stored comparison scans and the current scan when enabled.

Cosine Error | Shows error relative to the ideal cosine profile.

Connection and Device | Selects the serial port and displays connected device details.

Measurement Setup | Stores diode model, diode type, diffuser, bench configuration, operator, output folder, notes, and related metadata.

Controls | Provides scan start and stop, home and end movement, laser control, status requests, motion summary, and session clearing tools.

Measurement | Shows current state, progress, temperature, humidity, and scan information.

Alignment | Provides live value monitoring, best value tracking, and the live alignment trend graph.

Serial log | Displays firmware communication and operational messages.

Menu | Key items

File | Save CSV, Save PNG, Export report set, Exit

Tools | Read speeds, Apply speeds, Show log, Clear log, Clear session, Settings, Reset all settings

Help | How to use, What’s new, Full changelog, About

Shortcut | Action

S | Start scan

X | Stop

F | Live measure / free mode

H | Home

Ctrl+S | Save CSV

Ctrl+P | Save PNG

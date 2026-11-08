# CHANGELOG

Text transcribed from the author-supplied V26.7 document. Embedded illustrations remain in the original document.

Cosine Response Test Bench Controller

Full Changelog   V1 to V26.7

This document records the major software changes made across the Cosine Response Test Bench Controller from the earliest hardware prototyping phase through V26.7. Entries are presented in chronological order, with the oldest items first.

Early Development Summary

## V1 to V9

Hardware prototyping.

Manual measurements and spreadsheet analysis.

## V10 Series

Digital logging introduced.

## V11 Series

Signal handling improvements and filtering.

## V12 Series

Python data processing tools and CSV workflows.

## V13 Series

Automation scripts and repeatability improvements.

## V14 Series

Structured logging and early automation.

## V15 Series

First functional desktop software.

Basic plotting and CSV export.

## V16 Series

Structured architecture.

Serial parser and alignment tracking.

## V17 Series

Semi automated measurement workflow.

Improved data acquisition stability.

## V18 Series

First GUI with PyQt.

Arduino communication.

Basic plotting and scan control.

## V19 Series

Multi graph system introduced.

Scan comparison and storage.

Error graph and RMSE metrics.

## V20 Series

Major UI redesign, improved graphs and alignment tools.

Full CSV export with metadata and multi scan support.

Scan naming fixes and UI improvements.

## V20.1

Updated About section with developer and contact details.

Fixed legend warnings when switching Graph 1 or Graph 2 to Raw voltage mode.

## V20.2

Made GitHub and email links clickable in the About section.

Enabled copyable text across the software.

## V20.3

Added a short How to use help window.

Added tooltips across key controls.

## V20.4

Improved Live Alignment Trend layout.

Fixed label visibility and plot margins.

## V20.5

Initial scan naming fix attempt.

## V20.6

Fixed duplicate scan naming issues.

Ensured globally unique scan labels across mixed Start Scan and Compare Scan workflows.

## V20.7

Restored full detailed CSV export for Graph 1 and Graph 2.

Export includes angle, voltage, dark offset, reference voltage, corrected voltage, normalised voltage, and ideal cosine.

Graph 2 supports multi scan export in a single file.

Structured metadata section added back to the export format.

## V20.8

Improved firmware version, board name, and build info reading from the controller.

Expanded firmware response parsing for VERSION, INFO, FIRMWARE, BOARD, and BUILD style messages.

## V20.9

Added Laser On and End Position buttons to the Controls section.

Prepared software support for the new firmware side laser and end position commands.

## V21.1

Grouped the Controls section into Scanning control, Positioning and Laser, and Clearing.

Added a single laser toggle button with Laser On and Laser Off states.

Kept End Position inside the Positioning and Laser group.

## V21.2

Rearranged the Controls groups vertically.

Debugged the Laser On and Laser Off toggle behaviour.

Fixed queue processing issues that could stop the laser button state from updating correctly.

## V21.3

Swapped Position Status and End Position buttons.

Added active highlight state for Home Position and End Position buttons.

Position highlights now update during home, end, scan, and free mode transitions.

## V21.4

Updated the in software release notes to reflect the latest feature set.

When Number of scans is greater than 1, Start Scan now stores completed scans on Graph 2 like Compare Scan.

Multi scan Start Scan behaviour now matches the comparison workflow more consistently.

## V21.5

Updated graph titles to be shorter and clearer.

Refined axis labels for Graph 1, Graph 2, and Error graph.

Improved consistency between Normalised Response and Raw Voltage axis naming.

Enhanced readability of plotted results for publication use.

## V21.6

Made the full Test Bench Settings top area collapsible.

Improved Serial Log collapse and reopen behaviour with a visible right side reopen control.

Changed export panels so they are hidden by default and opened locally when needed.

Made the Controls layout more compact.

Moved Measurement Setup into a popup dialog with a compact summary in the main UI.

## V21.7

Tightened the expanded top settings area so it uses less height.

Reworked the Measurement Setup summary into a clearer two line compact summary.

Enlarged and strengthened the right edge Serial Log reopen control.

Moved graph export access to clearer local Export buttons in the graph side panels.

Widened the graph side panels slightly so controls are less cramped.

## V21.8

Removed the visible top Test Bench Settings area from the main layout.

Moved Connection and Connected Device into one combined right column panel.

Moved Motion Control into the right column as a compact summary card with an Edit control popup.

Kept Measurement Setup as a compact summary card with popup editing.

Slimmed down the Serial Log reopen tab so it was less visually heavy.

## V21.9

Moved Motion Control into the Controls panel as a compact summary plus Edit control popup.

Made Controls more compact overall.

Reduced the space used by Positioning and Laser and Clearing.

Restored a more compact Measurement Setup summary style with grouped inline fields instead of fully stacked vertical values.

## V22

Reworked the Measurement panel into a clearer dashboard layout.

Added a stronger header with Mode and Samples.

Kept a full width progress bar for scan progress.

Grouped Temperature and Humidity separately from scan timing.

Rebuilt the key metrics area into a cleaner two column layout and made the summary line wrap safely.

## V22.1

Strengthened the Measurement header with clearer Mode and Samples.

Reworked the progress row so the count sits next to the bar cleanly.

Reduced the visual height of the Temperature and Humidity gauges.

Kept key metrics in a cleaner two column layout.

Split the long summary into two cleaner lines to avoid clipping.

## V22.2

Reduced the visual dominance of the Temperature and Humidity bars.

Tightened spacing between all rows to remove the stretched feeling.

Improved alignment between left and right columns.

Made Quality more prominent and improved summary spacing and consistency.

## V22.3

Refined Measurement panel alignment between left and right columns.

Improved progress bar and value alignment so they behave as one unit.

Further refined Temperature and Humidity bars and summary spacing.

Improved typography and visual rhythm across the panel.

## V22.4

Moved Humidity to the right of Temperature to save vertical space.

Moved Finished and Duration below the metrics area on the right.

Moved Quality above RMSE so it is seen first.

Removed the duplicate sample count so it is no longer shown twice.

## V22.5

Kept Temperature and Humidity as separate gauges.

Reworked the Measurement panel layout into a cleaner grid.

Kept Quality above RMSE and moved Finished and Duration below Peak offset on the right.

Removed the duplicated sample count from the summary area.

## V22.6

Reworked the Measurement panel into proper two text columns.

Removed the empty gap under the left column.

Kept Quality above RMSE and Finished and Duration below Peak offset.

Removed duplicate sample display from the lower summary area.

## V22.7

Removed Compare Scan from Controls.

Placed Start Scan, Number of scans, and Stop Scan on one line.

Moved Free Measure into Alignment.

Moved Clear Plot and Clear Session into Measurement Setup.

Improved button colours and emphasis for primary actions.

Reworked Measurement so Quality stands alone, aligned RMSE with Centre, and kept Finished and Duration below Peak offset.

Removed the duplicate alignment value box above the coloured scale.

## V22.8

Removed the Number of scans label and kept the scan count selector compact between Start Scan and Stop Scan.

Strengthened button styling so Stop Scan no longer looks weak.

Improved Measurement Setup summary stacking and added a divider above Clear Plot and Clear Session.

Separated scan info in Measurement and reduced summary duplication.

Clarified Alignment wording by showing Current value, Best value, and Strength scale.

## V22.9

Removed the recurring Measurement panel gap by splitting metrics and scan info into separate layout blocks.

Kept Temperature and Humidity as separate gauges.

Renamed Free Measure to Live Measure and added a dedicated Stop button beside it.

Updated alignment control state handling so the new Stop button only enables during live mode.

## V23

Split Measurement into clearer groups with a metrics block and a separate scan info block.

Strengthened Quality styling and default empty state colour.

Regrouped Alignment actions into one compact row with Find best, Live Measure, Stop, and Reset best.

Shortened the Strength label wording and enabled safer wrapping on long right column device values.

## V23.1

Removed the Find best alignment button from the Alignment workflow.

Kept a cleaner alignment action row with Live Measure, Stop, and Reset best.

Restored the missing °C in Temperature.

Split Scan info into its own visual block below metrics.

Removed duplicate RMSE and Symmetry summary repetition and kept a cleaner single summary line.

## V23.2

Separated the Temperature and Humidity gauges into distinct stacked blocks so their scales no longer read like one combined line.

Shortened Live Measure to Start Live.

Reduced the live action button widths so the alignment controls feel tighter.

Changed the scan start logic so Start Scan no longer clears Graph 2 comparison history.

Comparison is now only cleared by Clear Plot or Clear Session.

## V23.3

Final UI polish pass for gauges, alignment, and spacing.

Reworked Temperature and Humidity gauges so each one reads as a separate control with its own scale.

Restored the missing °C in the temperature readout.

Tightened the Alignment button row and shortened Start Live to Live.

Reduced the size of the large Strength display and softened Scan info styling.

## V23.4

Placed Temperature and Humidity back next to each other with a small gap between them.

Kept Temperature and Humidity as separate gauges with independent labels and scales.

Made the three Alignment buttons the same size, same corner radius, and same overall shape.

Applied more consistent corner radius across buttons and darkened borders for non filled buttons.

## V23.5

Made the Serial Log narrower by default and improved inner padding on its buttons.

Moved Export buttons to the bottom of all three graph side panels.

Changed Export behaviour so each button opens a compact popup with export options.

Adjusted Temperature and Humidity gauge label positioning.

Removed duplicate Current value text from Alignment and renamed the live signal label.

Made the main software title slightly larger and displayed the software version in the header.

## V23.6

Reversed the strict 1.0 cap on normalised measured curves.

Restored peak headroom for Graph 1 and Graph 2 so measured peaks are not artificially flattened.

## V23.7

Moved graph export popups to open above their respective Export buttons when space allows.

Removed the separate Best value text from Alignment.

Replaced it with a vertical best value marker inside the live signal bar.

Moved the Live value mode dropdown onto the same line as the Alignment action buttons.

Renamed the alignment action button to Live Measure.

Moved the Live Alignment Trend graph closer to its title by tightening that section layout.

Retained restored peak headroom so measured peaks are not artificially flattened.

## V23.8

Changed the Alignment label to Signal Voltage | Best: ...

Removed the lower = stronger wording from the main UI line.

Updated the Measurement Setup summary to show two columns with all diode values except notes.

Displayed Diode Model, Diode Type, Diffuser Used, Bench Config, Test ID, and Operator in the summary.

## V23.9

Increased the default startup window size so more of the full UI is visible immediately.

Added a minimum window size to reduce the need to manually enlarge the window on open.

Reduced the top grey header area by tightening the main layout margins and spacing.

Moved Measurement Setup above Controls.

Made Edit control more consistent with Edit setup in size and feel.

## V24

Optimised overall layout and spacing for better use of screen space.

Reduced the top grey header height and pulled the software title tighter under the menu.

Kept the version visible at the top right.

Slightly tightened graph spacing so more plot area is visible.

Improved Measurement Setup spacing with more space between rows and the two columns.

Made the Serial Log narrower by default and improved button padding in its header.

Changed the collapsed Serial Log control to a lighter vertical tab with readable vertical text.

Added scans: before the scan count dropdown.

Added more padding above the Signal Voltage row in Alignment.

## V24.1

Refined Serial Log spacing and width so the panel feels less cramped when open.

Lightened the collapsed Serial Log tab so it is less visually heavy.

Added more spacing in Alignment between the control row and the Signal Voltage row.

Moved Clear Plot and Clear Session out of Measurement Setup and into a more logical Session actions row inside Controls.

Reduced excess padding around the main graphs, especially below the plots.

Improved spacing in the Measurement Setup two column summary.

## V24.2

Centred the software title more cleanly within the top header band.

Centred the Signal Voltage and voltage bar row more clearly and added spacing above it.

Added a very light grey background to the five main right side panels.

Made Stop Scan and the Alignment Stop button show a greyed out disabled state when inactive.

## V24.3

Refined Controls and Alignment styling consistency.

Restored the Signal Voltage bar to a fuller width after an unintended narrowing.

Added disabled state behaviour to the Live Measure Stop button to match Stop Scan logic.

Restored rounded corners on Stop Scan.

Standardised Positioning and Laser button borders, corner radius, and neutral button edge strength.

Improved panel body styling so the light grey fill stays within the framed area.

Changed inner Controls sections to use darker contours instead of white looking blocks.

## V24.4

Made the Positioning and Laser buttons use the same neutral grey tone as the other grey action buttons.

Matched the Edit control button internal padding to Clear Session for better consistency.

Added a visible pressed background state to Reset best.

## V24.5

Changed Reset best to the same grey button styling as Status and Laser On.

Made the laser button text switch to Laser Off when the laser is on.

Narrowed Edit control and aligned it tighter to the right.

## V24.6

Unified checkbox styling with the graph settings checkboxes.

Lightened the checked blue colour across the software.

Darkened dropdown edges slightly for better definition.

Restored the checkbox tick icon and fixed missing dropdown icons.

## V24.7

Reduced the minimum width demand of the left graph area.

Increased protection for the right control column.

Stopped the internal graph splitter from collapsing child sections.

Rebalanced the internal splitter so the graph area shrinks before the control column.

Further reduced the serial log width allowance.

## V24.8

Improved laptop fit responsiveness while keeping the existing workflow unchanged.

Reduced vertical spacing and control heights slightly to keep more of the full UI visible.

Reduced the initial graph height share so the right control column stays accessible on shorter screens.

Updated the in software What’s new section for V24.8.

## V24.9

Narrowed the control column and the serial log default width to free more space for the graphs.

Added automatic serial log scrolling so the latest incoming lines remain visible while running.

Updated the What’s new section for V24.9.

## V24.10

Moved Trend On below onto the Live Alignment Trend title row.

Reduced the control column width by about 25 %.

Preserved the existing behaviour and layout logic elsewhere.

## V24.11

Corrected the Trend On placement so it sits on the Live Alignment Trend row as intended.

Narrowed the five windows in the control column by about 25 %.

Left the rest of the design and behaviour unchanged.

## V24.12

Fixed the startup crash caused by undefined splitter sizing variables.

Kept Trend On on the Live Alignment Trend row.

Retained the narrower control column without changing the workflow.

## V24.13

Allowed the serial log to be widened instead of constraining it to a narrow maximum width.

Increased the font size in the Measurement Setup information columns.

Moved Status to the left side of the Measurement panel and matched its size to the mode indicator.

Opened the control column wider by default so none of its windows are hidden.

Added Tools > Settings and slightly reduced the Live Alignment graph height.

## V24.14

Removed the subjective Quality line from the Measurement panel.

Moved RMSE, Symmetry error, Response at 0°, and Peak offset into the Scan info group.

Removed the diode type and completed summary line from the Scan info section.

Aligned the Measurement status line to the left.

## V24.15

Changed settings storage from registry based QSettings to a JSON file saved in the same folder as the software.

Made the settings file portable and easier to back up or copy between machines.

Updated the Tools > Settings text to reflect the file based approach.

## V24.16

Expanded the JSON settings file to include window size, maximised state, and splitter widths.

Added persistence for graph settings and live alignment view settings.

Made the software reopen closer to the previous session state.

## V24.17

Fixed JSON settings restoration for full screen mode, control column width, and graph settings.

Moved the last seen What’s new version persistence into the JSON settings file.

Improved restoration consistency after startup.

## V24.18

Fixed saving and restoring of the actual graph versus control column splitter widths.

Reapplied saved splitter sizes after startup so defaults no longer overwrite them.

Completed JSON persistence for the graph and control column width state.

## V24.19

Reduced the Live Alignment Trend graph height by about 15 % while keeping its width unchanged.

## V24.20

Applied a stronger height constraint to shorten the Alignment window further.

Used a maximum graph height to force the Live Alignment Trend panel to become shorter.

## V24.21

Removed the overly restrictive maximum height introduced in V24.20.

Restored a more proportional Live Alignment Trend height reduction.

Returned the Alignment window to a more balanced appearance.

## V24.22

Moved the Measurement status label to the left side of the Measurement header.

Prepared the status row for cleaner separation from the progress counter.

## V24.23

Made the Cosine Error Export button the same width as the other graph Export buttons.

Adjusted the Measurement header and progress row while refining the status placement.

## V24.24

Restored the 0/101 progress counter on the right side of the progress bar.

Stopped the Measurement status label from stretching across the full row.

Kept the status on the left and the counter on the right.

## V24.25

Forced layout level left alignment for the Measurement status label.

Removed remaining right alignment influence from the status row.

## V24.26

Fixed the Measurement header layout by moving Status before the row stretch.

Resolved the final issue that kept Status visually anchored to the right.

## V24.27

Fixed the Clear Session crash caused by an invalid data reference inside the clear session workflow.

Restored runnable behaviour based on the last stable build.

## V24.28

Changed Graph 2 title to Cosine Response Scan Comparison for clearer standalone exports.

Corrected Cosine Error so it is plotted and labelled consistently in %.

Removed the Graph 2 right raw voltage axis when multiple scans are displayed.

Changed Centre (0°) to Response at 0° and based Peak offset on the maximum normalised response.

Clarified the symmetry error wording.

## V25.1

Fixed the Live Alignment Trend X-axis to use a 101 sample window.

Moved the Live Alignment Trend title into the white graph section above the plot.

## V25.2

Locked the Live Alignment Trend to a 101 sample window in the graph display.

Adjusted title spacing above the Live Alignment Trend graph.

Changed Response at 0° to Response at 0° (normalised).

Gave the Measurement status line more room so it does not wrap.

Removed the bottom Status line from Controls and widened the graph settings side panels.

## V25.3

Fixed the symmetry label string to show |+θ − −θ| mean correctly.

Renamed the Live Alignment Trend Y-axis to Signal voltage (V).

Distributed shorter Live Alignment traces across the full 1 to 101 range so the plotted trace is centred properly.

Pushed the Graph 2 Scans scrollbar further right.

## V25.4

Widened the Graph 2 Scans panel by about 20 %.

Reduced the Scans window height to create more room above the Export button.

Attempted to move the Graph 2 Scans scrollbar fully to the right edge.

## V25.5

Shortened the Graph 2 Scans list to create more room above Export.

Refined scrollbar positioning and list panel spacing in the Graph 2 Scans section.

## V25.6

Anchored the Graph 2 Scans list at the top after the V25.5 layout issue.

Shortened the Scans window from the bottom without leaving empty space above the list.

## V25.7

Applied a dedicated Graph 2 Scans scrollbar position only update based on the V25.4 branch.

## V25.8

Forced the Graph 2 Scans list to use the full panel width.

Removed internal margins from the Scans layout to help the scrollbar sit at the far right edge.

## V25.9

Removed the width cap from the Graph 2 Scans list so the scrollbar can reach the true far right edge of the panel.

## V25.10

Adjusted Graph 2 and Cosine Error Export button layout spacing and alignment while investigating the floating button issue.

## V25.11

Made Graph 1 and Graph 2 side panels the same width.

Reduced spacing between Graph 2 and its side panel so the plot width is closer to Graph 1.

Moved all three Export buttons to the bottom right and aligned them consistently.

## V25.12

Increased plot margins so titles and bottom axis text remain visible when graph heights are reduced.

Applied safer layout spacing to Graph 1, Graph 2, and Cosine Error.

## V25.13

Reduced the left padding on all three graphs by the same amount.

Tightened Graph 2 side spacing so its plot width is closer to Graph 1.

Increased the bottom graph height allocation to reduce clipping risk.

## V26.1

Matched the Graph 2 plot margin behaviour more closely to Graph 1.

Standardised title spacing across the graphs.

Set all three side panels to the same width.

Added extra right inset inside side panels so Export buttons no longer sit too close to the frame.

## V26.2

Applied Graph 2 style clipping protection to Graph 1 and Cosine Error.

Pulled right side Y-axis labels inward to reduce clipping near the Graph settings panel.

Added more protected height allocation for Graph 1.

## V26.3

Unified clipping safe subplot margins across Graph 1, Graph 2, and Cosine Error.

Added more space between each graph and its side panel.

Rebalanced graph height allocation after unifying margins.

## V26.4

Added more equal left padding to all graphs so left Y-axis labels sit farther from the software frame.

Increased right Y-axis padding so Raw voltage labels sit farther from the side panels.

Rebalanced graph heights and gave Cosine Error more height.

## V26.5

Tightened vertical spacing around Graph 1 and Graph 2.

Reduced white space by reallocating splitter space and reducing row spacing.

Reduced bottom margins for Graph 1 and Graph 2 while keeping labels visible.

## V26.6

Increased Graph 2 height by redistributing splitter space so the white space around it is used more effectively.

## V26.7

Removed the white boxed background behind the Live Alignment Trend title so it sits cleanly on the graph area.

Removed the autosave feature.

Finalised release preparation for executable packaging.

Updated in software release messaging, About text, and fallback changelog wording.

Refined graph presentation, scan comparison wording, and export behaviour for the final release.

Completed final alignment and interface polish.

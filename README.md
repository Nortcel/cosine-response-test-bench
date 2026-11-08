# Automated cosine-response test bench

An open-hardware bench with a rotating laser source, stationary photodiode, Arduino controller and desktop software for angular-response experiments.

Developed by Attila Preszter — Nortcel Renewables. Contact: attila@nortcel.com.

![Completed bench](hardware/photos/CRTB%20-%20%28A%29%20Completed%20bench.jpg)

## Build and use

- [User manual](docs/User%20manual.md) and [illustrated Word manual](docs/Cosine_Response_Test_Bench_Controller_V26_7_User_Manual.docx)
- [Build instructions](documentation/Build%20instructions.txt)
- [Operation and firmware limitations](documentation/Operation%20and%20validation.txt)
- [Controller V26.7 source and dependencies](software/source/) and [setup instructions](software/BUILD%20AND%20RUN.txt)
- [Firmware V5.2.2 and serial protocol](firmware/)
- [CAD, wiring, bill of materials and photographs](hardware/)
- [Measurement geometry and controller screenshot](figures/)
- [Release notes](https://github.com/Nortcel/cosine-response-test-bench/releases) and [full software changelog](CHANGELOG.md)

## Measurements and analysis

[Historical datasets](data/) and [analysis scripts](analysis/) support reproduction of the reported work. Read [the dataset notes](data/README.txt) before using them: acquisition campaigns are separate, GUI and offline metrics differ, and the optical table is a graph transcription with an unresolved physical reference scale. No raw data have been replaced by reconstructed measurements.

This device supports narrow-band angular screening; it is not a standards-compliant broadband pyranometer calibration facility. Read the operation notes before using the moving arm and laser. The bill of materials states its historical cost basis and exclusions.

## Download

Use **Code → Download ZIP** for the current main-branch files. The existing v26.7 tag was created before these files were uploaded; its automatic source archives contain the earlier snapshot.

This package supplies controller source. A Windows executable is not included while its bundled dependency notices are reviewed. The dependency list is not a verified version lock. V26.7 retains the application's original date of 27 March 2026; GitHub publication occurred later.

## Licences

MIT for original code; CERN-OHL-S-2.0 for original hardware designs; CC-BY-4.0 for original documentation and data. [Licence allocation and third-party notices](licenses/).

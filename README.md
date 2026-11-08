# Automated cosine-response test bench

An open-hardware bench with a rotating laser source, stationary photodiode, Arduino firmware and desktop controller for angular-response experiments.

Developed by **Attila Preszter — Nortcel Renewables**. Contact: attila@nortcel.com.

![Completed cosine-response test bench](hardware/photos/CRTB%20-%20%28A%29%20Completed%20bench.jpg)

## Start here

| What you need | Location |
|---|---|
| V26.7 release notes | [Releases](https://github.com/Nortcel/cosine-response-test-bench/releases) |
| Full development history | [Changelog](CHANGELOG.md) |
| Controller user manual and original illustrated documents | [Manuals](docs/) |
| Controller Python source | [Source code](software/source/) |
| Source setup instructions | [Build and run](software/BUILD%20AND%20RUN.txt) |
| Compatible historical firmware V5.2.2 | [Firmware and serial protocol](firmware/) |
| Build and operation instructions | [Documentation](documentation/) |
| Bill of materials, CAD, circuit and photos | [Hardware](hardware/) |
| Historical measurements and provenance | [Data](data/) |
| Reproducible analysis and outputs | [Analysis](analysis/) |
| Figures | [Figures](figures/) |
| File-level licence allocation | [Licences](licenses/) |

## Downloads and release status

The published v26.7 tag currently records the earlier changelog-only repository snapshot. GitHub's automatic source-code downloads for that tag do **not** include the subsequently added project files. For the current complete repository contents, use **Code → Download ZIP** on the main branch.

The application identifies V26.7 with the date 27 March 2026. Repository publication occurred later. Supplied controller source and firmware are preserved unchanged. The Windows executable is awaiting its bundled dependency and licence-notice inventory and is not included in this public upload. Source setup instructions are available above; the dependency list is not a verified version lock.

## Measurement scope and limitations

The bench supports narrow-band angular-response screening and sensor alignment. It is not a standards-compliant broadband pyranometer calibration facility. The developer reports successful functional operation; this publication does not establish independent fault testing or a bit-identical executable rebuild. Review the firmware limitations before operating the hardware.

Historical workbook measurements and the separate 201-point CSV campaign are distinct datasets. The analysis documentation explains their provenance. GUI normalisation and metrics differ from the offline historical analysis; their values must not be interchanged. Optical graph transcriptions are labelled secondary evidence, not newly recovered raw measurements.

## Licences

Original software, firmware and analysis code: **MIT**. Original hardware designs: **CERN-OHL-S-2.0**. Original documentation, photographs and data: **CC-BY-4.0**. See `licenses/LICENCE MAP.csv` for allocation. Third-party components retain their own terms. The root MIT licence does not relicense hardware, data or third-party materials.

The manuscript and private author-review correspondence are not included here.

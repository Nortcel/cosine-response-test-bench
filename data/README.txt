Measurement data

workbook_cohort contains the unchanged historical workbook inputs used for the article's primary analysis. Each run has 100 measured samples; the analysis adds one explicitly marked constructed endpoint. csv_cohort is a separate historical 201-point campaign and must not be merged with the workbook cohort or treated as current V5.2.2 acquisitions.

optical_graph_transcription contains 20 values transcribed from printed labels in the historical optical-test graph (dissertation Chapter 3, Figure 3-3), not original paired instrument logs. The source graph and figure-source photographs are retained. The original graph uses W/m2, whereas later meter photographs display mW; the plotted scale and conversion are unresolved. The detector label differs between graph title (985) and text (958-1024-1-ND). No conversion or absolute calibration/saturation threshold is established. The optical check is separate from the cosine datasets.

The controller GUI uses dark-offset/central-reference normalisation; the historical offline analysis uses abs(5-V) and peak normalisation. Their error metrics are not interchangeable. See the analysis instructions and code. Original values are preserved; generated outputs can be reproduced from the scripts.

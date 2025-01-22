All iCatcher+ pre-processing code is based on https://osf.io/ndkt6/ and https://github.com/mzettersten/lwl_typ_animals/tree/master/data_analysis/registered_report/analysis/manuscript. We decided to use trial-by-trial recordings instead of a single recording because of known issues with Lookit's trial start time and video start time accuracies because of participant lag.

Torch and iCatcher appear incompatible for Python=3.13, using Python 3.12.

Existing shell script hardcodes using Slurm to analyze the data. This makes the script much easier to adapt to our SSRDE cluster but nowhere else. This annotation system is currently being built to be run on SSRDE. I got rid of Singularity, there is no containerization solution that currently exists on SSRDE. All video data will also only be stored on our Polygon server for now.

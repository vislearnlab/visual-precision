# Running iCatcher+
All pilot data is downloaded 
All iCatcher+ pre-processing code is based on https://osf.io/ndkt6/ and https://github.com/mzettersten/lwl_typ_animals/tree/master/data_analysis/registered_report/analysis/manuscript. 

We decided to use trial-by-trial recordings instead of a single recording because of known issues with Lookit's trial start time and video start time accuracies because of participant lag.

Set up with Torch and iCatcher is reproducible using Python 3.12.

Existing shell script allows Slurm to analyze the data. That allowed us to run this configuration on the SSRDE cluster at [BLINDED]. The original script used the MIT Singularity container which was fully removed since no containerization solution currently exists on SSRDE. All video data is also only be stored remotely on our [BLINDED] server.



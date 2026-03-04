FROM continuumio/miniconda3:23.5.2-0

LABEL maintainer="your-email@example.com"
LABEL description="Long-read QC Pipeline - Mini Bioinformatics Case Study"

WORKDIR /pipeline

# Copy environment file and create conda env
COPY environment.yml .
RUN conda env create -f environment.yml && conda clean -afy

# Activate env by default
SHELL ["conda", "run", "-n", "longread-qc", "/bin/bash", "-c"]

# Copy all pipeline files
COPY . .

# Make scripts executable
RUN chmod +x scripts/read_stats.py scripts/visualize.py

# Default: run the full pipeline
ENTRYPOINT ["conda", "run", "-n", "longread-qc", "snakemake", "--cores", "all", "--use-conda"]

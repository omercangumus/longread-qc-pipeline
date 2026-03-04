# 🧬 longread-qc-pipeline

A reproducible quality control pipeline for long-read sequencing data (Oxford Nanopore Technology).  
Built with **Snakemake**, **NanoPlot**, and custom Python scripts.

---

## 📁 Repository Structure

```
longread-qc-pipeline/
├── workflow/
│   ├── Snakefile           # Pipeline orchestration (Snakemake)
│   └── config/
│       └── config.yaml     # All configurable paths and parameters
├── scripts/
│   ├── read_stats.py       # Custom per-read statistics (GC, length, quality)
│   └── visualize.py        # Distribution plots + summary statistics
├── tests/
│   └── test_read_stats.py  # Unit tests for core functions
├── data/                   # Place your FASTQ file here (not tracked in git)
├── results/                # Pipeline outputs (auto-generated)
│   ├── qc/                 # NanoPlot HTML report + plots
│   ├── stats/              # read_stats.csv + summary_statistics.txt
│   └── plots/              # Distribution plots + dashboard
├── environment.yml         # Conda environment definition
├── Dockerfile              # Docker image definition
├── email_draft.md          # Non-technical report for Prof. Kılıç
└── README.md               # This file
```

---

## ⚙️ Requirements

Choose **one** of the following:

### Option A — Conda (Recommended for local use)

```bash
conda env create -f environment.yml
conda activate longread-qc
```

### Option B — Docker

```bash
docker build -t longread-qc-pipeline .
```

---

## 🚀 How to Run

### 1. Place your FASTQ file

Copy or symlink your `.fastq.gz` file:

```bash
cp /path/to/your/reads.fastq.gz data/sample.fastq.gz
```

Or edit `workflow/config/config.yaml` to point to a different path:

```yaml
input_fastq: "data/your_actual_filename.fastq.gz"
```

### 2. Run the pipeline

**With Conda:**
```bash
conda activate longread-qc
snakemake --cores 4 --use-conda
```

**With Docker:**
```bash
docker run --rm \
  -v $(pwd)/data:/pipeline/data \
  -v $(pwd)/results:/pipeline/results \
  longread-qc-pipeline
```

**Dry run (preview steps without executing):**
```bash
snakemake --cores 4 --dryrun
```

---

## 📊 Pipeline Steps

| Step | Tool | Output |
|------|------|--------|
| 1. Long-read QC | NanoPlot | `results/qc/NanoPlot-report.html` |
| 2. Per-read statistics | Custom Python | `results/stats/read_stats.csv` |
| 3. Visualization + Summary | Custom Python | `results/plots/*.png`, `summary_statistics.txt` |

---

## 📈 Outputs Explained

### `results/qc/NanoPlot-report.html`
Interactive HTML report from NanoPlot, showing read quality, length distributions, and other standard ONT QC metrics. Open in any browser.

### `results/stats/read_stats.csv`
CSV file with one row per read:

| Column | Description |
|--------|-------------|
| `read_id` | Unique read identifier from FASTQ header |
| `read_length` | Length of the sequence in base pairs |
| `gc_content_pct` | GC content as a percentage (0–100) |
| `mean_quality_score` | Mean Phred Q score (biologically correct average) |

### `results/stats/summary_statistics.txt`
Plain-text file with mean, median, std dev, min, max, and N50 (for read length) across all reads.

### `results/plots/`

| File | Description |
|------|-------------|
| `gc_content_distribution.png` | GC content histogram + KDE |
| `read_length_distribution.png` | Read length histogram (log₁₀ scale) |
| `mean_quality_distribution.png` | Quality score distribution + ONT thresholds |
| `combined_dashboard.png` | All 3 plots + summary statistics table |

---

## 🧪 Running Tests

```bash
conda activate longread-qc
pytest tests/ -v
```

---

## 🔧 Configuration

Edit `workflow/config/config.yaml` to customize:

```yaml
sample_name: "my_sample"           # Sample identifier
input_fastq: "data/reads.fastq.gz" # Input file path
nanoplot_threads: 4                # CPU threads for NanoPlot
```

---

## 🐋 Docker Details

Build the image:
```bash
docker build -t longread-qc-pipeline .
```

Run with volume mounts (so data and results persist outside the container):
```bash
docker run --rm \
  -v $(pwd)/data:/pipeline/data \
  -v $(pwd)/results:/pipeline/results \
  longread-qc-pipeline --cores 4
```

---

## 📬 Communication

See [`email_draft.md`](email_draft.md) for a non-technical summary written for Prof. Kılıç explaining the analysis and recommendations.

---

## 🗂️ Technology Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Snakemake | 7.32.4 | Pipeline orchestration |
| NanoPlot | 1.42.0 | Long-read QC (ONT-specific) |
| Python | 3.10 | Custom analysis scripts |
| pandas | 2.0.3 | Data processing |
| matplotlib + seaborn | 3.7.2 / 0.12.2 | Visualization |
| scipy | 1.11.2 | KDE, statistics |
| BioPython | 1.81 | FASTQ parsing support |
| pytest | 7.4.0 | Unit testing |

---

## 📝 Notes on Long-Read Specific Choices

- **NanoPlot** (not FastQC): FastQC is designed for Illumina short reads. NanoPlot is the standard tool for ONT data.
- **Log-scale read length plot**: Long reads span orders of magnitude (hundreds to hundreds of thousands of bp), making log scale essential for meaningful visualization.
- **Phred-correct quality averaging**: Mean quality is computed by averaging error probabilities and converting back to Phred — this is the mathematically correct method, consistent with NanoStat/NanoPlot.
- **Q7 and Q10 threshold lines**: These are standard ONT pass/fail thresholds shown on the quality plot for context.

---

## 👤 Author

Created as part of a Bioinformatics Internship Case Study.  
GitHub: [your-github-username](https://github.com/your-github-username)

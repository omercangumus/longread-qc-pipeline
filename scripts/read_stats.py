#!/usr/bin/env python3
"""
read_stats.py
-------------
Custom script for per-read statistics calculation from FASTQ files.
Calculates: GC content (%), Read Length, Mean Read Quality Score

Usage:
    python scripts/read_stats.py --input data/sample.fastq.gz --output results/stats/read_stats.csv
"""

import argparse
import gzip
import csv
import sys
import os
import numpy as np
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate per-read statistics from a FASTQ file."
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to input FASTQ file (gzipped or plain)"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path to output CSV file"
    )
    return parser.parse_args()


def phred_to_prob(phred_score: int) -> float:
    """Convert Phred quality score to error probability."""
    return 10 ** (-phred_score / 10.0)


def mean_quality_from_scores(quality_string: str) -> float:
    """
    Calculate mean quality score using the correct Phred-averaging method.
    Converts each score to error probability, averages them, converts back.
    This is the biologically correct method (used by NanoStat/NanoPlot).
    """
    phred_scores = [ord(c) - 33 for c in quality_string]
    if not phred_scores:
        return 0.0
    error_probs = [phred_to_prob(q) for q in phred_scores]
    mean_error_prob = np.mean(error_probs)
    if mean_error_prob == 0:
        return 40.0  # cap at Q40
    mean_q = -10 * np.log10(mean_error_prob)
    return round(mean_q, 4)


def calculate_gc_content(sequence: str) -> float:
    """Calculate GC content percentage for a DNA sequence."""
    sequence = sequence.upper()
    total = len(sequence)
    if total == 0:
        return 0.0
    gc_count = sequence.count('G') + sequence.count('C')
    return round((gc_count / total) * 100, 4)


def open_fastq(filepath: str):
    """Open FASTQ file, handling both gzipped and plain text formats."""
    if filepath.endswith('.gz'):
        return gzip.open(filepath, 'rt')
    else:
        return open(filepath, 'r')


def parse_fastq(filepath: str):
    """
    Generator that yields (read_id, sequence, quality_string) tuples.
    Handles standard 4-line FASTQ format.
    """
    with open_fastq(filepath) as f:
        while True:
            header = f.readline().strip()
            if not header:
                break  # End of file
            sequence = f.readline().strip()
            f.readline()  # '+' line, skip
            quality = f.readline().strip()

            if not header.startswith('@'):
                print(f"Warning: Unexpected header format: {header}", file=sys.stderr)
                continue

            read_id = header[1:].split()[0]  # Remove '@' and take first token
            yield read_id, sequence, quality


def process_fastq(input_path: str, output_path: str):
    """Main processing function: parse FASTQ, calculate stats, write CSV."""

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    read_count = 0
    fieldnames = ["read_id", "read_length", "gc_content_pct", "mean_quality_score"]

    print(f"[INFO] Processing: {input_path}", file=sys.stderr)

    with open(output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for read_id, sequence, quality in parse_fastq(input_path):
            read_length = len(sequence)
            gc_content = calculate_gc_content(sequence)
            mean_qual = mean_quality_from_scores(quality)

            writer.writerow({
                "read_id": read_id,
                "read_length": read_length,
                "gc_content_pct": gc_content,
                "mean_quality_score": mean_qual
            })
            read_count += 1

            if read_count % 10000 == 0:
                print(f"[INFO] Processed {read_count:,} reads...", file=sys.stderr)

    print(f"[INFO] Done. Total reads processed: {read_count:,}", file=sys.stderr)
    print(f"[INFO] Output saved to: {output_path}", file=sys.stderr)
    return read_count


def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    read_count = process_fastq(args.input, args.output)

    if read_count == 0:
        print("[WARNING] No reads were processed. Check input file format.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

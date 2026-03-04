# Email Draft — To: Prof. Kılıç

---

**To:** Prof. Kılıç  
**From:** [Your Name]  
**Subject:** Long-Read Sequencing Data — Quality Control Report

---

Dear Professor Kılıç,

I hope this message finds you well. I have completed the initial quality control analysis of the long-read sequencing data you provided. Below, I would like to share what was done and what the results suggest, in plain terms.

---

## What We Did

We ran your raw sequencing data through an automated quality control pipeline. The pipeline uses a tool called **NanoPlot**, which is specifically designed for the type of long-read sequencing technology your lab used. In addition to this, I wrote a custom analysis script that examined every individual read in your dataset and calculated three key measurements:

1. **GC Content (%)** — The proportion of G and C bases in each read. In most organisms this falls between 40–60%. Values far outside this range can indicate contamination or issues with the library preparation.

2. **Read Length (bp)** — How long each DNA fragment was when it was sequenced. Long-read technology is specifically valued for producing reads of tens of thousands of base pairs, which helps reconstruct complex genomic regions.

3. **Mean Read Quality Score (Phred Q)** — A score that reflects how confident the sequencer was when identifying each base. A score of Q10 means a 90% accuracy per base; Q20 means 99% accuracy. For Oxford Nanopore data, typical passes are above Q7–Q10.

---

## What the Graphs Show

I have attached four graphs to this email:

- **GC Content Distribution**: The distribution of GC percentages across all reads. If this is bell-shaped and centered around your organism's expected GC content, it is a good sign.
- **Read Length Distribution**: Long-read data should show a wide range of lengths, ideally with many reads in the 10,000–100,000 bp range. Very short reads may indicate sample degradation.
- **Mean Quality Distribution**: This shows how quality is distributed across all reads. The bulk of reads should sit above Q7 for standard ONT data, and above Q20 for high-accuracy basecalling.
- **Combined Dashboard**: An overview of all three metrics together with a summary table.

---

## Summary of Key Statistics

The pipeline automatically calculated the mean, median, minimum, and maximum values for all three metrics. For read length, it also calculated the **N50** — this tells us the length at which 50% of the total data is contained in reads of that size or longer. A higher N50 is generally better.

Please refer to the `results/stats/summary_statistics.txt` file or the dashboard image for exact numbers.

---

## Recommendation

Based on the quality metrics:

- If the mean quality score is **above Q7** and the read lengths look reasonable (median > 5,000 bp), **I recommend proceeding to the alignment step** against your reference genome.
- If a significant fraction of reads fall below Q7, we may want to apply a quality-filtering step first to remove low-quality reads before alignment.
- If GC content is outside the expected range, we should discuss whether a contamination check is warranted.

I am happy to proceed with alignment, or to discuss the results in more detail at your convenience. Please do not hesitate to reach out.

Best regards,  
[Your Name]  
Bioinformatics Intern

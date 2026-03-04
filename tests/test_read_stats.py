#!/usr/bin/env python3
"""
Unit tests for read_stats.py helper functions.
Run with: pytest tests/test_read_stats.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from read_stats import calculate_gc_content, mean_quality_from_scores, phred_to_prob


class TestGCContent:
    def test_pure_gc(self):
        assert calculate_gc_content("GGCC") == 100.0

    def test_pure_at(self):
        assert calculate_gc_content("AATT") == 0.0

    def test_mixed(self):
        assert calculate_gc_content("ATGC") == 50.0

    def test_empty(self):
        assert calculate_gc_content("") == 0.0

    def test_lowercase(self):
        assert calculate_gc_content("atgc") == 50.0


class TestMeanQuality:
    def test_uniform_q20(self):
        # ASCII for Q20: ord(char) - 33 = 20 => char = chr(53) = '5'
        q_str = "5" * 10
        result = mean_quality_from_scores(q_str)
        assert abs(result - 20.0) < 0.01

    def test_empty(self):
        assert mean_quality_from_scores("") == 0.0

    def test_returns_float(self):
        assert isinstance(mean_quality_from_scores("IIIII"), float)


class TestPhredConversion:
    def test_q20_probability(self):
        prob = phred_to_prob(20)
        assert abs(prob - 0.01) < 1e-6

    def test_q30_probability(self):
        prob = phred_to_prob(30)
        assert abs(prob - 0.001) < 1e-7

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Reverse Key Converter transformation and validation logic.

Run:  py -m unittest test_logic -v
"""

import sys
import unittest

sys.path.insert(0, '.')
from reverse_key_converter import transform_line, is_line_valid, process_content, extract_hex_only


class TestTransformLine(unittest.TestCase):
    """Tests for transform_line(): reversing hex byte groups of 4."""

    # ── Original format: prefix with colon + Current/Next ────────────

    def test_key_3B_01_current(self):
        self.assertEqual(
            transform_line("01 Key 3B: F8 BB 1E BE AE D7 E9 A8 61 AC F1 C0 21 6B BD 6F 92 C2 F2 C0 62 FC 95 CF BB 79 22 A1 31 5F DA B6 Current"),
            "01 Key 3B: BE 1E BB F8 A8 E9 D7 AE C0 F1 AC 61 6F BD 6B 21 C0 F2 C2 92 CF 95 FC 62 A1 22 79 BB B6 DA 5F 31 Current",
        )

    def test_key_3B_06_current(self):
        self.assertEqual(
            transform_line("06 Key 3B: 95 48 87 18 9D 2B E5 A4 97 34 52 88 DD 0D AD 8A A2 AB A3 A6 49 BF 5B F8 F8 46 3C D5 AB 60 1B 19 Current"),
            "06 Key 3B: 18 87 48 95 A4 E5 2B 9D 88 52 34 97 8A AD 0D DD A6 A3 AB A2 F8 5B BF 49 D5 3C 46 F8 19 1B 60 AB Current",
        )

    def test_key_3B_07_current(self):
        self.assertEqual(
            transform_line("07 Key 3B: 38 E4 DB 5E B2 C5 2C EC EA 56 08 CC C5 93 36 12 81 2F FB 0E E4 4B 8E C3 17 A9 0E BD 46 71 3D 88 Current"),
            "07 Key 3B: 5E DB E4 38 EC 2C C5 B2 CC 08 56 EA 12 36 93 C5 0E FB 2F 81 C3 8E 4B E4 BD 0E A9 17 88 3D 71 46 Current",
        )

    def test_key_3B_0F_current(self):
        self.assertEqual(
            transform_line("0F Key 3B: BA BE A3 92 A0 2E 4B 6B AA CB 57 89 D4 75 50 AD 86 05 71 54 30 D4 5B 3C F9 88 2A 6C A8 9C 95 BC Current"),
            "0F Key 3B: 92 A3 BE BA 6B 4B 2E A0 89 57 CB AA AD 50 75 D4 54 71 05 86 3C 5B D4 30 6C 2A 88 F9 BC 95 9C A8 Current",
        )

    def test_key_56_01_next(self):
        self.assertEqual(
            transform_line("01 Key 56: FF F9 A7 1D 30 00 14 F1 F5 33 F8 6F 43 42 35 F4 F6 B7 F0 92 4A 39 25 A2 79 28 E2 BD A7 E9 4B A9 Next"),
            "01 Key 56: 1D A7 F9 FF F1 14 00 30 6F F8 33 F5 F4 35 42 43 92 F0 B7 F6 A2 25 39 4A BD E2 28 79 A9 4B E9 A7 Next",
        )

    def test_key_56_06_next(self):
        self.assertEqual(
            transform_line("06 Key 56: F2 E7 6A 63 21 AD AE 54 0B 06 D7 F4 71 4D E2 DA 48 5B EE 52 51 22 83 EA 91 C7 9D 83 40 8A 5F 47 Next"),
            "06 Key 56: 63 6A E7 F2 54 AE AD 21 F4 D7 06 0B DA E2 4D 71 52 EE 5B 48 EA 83 22 51 83 9D C7 91 47 5F 8A 40 Next",
        )

    def test_key_56_07_next(self):
        self.assertEqual(
            transform_line("07 Key 56: 7F BC 12 BE 9C F4 29 DE A2 50 90 A5 21 AD 54 7C 48 50 38 31 65 A5 0A 52 AF 30 FF B2 F7 1D 97 F6 Next"),
            "07 Key 56: BE 12 BC 7F DE 29 F4 9C A5 90 50 A2 7C 54 AD 21 31 38 50 48 52 0A A5 65 B2 FF 30 AF F6 97 1D F7 Next",
        )

    def test_key_56_0F_next(self):
        self.assertEqual(
            transform_line("0F Key 56: 8F B0 1F DA D0 CE EA CC E0 F5 65 71 DB 0E 07 04 A5 01 DE 6A 51 63 BD B5 F9 61 00 FE 5D 68 BF 9D Next"),
            "0F Key 56: DA 1F B0 8F CC EA CE D0 71 65 F5 E0 04 07 0E DB 6A DE 01 A5 B5 BD 63 51 FE 00 61 F9 9D BF 68 5D Next",
        )

    # ── No prefix, with or without Current/Next ─────────────────────

    def test_hex_with_current_no_prefix(self):
        self.assertEqual(
            transform_line("F8 BB 1E BE AE D7 E9 A8 61 AC F1 C0 21 6B BD 6F 92 C2 F2 C0 62 FC 95 CF BB 79 22 A1 31 5F DA B6 Current"),
            "BE 1E BB F8 A8 E9 D7 AE C0 F1 AC 61 6F BD 6B 21 C0 F2 C2 92 CF 95 FC 62 A1 22 79 BB B6 DA 5F 31 Current",
        )

    def test_hex_only_no_prefix_no_suffix(self):
        self.assertEqual(
            transform_line("F8 BB 1E BE AE D7 E9 A8 61 AC F1 C0 21 6B BD 6F 92 C2 F2 C0 62 FC 95 CF BB 79 22 A1 31 5F DA B6"),
            "BE 1E BB F8 A8 E9 D7 AE C0 F1 AC 61 6F BD 6B 21 C0 F2 C2 92 CF 95 FC 62 A1 22 79 BB B6 DA 5F 31",
        )

    def test_short_4_bytes(self):
        self.assertEqual(transform_line("AE D7 E9 A8"), "A8 E9 D7 AE")

    # ── Non-hex prefixes and suffixes ────────────────────────────────

    def test_underscore_prefix(self):
        """07_56 is not hex — only the hex bytes after it are reversed."""
        self.assertEqual(
            transform_line("07_56    D2 5D 86 42 A7 B5 78 F6 F5 50 93 03 DF 82 2C ED 6F 03 F1 A8 05 44 72 75 89 4F 62 2E 78 2B EC 85"),
            "07_56    42 86 5D D2 F6 78 B5 A7 03 93 50 F5 ED 2C 82 DF A8 F1 03 6F 75 72 44 05 2E 62 4F 89 85 EC 2B 78",
        )

    def test_arrow_prefix_paren_suffix(self):
        """RX <- prefix and (1 мс.) suffix are preserved."""
        self.assertEqual(
            transform_line("RX <- 56 8F B5 BF 7E 47 0B 2C 55 A6 15 47 3C 8F 77 CE D5 73 39 C1 F1 9A 44 96 7D 96 96 8F DE 4B A8 21 (1 мс.)"),
            "RX <- BF B5 8F 56 2C 0B 47 7E 47 15 A6 55 CE 77 8F 3C C1 39 73 D5 96 44 9A F1 8F 96 96 7D 21 A8 4B DE (1 мс.)",
        )

    # ── Separators: commas, semicolons, pipes, brackets ──────────────

    def test_comma_separated(self):
        self.assertEqual(
            transform_line("83 40 8A 5F, 83 40 8A 5F"),
            "5F 8A 40 83, 5F 8A 40 83",
        )

    def test_triple_comma_separated(self):
        self.assertEqual(
            transform_line("83 40 8A 5F, 83 40 8A 5F, 83 40 8A 5F"),
            "5F 8A 40 83, 5F 8A 40 83, 5F 8A 40 83",
        )

    def test_brackets(self):
        self.assertEqual(transform_line("[A1 B2 C3 D4]"), "[D4 C3 B2 A1]")

    def test_semicolon_separator(self):
        self.assertEqual(
            transform_line("A1 B2 C3 D4; E5 F6 A7 B8"),
            "D4 C3 B2 A1; B8 A7 F6 E5",
        )

    def test_pipe_separator(self):
        self.assertEqual(
            transform_line("A1 B2 C3 D4 | E5 F6 A7 B8"),
            "D4 C3 B2 A1 | B8 A7 F6 E5",
        )

    # ── Lowercase and mixed case hex ─────────────────────────────────

    def test_lowercase_hex(self):
        self.assertEqual(transform_line("ae d7 e9 a8"), "a8 e9 d7 ae")

    def test_mixed_case_hex(self):
        self.assertEqual(transform_line("Ae d7 E9 a8"), "a8 E9 d7 Ae")

    # ── Pass-through (no transformation) ─────────────────────────────

    def test_empty_line(self):
        self.assertEqual(transform_line(""), "")

    def test_non_hex_text(self):
        self.assertEqual(transform_line("Some random text"), "Some random text")

    def test_whitespace_only(self):
        self.assertEqual(transform_line("   "), "   ")


class TestIsLineValid(unittest.TestCase):
    """Tests for is_line_valid(): hex byte count must be divisible by 4."""

    def test_empty_line(self):
        self.assertTrue(is_line_valid(""))

    def test_whitespace_only(self):
        self.assertTrue(is_line_valid("   "))

    def test_4_bytes(self):
        self.assertTrue(is_line_valid("F8 BB 1E BE"))

    def test_8_bytes(self):
        self.assertTrue(is_line_valid("F8 BB 1E BE AE D7 E9 A8"))

    def test_32_bytes_with_current(self):
        self.assertTrue(is_line_valid(
            "F8 BB 1E BE AE D7 E9 A8 61 AC F1 C0 21 6B BD 6F "
            "92 C2 F2 C0 62 FC 95 CF BB 79 22 A1 31 5F DA B6 Current"
        ))

    def test_prefix_colon_format(self):
        self.assertTrue(is_line_valid("01 Key 3B: F8 BB 1E BE Current"))

    def test_underscore_prefix(self):
        self.assertTrue(is_line_valid("07_56    D2 5D 86 42 A7 B5 78 F6"))

    def test_arrow_prefix(self):
        self.assertTrue(is_line_valid("RX <- 56 8F B5 BF 7E 47 0B 2C (1 мс.)"))

    def test_comma_separated_valid(self):
        self.assertTrue(is_line_valid("83 40 8A 5F, 83 40 8A 5F"))

    def test_no_hex_content(self):
        """Lines with no hex bytes are not key lines — no red highlight."""
        self.assertTrue(is_line_valid("Some random text"))

    # ── Invalid lines ────────────────────────────────────────────────

    def test_3_bytes_invalid(self):
        self.assertFalse(is_line_valid("AE D7 E9"))

    def test_5_bytes_invalid(self):
        self.assertFalse(is_line_valid("AE D7 E9 A8 B1"))

    def test_comma_separated_one_bad_group(self):
        """First group OK (4 bytes), second group has 3 bytes."""
        self.assertFalse(is_line_valid("83 40 8A 5F, 83 40 8A"))


class TestProcessContent(unittest.TestCase):
    """Tests for process_content(): multi-line processing."""

    def test_multiline(self):
        inp = (
            "01 Key 3B: F8 BB 1E BE AE D7 E9 A8 Current\n"
            "AE D7 E9 A8\n"
            "\n"
            "Some comment"
        )
        expected = (
            "01 Key 3B: BE 1E BB F8 A8 E9 D7 AE Current\n"
            "A8 E9 D7 AE\n"
            "\n"
            "Some comment"
        )
        self.assertEqual(process_content(inp), expected)

    def test_mixed_formats(self):
        inp = (
            "07_56    D2 5D 86 42 A7 B5 78 F6\n"
            "83 40 8A 5F, 83 40 8A 5F"
        )
        expected = (
            "07_56    42 86 5D D2 F6 78 B5 A7\n"
            "5F 8A 40 83, 5F 8A 40 83"
        )
        self.assertEqual(process_content(inp), expected)


class TestExtractHexOnly(unittest.TestCase):
    """Tests for extract_hex_only(): stripping non-hex text."""

    def test_empty_line(self):
        self.assertEqual(extract_hex_only(""), "")

    def test_whitespace_only(self):
        self.assertEqual(extract_hex_only("   "), "")

    def test_no_hex(self):
        self.assertEqual(extract_hex_only("Some random text"), "")

    def test_plain_hex(self):
        self.assertEqual(
            extract_hex_only("F8 BB 1E BE AE D7 E9 A8"),
            "F8 BB 1E BE AE D7 E9 A8",
        )

    def test_prefix_colon_stripped(self):
        # "01" and "3B" are valid hex tokens — they are kept
        self.assertEqual(
            extract_hex_only("01 Key 3B: F8 BB 1E BE Current"),
            "01 3B F8 BB 1E BE",
        )

    def test_underscore_prefix_stripped(self):
        self.assertEqual(
            extract_hex_only("07_56    D2 5D 86 42 A7 B5 78 F6"),
            "D2 5D 86 42 A7 B5 78 F6",
        )

    def test_arrow_prefix_and_paren_suffix_stripped(self):
        self.assertEqual(
            extract_hex_only("RX <- 56 8F B5 BF 7E 47 0B 2C (1 мс.)"),
            "56 8F B5 BF 7E 47 0B 2C",
        )

    def test_comma_separated_merged(self):
        self.assertEqual(
            extract_hex_only("83 40 8A 5F, 83 40 8A 5F"),
            "83 40 8A 5F 83 40 8A 5F",
        )

    def test_brackets_stripped(self):
        self.assertEqual(extract_hex_only("[A1 B2 C3 D4]"), "A1 B2 C3 D4")

    def test_pipe_separated_merged(self):
        self.assertEqual(
            extract_hex_only("A1 B2 C3 D4 | E5 F6 A7 B8"),
            "A1 B2 C3 D4 E5 F6 A7 B8",
        )


class TestProcessContentStripped(unittest.TestCase):
    """Tests for process_content() with strip_extra=True."""

    def test_multiline_stripped(self):
        inp = (
            "01 Key 3B: F8 BB 1E BE AE D7 E9 A8 Current\n"
            "AE D7 E9 A8\n"
            "\n"
            "Some comment"
        )
        # "01" and "3B" are valid hex tokens from the prefix — kept after stripping
        expected = (
            "01 3B BE 1E BB F8 A8 E9 D7 AE\n"
            "A8 E9 D7 AE\n"
            "\n"
            ""
        )
        self.assertEqual(process_content(inp, strip_extra=True), expected)

    def test_comma_separated_stripped(self):
        inp = "83 40 8A 5F, 83 40 8A 5F"
        expected = "5F 8A 40 83 5F 8A 40 83"
        self.assertEqual(process_content(inp, strip_extra=True), expected)


if __name__ == "__main__":
    unittest.main()

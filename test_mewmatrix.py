#!/usr/bin/env python3
"""
Comprehensive test suite for mewmatrix and meowmatrix.
"""

import importlib
import io
import json
import os
import re
import tempfile
import unicodedata
import unittest
from unittest.mock import patch
import mewmatrix


def visual_len(s: str) -> int:
    """Calculate terminal visual column width ignoring ANSI escape codes."""
    clean = re.sub(r"\x1b\[[0-9;]*m|\x1b\[\??[0-9;]*[a-zA-Z]", "", s)
    length = 0
    for ch in clean:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            length += 2
        else:
            length += 1
    return length


class TestMewMatrix(unittest.TestCase):
    def test_bold_head_rendering(self):
        """Verify that ANSI_BOLD_WHITE is actually rendered on drop heads when bold_head is True."""
        sim = mewmatrix.MatrixSimulation(
            cols=10,
            rows=10,
            chars=mewmatrix.CHARSETS["ascii"],
            colors=["32"],
            density=0.0,
            tail_len=5,
        )
        renderer = mewmatrix.MatrixRenderer(bold_head=True)
        sim.drops[0] = 0

        found_bold = False
        for _ in range(8):
            sim.step()
            frame = renderer.render(sim)
            if mewmatrix.ANSI_BOLD_WHITE in frame:
                found_bold = True
                break
        self.assertTrue(found_bold, "ANSI_BOLD_WHITE should be rendered for the drop head")

    def test_meow_mode_line_widths_odd_and_even_cols(self):
        """Verify that meow mode never overflows terminal line width, even with odd columns."""
        for cols in [15, 16, 21, 22, 79, 80]:
            sim = mewmatrix.MatrixSimulation(
                cols=cols,
                rows=8,
                chars=mewmatrix.CAT_EMOJIS,
                colors=["32"],
                density=0.0,
                tail_len=4,
                col_stride=2,
            )
            renderer = mewmatrix.MatrixRenderer(bold_head=True)
            for step in range(10):
                sim.step()
                frame = renderer.render(sim)
                lines = frame.split("\n")
                for line_idx, line in enumerate(lines):
                    vlen = visual_len(line)
                    self.assertEqual(
                        vlen,
                        cols,
                        f"cols={cols}, step={step}, line {line_idx} visual width {vlen} != {cols}",
                    )

    def test_color_resolution(self):
        """Verify resolution of standard colors, rainbow, cat aliases, and config fallback."""
        self.assertEqual(mewmatrix.resolve_colors(["red"], "green"), ["31"])
        self.assertEqual(mewmatrix.resolve_colors(["blue", "red"], "green"), ["34", "31"])
        self.assertEqual(mewmatrix.resolve_colors(["rainbow"], "green"), mewmatrix.RAINBOW_COLORS)
        self.assertEqual(mewmatrix.resolve_colors(["all"], "green"), mewmatrix.RAINBOW_COLORS)
        self.assertEqual(mewmatrix.resolve_colors([], "rainbow"), mewmatrix.RAINBOW_COLORS)
        self.assertEqual(mewmatrix.resolve_colors([], "cyan"), ["36"])
        # Config color as list
        self.assertEqual(mewmatrix.resolve_colors([], ["red", "blue"]), ["31", "34"])
        # Config color as comma-separated string
        self.assertEqual(mewmatrix.resolve_colors([], "red, blue"), ["31", "34"])

    def test_cat_color_aliases(self):
        """Verify cat-themed color aliases work properly."""
        self.assertEqual(mewmatrix.resolve_colors(["purr"], "green"), ["32"])
        self.assertEqual(mewmatrix.resolve_colors(["hiss"], "green"), ["31"])
        self.assertEqual(mewmatrix.resolve_colors(["nya"], "green"), ["36"])
        self.assertEqual(mewmatrix.resolve_colors(["mew"], "green"), ["35"])
        self.assertEqual(mewmatrix.resolve_colors(["angry"], "green"), ["33"])
        self.assertEqual(mewmatrix.resolve_colors(["trill"], "green"), ["34"])

    def test_tail_length_bounds_and_no_crash(self):
        """Verify simulation never crashes with invalid or negative tail lengths."""
        for bad_tail in [-10, 0, 1, 100]:
            sim = mewmatrix.MatrixSimulation(
                cols=10,
                rows=10,
                chars="abc",
                colors=["32"],
                density=0.5,
                tail_len=bad_tail,
            )
            for _ in range(20):
                sim.step()
            sim.resize(15, 12)
            for _ in range(10):
                sim.step()

    def test_corrupt_config_loading(self):
        """Verify load_config handles missing or corrupted json gracefully."""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".meow") as f:
            f.write("{invalid json: here")
            temp_path = f.name
        try:
            old_paths = mewmatrix.CONFIG_PATHS
            mewmatrix.CONFIG_PATHS = [temp_path]
            cfg = mewmatrix.load_config()
            self.assertEqual(cfg["color"], "green")
            self.assertEqual(cfg["speed"], 0.05)
        finally:
            mewmatrix.CONFIG_PATHS = old_paths
            os.remove(temp_path)

    def test_print_help(self):
        """Verify print_help outputs usage without error."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            mewmatrix.print_help()
        output = buf.getvalue()
        self.assertIn("Usage:", output)
        self.assertIn("meow", output)
        self.assertIn("rainbow", output)

    def test_init_config(self):
        """Verify init_config writes valid JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            target_cfg = os.path.join(tmpdir, "config.meow")
            old_primary = mewmatrix.PRIMARY_CONFIG_FILE
            mewmatrix.PRIMARY_CONFIG_FILE = target_cfg
            try:
                mewmatrix.init_config()
                self.assertTrue(os.path.isfile(target_cfg))
                with open(target_cfg, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertEqual(data["color"], "green")
            finally:
                mewmatrix.PRIMARY_CONFIG_FILE = old_primary

    def test_pip_package_parity(self):
        """Verify that meowmatrix_pip has identical bugfixes."""
        import sys
        sys.path.insert(0, os.path.abspath("meowmatrix_pip"))
        import meowmatrix as pip_meow
        self.assertEqual(pip_meow.resolve_colors(["hiss"], "green"), ["31"])
        sim = pip_meow.MatrixSimulation(
            cols=15, rows=6, chars=pip_meow.CAT_EMOJIS, colors=["32"],
            density=0.0, tail_len=4, col_stride=2
        )
        sim.step()
        renderer = pip_meow.MatrixRenderer(bold_head=True)
        frame = renderer.render(sim)
        for line in frame.split("\n"):
            self.assertEqual(visual_len(line), 15)


if __name__ == "__main__":
    unittest.main()

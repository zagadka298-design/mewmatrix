#!/usr/bin/env python3
"""
MewMatrix - A terminal matrix rain with multi-color mixing, cat mode, and self-updater.
"""

from __future__ import annotations

import atexit
import json
import os
import random
import re
import shutil
import signal
import sys
import time
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

__version__ = "2.2.0"

GITHUB_RAW_URL = "https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/mewmatrix.py"
GITHUB_REPO_URL = "https://github.com/zagadka298-design/mewmatrix"
UPDATE_CACHE_FILE = os.path.expanduser("~/.config/mewmatrix/.last_update_check")

# Configuration paths searched in priority order
CONFIG_PATHS: List[str] = [
    os.path.expanduser("~/.config/mewmatrix/config.meow"),
    os.path.expanduser("~/.config/meowmatrix/config.meow"),
]
PRIMARY_CONFIG_FILE = CONFIG_PATHS[0]
FALLBACK_CONFIG_FILE = CONFIG_PATHS[1]

# Color mappings to standard ANSI foreground color codes, including cat-themed aliases
COLOR_CODES: Dict[str, str] = {
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    # Cat aliases
    "purr": "32",
    "hiss": "31",
    "angry": "33",
    "trill": "34",
    "mew": "35",
    "nya": "36",
}

# Ordered rainbow colors
RAINBOW_COLORS: List[str] = [
    "31",  # red
    "32",  # green
    "33",  # yellow
    "34",  # blue
    "35",  # magenta
    "36",  # cyan
    "37",  # white
]

DEFAULT_CONFIG: Dict[str, Any] = {
    "color": "green",
    "speed": 0.05,
    "density": 0.78,
    "charset": "full",
    "tail_length": 15,
    "bold_head": True,
    "check_updates": True,
}

CHARSETS: Dict[str, str] = {
    "full": "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ascii": "abcdefghijklmnopqrstuvwxyz0123456789",
    "hex": "0123456789ABCDEF",
}

CAT_EMOJIS: str = "🐱😺😸😻😽😼🙀😿😾"

# ANSI Terminal Escape Sequences
ANSI_CLEAR_SCREEN = "\033[2J"
ANSI_CURSOR_HOME = "\033[H"
ANSI_HIDE_CURSOR = "\033[?25l"
ANSI_SHOW_CURSOR = "\033[?25h"
ANSI_DISABLE_AUTOWRAP = "\033[?7l"
ANSI_ENABLE_AUTOWRAP = "\033[?7h"
ANSI_RESET = "\033[0m"
ANSI_BOLD_WHITE = "\033[1;97m"


def restore_terminal() -> None:
    """Ensure cursor visibility and autowrap state are restored on program exit."""
    try:
        sys.stdout.write(ANSI_SHOW_CURSOR + ANSI_ENABLE_AUTOWRAP + ANSI_RESET)
        sys.stdout.flush()
    except (OSError, ValueError):
        pass


# Backwards compatibility alias
restore_cursor = restore_terminal

atexit.register(restore_terminal)


def get_terminal_dimensions() -> Tuple[int, int]:
    """Return terminal (columns, lines) with safe minimum bounds and fallback."""
    try:
        size = os.get_terminal_size()
        return max(size.columns, 2), max(size.lines, 2)
    except OSError:
        return 80, 24


def load_config() -> dict:
    """
    Safely load configuration from config.meow, falling back to defaults
    if the file does not exist or contains invalid JSON.
    """
    cfg = dict(DEFAULT_CONFIG)
    for config_path in CONFIG_PATHS:
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        cfg.update(loaded)
                        break
            except (OSError, json.JSONDecodeError):
                pass
    return cfg


def init_config() -> None:
    """Create a default configuration file."""
    try:
        os.makedirs(os.path.dirname(PRIMARY_CONFIG_FILE), exist_ok=True)
        with open(PRIMARY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"config saved to {PRIMARY_CONFIG_FILE}")
    except OSError as e:
        print(f"Error creating config file: {e}", file=sys.stderr)


def parse_version(version_str: str) -> Tuple[int, ...]:
    """Parse a semver version string like '2.2.0' into a tuple of integers for comparison."""
    try:
        clean = re.sub(r"[^\d.]", "", str(version_str))
        return tuple(int(x) for x in clean.split(".") if x)
    except Exception:
        return (0,)


def fetch_remote_version(timeout: float = 4.0) -> Tuple[Optional[str], Optional[str]]:
    """Fetch the latest script and remote version string from GitHub."""
    try:
        req = urllib.request.Request(
            GITHUB_RAW_URL,
            headers={"User-Agent": f"MewMatrix-Updater/{__version__}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read().decode("utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        remote_ver = match.group(1) if match else None
        return remote_ver, content
    except Exception:
        return None, None


def check_for_updates_background() -> Optional[str]:
    """
    Check for updates at most once every 24 hours.
    Returns the new version string if an update is available, or None.
    Fails silently so matrix startup is never delayed or disrupted.
    """
    try:
        now = time.time()
        last_check_time = 0.0
        cached_remote_ver: Optional[str] = None

        if os.path.isfile(UPDATE_CACHE_FILE):
            try:
                with open(UPDATE_CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    last_check_time = float(data.get("timestamp", 0))
                    cached_remote_ver = data.get("version")
            except Exception:
                pass

        # If checked within the last 24 hours (86400 seconds)
        if (now - last_check_time) < 86400:
            if cached_remote_ver and parse_version(cached_remote_ver) > parse_version(__version__):
                return cached_remote_ver
            return None

        # Fetch with short timeout (1.5 seconds)
        remote_ver, _ = fetch_remote_version(timeout=1.5)
        if remote_ver:
            try:
                os.makedirs(os.path.dirname(UPDATE_CACHE_FILE), exist_ok=True)
                with open(UPDATE_CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump({"timestamp": now, "version": remote_ver}, f)
            except Exception:
                pass

            if parse_version(remote_ver) > parse_version(__version__):
                return remote_ver
    except Exception:
        pass
    return None


def update_mewmatrix(force: bool = False) -> None:
    """Download and install the latest version of MewMatrix from GitHub."""
    print("🐱 Checking for MewMatrix updates from GitHub...")
    remote_ver, content = fetch_remote_version(timeout=6.0)

    if not remote_ver or not content:
        print("❌ Could not connect to GitHub or fetch the latest version.")
        print(f"👉 Check your internet connection or visit: {GITHUB_REPO_URL}")
        return

    curr_tuple = parse_version(__version__)
    remote_tuple = parse_version(remote_ver)

    if not force and remote_tuple <= curr_tuple:
        print(f"✨ MewMatrix is already at the latest version (v{__version__})!")
        print("To reinstall/refresh anyway, run: mewmatrix --update --force")
        return

    print(f"📥 Updating MewMatrix: v{__version__} -> v{remote_ver}...")

    # Validate Python code syntax before writing
    try:
        compile(content, "<mewmatrix_update>", "exec")
    except Exception as e:
        print(f"❌ Downloaded update failed syntax validation: {e}")
        return

    # Find candidate paths to update
    candidate_paths: List[str] = []

    # 1. Location found in PATH
    which_path = shutil.which("mewmatrix")
    if which_path:
        candidate_paths.append(which_path)

    # 2. Location of current running file
    try:
        self_file = os.path.abspath(__file__)
        if self_file not in candidate_paths:
            candidate_paths.append(self_file)
    except Exception:
        pass

    # 3. Standard user and system locations
    for standard_path in [
        os.path.expanduser("~/.local/bin/mewmatrix"),
        "/usr/local/bin/mewmatrix",
    ]:
        if standard_path not in candidate_paths and os.path.exists(standard_path):
            candidate_paths.append(standard_path)

    updated_any = False
    for path in candidate_paths:
        try:
            real_target = os.path.realpath(path)
            paths_to_update = {real_target, path}

            for p in paths_to_update:
                if os.path.isdir(p):
                    continue
                os.makedirs(os.path.dirname(p), exist_ok=True)
                tmp_file = p + ".tmp"
                with open(tmp_file, "w", encoding="utf-8") as f:
                    f.write(content)
                os.chmod(tmp_file, 0o755)
                os.replace(tmp_file, p)

                # Clean any cached bytecode
                pycache_dir = os.path.join(os.path.dirname(p), "__pycache__")
                if os.path.isdir(pycache_dir):
                    shutil.rmtree(pycache_dir, ignore_errors=True)
                updated_any = True
        except PermissionError:
            print(f"⚠️ Permission denied when writing to: {path}")
        except Exception as e:
            print(f"⚠️ Could not update {path}: {e}")

    # Fallback to ~/.local/bin/mewmatrix if no existing targets succeeded
    if not updated_any:
        fallback_path = os.path.expanduser("~/.local/bin/mewmatrix")
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            tmp_file = fallback_path + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                f.write(content)
            os.chmod(tmp_file, 0o755)
            os.replace(tmp_file, fallback_path)
            updated_any = True
        except Exception as e:
            print(f"❌ Failed to install update to {fallback_path}: {e}")
            print("👉 Try running with sudo: sudo mewmatrix --update")
            return

    # Update cache record
    try:
        os.makedirs(os.path.dirname(UPDATE_CACHE_FILE), exist_ok=True)
        with open(UPDATE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"timestamp": time.time(), "version": remote_ver}, f)
    except Exception:
        pass

    # Ensure meowmatrix alias / symlink exists in ~/.local/bin
    try:
        user_meow = os.path.expanduser("~/.local/bin/meowmatrix")
        user_mew = os.path.expanduser("~/.local/bin/mewmatrix")
        if os.path.exists(user_mew) and not os.path.exists(user_meow):
            os.symlink(user_mew, user_meow)
    except Exception:
        pass

    print(f"🎉 MewMatrix successfully updated to v{remote_ver}!")
    print("Run 'mewmatrix --version' to verify.")


def print_help() -> None:
    """Print usage and help information."""
    prog = os.path.basename(sys.argv[0]) if sys.argv and sys.argv[0] else "mewmatrix"
    if prog.endswith(".py"):
        prog = prog[:-3]
    if prog == "__main__":
        prog = "mewmatrix"

    help_text = f"""🐱 MewMatrix v{__version__} - Terminal matrix rain with colors & cats!

Usage:
  {prog} [OPTIONS] [COLORS...]

Options:
  meow             Enable cat emoji mode 🐱
  --update         Check and automatically update to the latest version
  --version, -v    Show version information
  --init           Create default config file (~/.config/mewmatrix/config.meow)
  -h, --help       Show this help message

Colors (can be combined):
  green, red, blue, cyan, magenta, yellow, white
  purr, hiss, nya, mew, angry, trill
  rainbow, all     Cycle through all colors

Examples:
  {prog}
  {prog} meow
  {prog} red blue
  {prog} meow rainbow
  {prog} --update
"""
    print(help_text.strip())


def resolve_colors(args: List[str], config_color: Any) -> List[str]:
    """
    Determine the active ANSI color codes based on command-line arguments
    and configuration settings.
    """
    selected: List[str] = []
    has_rainbow = False

    for arg in args:
        lower = str(arg).lower()
        if lower in ("rainbow", "all"):
            has_rainbow = True
        elif lower in COLOR_CODES:
            selected.append(COLOR_CODES[lower])

    if has_rainbow:
        return list(RAINBOW_COLORS)

    if selected:
        # Preserve order while removing duplicates
        return list(dict.fromkeys(selected))

    # Fallback to config setting
    config_colors: List[str] = []
    if isinstance(config_color, list):
        config_items = [str(c).lower().strip() for c in config_color]
    elif isinstance(config_color, str):
        config_items = [c.strip().lower() for c in config_color.replace(",", " ").split() if c.strip()]
    else:
        config_items = []

    for item in config_items:
        if item in ("rainbow", "all"):
            return list(RAINBOW_COLORS)
        if item in COLOR_CODES:
            config_colors.append(COLOR_CODES[item])

    if config_colors:
        return list(dict.fromkeys(config_colors))

    return [COLOR_CODES["green"]]


class MatrixSimulation:
    """Manages the state and movement of falling character drops in the matrix."""

    def __init__(
        self,
        cols: int,
        rows: int,
        chars: str,
        colors: List[str],
        density: float,
        tail_len: int,
        col_stride: int = 1,
    ) -> None:
        self.cols = max(cols, 1)
        self.rows = max(rows, 1)
        self.chars = chars if chars else CHARSETS["full"]
        self.colors = colors if colors else [COLOR_CODES["green"]]
        self.density = min(max(float(density), 0.0), 1.0)
        self.tail_len = max(int(tail_len), 1)
        self.col_stride = max(int(col_stride), 1)

        self.screen: List[List[str]] = [[" "] * self.cols for _ in range(self.rows)]
        self.col_colors: List[str] = [random.choice(self.colors) for _ in range(self.cols)]
        self.drops: List[int] = [random.randint(-self.rows, 0) for _ in range(self.cols)]
        self.lengths: List[int] = [self._rand_length() for _ in range(self.cols)]

    def _rand_length(self) -> int:
        """Safely compute a random tail length based on tail_len setting."""
        min_len = max(3, self.tail_len // 2)
        max_len = max(min_len, self.tail_len + 10)
        return random.randint(min_len, max_len)

    def resize(self, new_cols: int, new_rows: int) -> None:
        """Reinitialize buffer grids upon terminal window resize."""
        self.cols = max(new_cols, 1)
        self.rows = max(new_rows, 1)
        self.screen = [[" "] * self.cols for _ in range(self.rows)]
        self.col_colors = [random.choice(self.colors) for _ in range(self.cols)]
        self.drops = [random.randint(-self.rows, 0) for _ in range(self.cols)]
        self.lengths = [self._rand_length() for _ in range(self.cols)]

    def step(self) -> None:
        """Advance the drops state by one simulation step."""
        max_col = self.cols - self.col_stride + 1
        for i in range(0, max_col, self.col_stride):
            drop_pos = self.drops[i]
            if drop_pos < 0:
                self.drops[i] += 1
            elif drop_pos == 0:
                if random.random() > self.density:
                    self.drops[i] = 1
                    self.lengths[i] = self._rand_length()
                    self.col_colors[i] = random.choice(self.colors)

            if self.drops[i] > 0:
                # Leading head position
                head_y = self.drops[i] - 1
                if 0 <= head_y < self.rows:
                    self.screen[head_y][i] = random.choice(self.chars)

                # Tail clearing position
                tail_y = self.drops[i] - self.lengths[i] - 1
                if 0 <= tail_y < self.rows:
                    self.screen[tail_y][i] = " "

                self.drops[i] += 1
                if self.drops[i] > self.rows + self.lengths[i]:
                    self.drops[i] = -random.randint(2, 15)
                    self.lengths[i] = self._rand_length()
                    self.col_colors[i] = random.choice(self.colors)


class MatrixRenderer:
    """Renders the matrix state into a buffered ANSI escape string."""

    def __init__(self, bold_head: bool) -> None:
        self.bold_head = bold_head
        self.head_bold = ANSI_BOLD_WHITE
        self.bright_cache = {c: f"\033[1;{c}m" for c in COLOR_CODES.values()}
        self.dim_cache = {c: f"\033[2;{c}m" for c in COLOR_CODES.values()}

    def render(self, sim: MatrixSimulation) -> str:
        """Build the full frame into a single string buffer."""
        buf: List[str] = [ANSI_CURSOR_HOME]
        rows = sim.rows
        cols = sim.cols
        screen = sim.screen
        drops = sim.drops
        col_colors = sim.col_colors
        col_stride = sim.col_stride
        bold_head = self.bold_head
        head_bold = self.head_bold
        bright_cache = self.bright_cache
        dim_cache = self.dim_cache
        reset = ANSI_RESET

        for y in range(rows):
            x = 0
            while x < cols:
                ch = screen[y][x]
                if ch != " ":
                    if x + col_stride <= cols:
                        c = col_colors[x]
                        drop_pos = drops[x]
                        # After step(), drops[x] has been incremented past head_y:
                        # head_y == drop_pos - 2, and lead_y == drop_pos - 3
                        head_y = drop_pos - 2
                        lead_y = drop_pos - 3
                        if y == head_y:
                            if bold_head:
                                buf.extend((head_bold, ch, reset))
                            else:
                                buf.extend((bright_cache.get(c, f"\033[1;{c}m"), ch, reset))
                        elif y == lead_y:
                            buf.extend((bright_cache.get(c, f"\033[1;{c}m"), ch, reset))
                        else:
                            buf.extend((dim_cache.get(c, f"\033[2;{c}m"), ch, reset))
                        x += col_stride
                    else:
                        buf.append(" ")
                        x += 1
                else:
                    buf.append(" ")
                    x += 1
            if y < rows - 1:
                buf.append("\n")

        return "".join(buf)


def main() -> None:
    args = sys.argv[1:]

    # Handle version flag
    if any(arg in ("-v", "--version") for arg in args):
        print(f"mewmatrix {__version__}")
        return

    # Handle self-update command
    if any(arg in ("--update", "update") for arg in args):
        force_update = "--force" in args
        update_mewmatrix(force=force_update)
        return

    # Handle help flag
    if any(arg in ("-h", "--help") for arg in args):
        print_help()
        return

    # Handle config initialization flag
    if "--init" in args:
        init_config()
        return

    cfg = load_config()

    # Non-blocking check for available update
    available_update: Optional[str] = None
    if cfg.get("check_updates", True):
        try:
            available_update = check_for_updates_background()
        except Exception:
            available_update = None

    meow_mode = "meow" in args

    try:
        speed = float(cfg.get("speed", 0.05))
        if speed <= 0:
            speed = 0.05
    except (ValueError, TypeError):
        speed = 0.05

    try:
        density = float(cfg.get("density", 0.78))
        density = min(max(density, 0.0), 1.0)
    except (ValueError, TypeError):
        density = 0.78

    try:
        tail_len = int(cfg.get("tail_length", 15))
        if tail_len < 1:
            tail_len = 15
    except (ValueError, TypeError):
        tail_len = 15

    bold_head = bool(cfg.get("bold_head", True))
    charset_name = str(cfg.get("charset", "full")).strip()

    selected_colors = resolve_colors(args, cfg.get("color", "green"))

    if meow_mode:
        chars = CAT_EMOJIS
        col_stride = 2  # Emojis occupy 2 visual columns
    else:
        if charset_name in CHARSETS:
            chars = CHARSETS[charset_name]
        elif charset_name:
            chars = charset_name
        else:
            chars = CHARSETS["full"]
        col_stride = 1

    cols, rows = get_terminal_dimensions()

    sim = MatrixSimulation(
        cols=cols,
        rows=rows,
        chars=chars,
        colors=selected_colors,
        density=density,
        tail_len=tail_len,
        col_stride=col_stride,
    )
    renderer = MatrixRenderer(bold_head=bold_head)

    # Handle dynamic terminal resizing
    terminal_resized = False

    def handle_sigwinch(signum, frame):
        nonlocal terminal_resized
        terminal_resized = True

    if hasattr(signal, "SIGWINCH"):
        try:
            signal.signal(signal.SIGWINCH, handle_sigwinch)
        except (ValueError, OSError):
            pass

    # Ensure clean exit on termination signals
    def handle_exit_signal(signum, frame):
        sys.exit(0)

    for sig_name in ("SIGTERM", "SIGHUP"):
        if hasattr(signal, sig_name):
            try:
                signal.signal(getattr(signal, sig_name), handle_exit_signal)
            except (ValueError, OSError):
                pass

    # Initial terminal setup: clear screen, disable autowrap, and hide cursor
    try:
        sys.stdout.write(ANSI_CLEAR_SCREEN + ANSI_DISABLE_AUTOWRAP + ANSI_HIDE_CURSOR)
        sys.stdout.flush()
    except (OSError, ValueError):
        pass

    try:
        while True:
            new_cols, new_rows = get_terminal_dimensions()
            if terminal_resized or new_cols != sim.cols or new_rows != sim.rows:
                terminal_resized = False
                if new_cols != sim.cols or new_rows != sim.rows:
                    sim.resize(new_cols, new_rows)
                    sys.stdout.write(ANSI_CLEAR_SCREEN)

            sim.step()
            frame = renderer.render(sim)
            sys.stdout.write(frame)
            sys.stdout.flush()
            time.sleep(speed)
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal()
        try:
            sys.stdout.write(ANSI_CLEAR_SCREEN + ANSI_CURSOR_HOME)
            sys.stdout.flush()
            print("meow!")
            if available_update:
                print(f"💡 A new version of MewMatrix is available: v{available_update} (current: v{__version__})")
                print("   Run 'mewmatrix --update' to upgrade!")
        except (OSError, ValueError):
            pass


if __name__ == "__main__":
    main()

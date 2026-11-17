# 🐱 MewMatrix

> A lightweight, zero-dependency `cmatrix` alternative written in pure Python, featuring multi-color mixing, cat mode, dynamic terminal resizing, and customizable rain effects.

<p align="center">
  <img src="https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/preview.gif" alt="MewMatrix Demo" width="650">
</p>

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

---

## ✨ Features

- **Global Command**: Run `mewmatrix` anywhere in your terminal.
- **Zero Dependencies**: Pure Python standard library — works out of the box without installing heavy packages.
- **Self-Updating**: Update to the latest version anytime with `mewmatrix --update` — no version conflicts or cache bugs.
- **Multi-Color Mixing**: Mix any combination of colors simultaneously (e.g. `mewmatrix red white blue`).
- **Rainbow Mode**: Cycles drops across a vibrant 7-color palette (`mewmatrix rainbow`).
- **Cat Mode (`meow`)**: Replaces falling characters with cat emojis (🐱😺😸😻😽😼🙀😿😾) with automatic 2-column spacing.
- **Cat-Themed Color Aliases**: Fun aliases for standard ANSI colors (`nya`, `purr`, `hiss`, `mew`, `angry`, `trill`).
- **Dynamic Resizing**: Seamlessly adapts to terminal window size changes in real-time (`SIGWINCH`).
- **Configurable**: Fine-tune speed, drop density, tail lengths, bold head character, and character sets via `~/.config/mewmatrix/config.meow`.
- **Multiple Charsets**: Built-in support for Matrix Katakana + Alphanumeric (`full`), `ascii`, `hex`, or custom character strings.
- **Clean Terminal Restoration**: Gracefully restores terminal state, cursor, and autowrap on exit (`Ctrl+C`, `SIGTERM`, `SIGHUP`).

---

## 📦 Installation & Quick Start

### ⚡ One-Line Automatic Install (Recommended)

Run this single command in your terminal. It automatically downloads `mewmatrix`, configures your `$PATH`, and sets up the global `mewmatrix` and `meowmatrix` commands:

```bash
curl -sSL https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/install.sh | bash
```

Once completed, you can run `mewmatrix` directly from anywhere!

---

### 🔄 Automatic Updates (Never Run Outdated Versions!)

MewMatrix includes a built-in self-updater. To upgrade to the latest version from GitHub at any time:

```bash
mewmatrix --update
```

What `mewmatrix --update` does:
1. Checks GitHub for the latest release.
2. Downloads and validates the new code syntax.
3. Automatically replaces the executable in-place and clears any stale bytecode (`__pycache__`) so the new version is immediately active without version caching bugs.

You can also update by re-running the one-line installer:
```bash
curl -sSL https://raw.githubusercontent.com/zagadka298-design/mewmatrix/main/install.sh | bash
```

To check your currently installed version:
```bash
mewmatrix --version
```

---

### 🛠️ Alternative Installation Methods

<details>
<summary><b>Method 2: Install via pip</b></summary>

```bash
# Install directly from GitHub
pip install git+https://github.com/zagadka298-design/mewmatrix.git

# Or install from a local clone
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
pip install .
```
</details>

<details>
<summary><b>Method 3: System-wide Standalone Binary</b></summary>

```bash
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
sudo cp mewmatrix.py /usr/local/bin/mewmatrix
sudo chmod +x /usr/local/bin/mewmatrix
```
</details>

<details>
<summary><b>Method 4: Run Directly with Python (No installation)</b></summary>

```bash
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
python3 mewmatrix.py
```
</details>

---

## 🚀 Usage

### Basic Commands

```bash
# Launch default matrix rain (green)
mewmatrix

# Launch with multiple colors mixed
mewmatrix cyan white blue

# Launch rainbow mode
mewmatrix rainbow

# Launch cat emoji rain
mewmatrix meow

# Combine cat mode with rainbow colors
mewmatrix meow rainbow

# Use cat-themed color aliases
mewmatrix nya purr
```

### Command-Line Arguments & Options

| Argument / Option | Description |
| :--- | :--- |
| `meow` | Enable Cat Mode (drops random cat emojis) |
| `rainbow`, `all` | Cycle through all rainbow colors |
| `--update` | Automatically check and update to the latest version |
| `--version`, `-v` | Show currently installed version |
| `--init` | Generate a default configuration file at `~/.config/mewmatrix/config.meow` |
| `-h`, `--help` | Show command usage and help message |

### Supported Colors & Aliases

| Standard Color Name | Cat-Themed Alias | Preview / Description |
| :--- | :--- | :--- |
| `green` | `purr` | Classic Matrix Green |
| `red` | `hiss` | Bright Red |
| `cyan` | `nya` | Bright Cyan |
| `magenta` | `mew` | Pink / Magenta |
| `yellow` | `angry` | Bright Yellow |
| `blue` | `trill` | Deep Blue |
| `white` | — | Bright White |

*(You can combine as many colors as you want: `mewmatrix red purr nya white`)*

---

## ⚙️ Configuration

You can customize MewMatrix permanently using a configuration file.

Generate the default configuration file:

```bash
mewmatrix --init
```

This creates `~/.config/mewmatrix/config.meow` (JSON format):

```json
{
  "color": "green",
  "speed": 0.05,
  "density": 0.78,
  "charset": "full",
  "tail_length": 15,
  "bold_head": true,
  "check_updates": true
}
```

### Configuration Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `color` | string / array | `"green"` | Default color, list of colors, or `"rainbow"`. E.g. `["cyan", "white"]` |
| `speed` | float | `0.05` | Frame delay in seconds (lower is faster) |
| `density` | float | `0.78` | Density of drops between `0.0` (sparse) and `1.0` (dense) |
| `charset` | string | `"full"` | Character set: `"full"` (matrix katakana + alphanumeric), `"ascii"`, `"hex"`, or any custom string |
| `tail_length` | integer | `15` | Average length of the raindrop trail |
| `bold_head` | boolean | `true` | When `true`, the leading character of each drop is rendered in bold white |
| `check_updates`| boolean | `true` | When `true`, automatically checks for new versions in the background (once per day) |

---

## 🧪 Running Tests

To run the unit test suite:

```bash
python3 -m unittest test_mewmatrix.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

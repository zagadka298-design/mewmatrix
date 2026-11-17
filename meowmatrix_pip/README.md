# 🐱 MewMatrix

> A lightweight, zero-dependency `cmatrix` alternative written in pure Python, featuring multi-color mixing, cat mode, dynamic terminal resizing, and customizable rain effects.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

---

## ✨ Features

- **Zero Dependencies**: Pure Python standard library — works out of the box without installing heavy packages.
- **Multi-Color Mixing**: Mix any combination of colors simultaneously (e.g. `mewmatrix red white blue`).
- **Rainbow Mode**: Cycles drops across a vibrant 7-color palette.
- **Cat Mode (`meow`)**: Replaces falling characters with cat emojis (🐱😺😸😻😽😼🙀😿😾) with automatic 2-column spacing.
- **Cat-Themed Color Aliases**: Fun aliases for standard ANSI colors (`nya`, `purr`, `hiss`, `mew`, `angry`, `trill`).
- **Dynamic Resizing**: Seamlessly adapts to terminal window size changes in real-time (`SIGWINCH`).
- **Configurable**: Fine-tune speed, drop density, tail lengths, bold head character, and character sets via `~/.config/mewmatrix/config.meow`.
- **Multiple Charsets**: Built-in support for Matrix Katakana + Alphanumeric (`full`), `ascii`, `hex`, or custom character strings.
- **Clean Terminal Restoration**: Gracefully restores terminal state, cursor, and autowrap on exit (`Ctrl+C`, `SIGTERM`, `SIGHUP`).

---

## 📦 Installation

### Method 1: Install from Source (Recommended)

Clone the repository and install it using `pip`:

```bash
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
pip install .
```

Now you can run `mewmatrix` from anywhere in your terminal.

### Method 2: Standalone Executable (No pip install needed)

You can copy the standalone script directly to your local binaries folder:

```bash
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
sudo cp mewmatrix.py /usr/local/bin/mewmatrix
sudo chmod +x /usr/local/bin/mewmatrix
```

### Method 3: Run Directly with Python

No installation required at all:

```bash
git clone https://github.com/zagadka298-design/mewmatrix.git
cd mewmatrix
python3 mewmatrix.py
```

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
  "bold_head": true
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

---

## 🧪 Running Tests

To run the unit test suite:

```bash
python3 -m unittest test_mewmatrix.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# Themes & Fonts — Time Warp II Customisation Guide

Detailed guide to personalising the Time Warp II IDE appearance.

---

## Colour Themes

### Switching Themes

Three ways to change your theme:

1. **Preferences → Color Theme** — pick from the submenu
2. **Command Palette** (Ctrl+Shift+P) — type "Theme:" and select
3. **Toolbar 🎨 button** — cycles to the next theme

The theme change takes effect instantly and is saved for next time.

### Available Themes

#### Light
Clean white background with dark text. Best for well-lit environments.

| Element | Colour |
|---------|--------|
| Editor background | white |
| Editor text | black |
| Canvas background | white |
| Status bar | #e0e0e0 (light grey) |
| Error text | #cc0000 (red) |

#### Dark
VS Code-inspired dark theme. The default theme.

| Element | Colour |
|---------|--------|
| Editor background | #1e1e1e (charcoal) |
| Editor text | #d4d4d4 (light grey) |
| Canvas background | #2d2d2d |
| Status bar | #007acc (blue) |
| Error text | #f44747 (bright red) |

#### Classic
Traditional white/cream look reminiscent of older IDEs.

| Element | Colour |
|---------|--------|
| Editor background | white |
| Editor text | black |
| Canvas background | #fffef0 (cream) |
| Status bar | #c0c0c0 (silver) |

#### Solarized Dark
Warm dark palette designed by Ethan Schoonover for readability.

| Element | Colour |
|---------|--------|
| Editor background | #002b36 (dark teal) |
| Editor text | #839496 (grey-blue) |
| Status bar | #073642 |

#### Solarized Light
Warm light palette, the companion to Solarized Dark.

| Element | Colour |
|---------|--------|
| Editor background | #fdf6e3 (warm cream) |
| Editor text | #657b83 (grey-green) |
| Status bar | #eee8d5 |

#### Monokai
Popular high-contrast dark theme.

| Element | Colour |
|---------|--------|
| Editor background | #272822 (dark olive) |
| Editor text | #f8f8f2 (near white) |
| Errors | #f92672 (hot pink) |
| Success | #a6e22e (lime green) |

#### Dracula
Modern dark theme with purple accents.

| Element | Colour |
|---------|--------|
| Editor background | #282a36 (dark blue-grey) |
| Editor text | #f8f8f2 (near white) |
| Borders | #6272a4 (muted blue) |
| Errors | #ff5555 (red) |
| Success | #50fa7b (green) |

#### Nord
Cool blue-grey palette inspired by the Arctic.

| Element | Colour |
|---------|--------|
| Editor background | #2e3440 (dark blue-grey) |
| Editor text | #d8dee9 (light grey) |
| Errors | #bf616a (muted red) |
| Success | #a3be8c (sage green) |

#### High Contrast
Maximum readability with pure black background and bright text.

| Element | Colour |
|---------|--------|
| Editor background | black |
| Editor text | white |
| Status bar text | #ffff00 (yellow) |
| Errors | #ff4444 (bright red) |
| Success | #44ff44 (bright green) |

**Recommended for:** users with low vision, projectors in bright rooms.

### Auto Dark/Light Mode

**Preferences → Auto Dark/Light (follow OS)** — when enabled, Time Warp II detects your operating system's dark or light mode setting and applies a matching theme automatically. This is enabled by default.

---

## Font Size

### Changing Font Size

Four ways to adjust font size:

1. **Preferences → Font Size** — pick a named size
2. **Command Palette** (Ctrl+Shift+P) — type "Font Size:"
3. **Toolbar Aa button** — cycles to the next size
4. **Ctrl+Scroll** / **Ctrl+Plus** / **Ctrl+Minus** — zoom in/out

### Available Sizes

| Name | Editor | Output | Best For |
|------|--------|--------|----------|
| Tiny | 8pt | 8pt | Maximum visible code |
| Small | 10pt | 9pt | Compact view |
| **Medium** | **12pt** | **11pt** | **Default — everyday use** |
| Large | 14pt | 13pt | Comfortable reading |
| Extra Large | 16pt | 15pt | Presentations, projection |
| Huge | 18pt | 17pt | Large monitors, demos |
| Giant | 22pt | 20pt | Maximum readability |

All sizes are saved between sessions.

---

## Font Family

### Changing Font Family

**Preferences → Font Family** lists all monospace fonts installed on your system.

Font families are organised into two groups:

1. **Priority fonts** — popular programming fonts listed first
2. **More Fonts** — all other monospace fonts in a submenu

### Priority Fonts

These fonts are prioritised in the menu (availability depends on your system):

| Font | Platform |
|------|----------|
| Courier | All |
| Courier New | All |
| Consolas | Windows |
| Monaco | macOS |
| Menlo | macOS |
| DejaVu Sans Mono | Linux |
| Liberation Mono | Linux |
| Ubuntu Mono | Ubuntu |
| Fira Code | Cross-platform (install separately) |
| Source Code Pro | Cross-platform (install separately) |
| JetBrains Mono | Cross-platform (install separately) |
| Cascadia Code | Windows 11 / install separately |
| SF Mono | macOS |
| Inconsolata | Cross-platform (install separately) |
| Roboto Mono | Cross-platform (install separately) |
| Hack | Cross-platform (install separately) |
| Anonymous Pro | Cross-platform (install separately) |
| Droid Sans Mono | Android / install separately |
| PT Mono | Cross-platform (install separately) |

### Installing Fonts

To add a new font:

1. Download the font from its official source
2. Install it using your operating system's font manager
3. Restart Time Warp II
4. The new font appears in **Preferences → Font Family**

Fonts with ligature support (Fira Code, JetBrains Mono, Cascadia Code) are fully supported.

---

## Settings File

All appearance settings are stored in `~/.templecode_settings.json`:

```json
{
  "theme": "dark",
  "font_size": "medium",
  "font_family": "Courier",
  "auto_dark": true
}
```

To reset appearance to defaults, delete this file and restart the IDE.

---

## Recommendations

### For Students
- **Theme:** Dark or Dracula — easy on the eyes for extended coding
- **Font size:** Medium or Large
- **Font:** System default (Courier) or DejaVu Sans Mono

### For Presentations
- **Theme:** High Contrast or Light — visible in well-lit rooms
- **Font size:** Huge or Giant
- **Font:** Consolas or JetBrains Mono for clean readability

### For Accessibility
- **Theme:** High Contrast — maximum contrast ratio
- **Font size:** Extra Large, Huge, or Giant
- **Auto Dark/Light:** Enable to match OS settings

---

*Time Warp II — Themes & Fonts Guide*
*Copyright © 2025 Honey Badger Universe*

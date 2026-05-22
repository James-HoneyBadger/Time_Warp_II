"""Turtle graphics canvas panel for Time Warp II."""
from __future__ import annotations

import os
import tempfile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


class GraphicsPanel:
    """Canvas panel for Logo turtle graphics with PNG/SVG export."""

    def __init__(self, app: TempleCodeApp, parent) -> None:
        tk = app.tk
        self.app = app

        self.frame = tk.LabelFrame(
            parent, text="Turtle Graphics", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )

        self.canvas = tk.Canvas(
            self.frame, width=600, height=400,
            bg="#2d2d2d", highlightthickness=1, highlightbackground="#3e3e3e",
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_resize)

    # ------------------------------------------------------------------
    #  Canvas helpers
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Clear the canvas and reset turtle state."""
        self.canvas.delete("all")
        interp = self.app.interpreter
        if hasattr(interp, 'turtle_graphics') and interp.turtle_graphics:
            tg = interp.turtle_graphics
            tg["x"] = 0.0
            tg["y"] = 0.0
            tg["heading"] = 0.0
            tg["lines"] = []
            interp.update_turtle_display()
        self.app._output("🎨 Canvas cleared\n")

    def export_png(self) -> None:
        """Export the canvas to a PNG file."""
        filename = self.app.filedialog.asksaveasfilename(
            title="Export Canvas as PNG", defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
        )
        if not filename:
            return
        ps_file = filename + ".ps"
        try:
            from PIL import Image
            self.canvas.postscript(file=ps_file, colormode="color")
            img = Image.open(ps_file)
            img.save(filename, "PNG")
            self.app._output(f"📸 Canvas exported to {filename}\n", "out_ok")
        except ImportError:
            ps_name = filename.replace(".png", ".ps")
            self.canvas.postscript(file=ps_name, colormode="color")
            self.app._output(
                f"📸 Canvas exported as PostScript to {ps_name}\n(Install Pillow for PNG)\n",
                "out_warn",
            )
        except Exception as e:
            self.app._output(f"❌ Export failed: {e}\n", "out_error")
        finally:
            # Always remove the temporary PostScript file if it was created.
            if os.path.exists(ps_file):
                try:
                    os.remove(ps_file)
                except OSError:
                    pass

    def copy_to_clipboard(self) -> None:
        """Copy the canvas contents to the system clipboard as a PNG image."""
        ps_file = None
        png_file = None
        try:
            from PIL import Image
            fd, ps_file = tempfile.mkstemp(suffix=".ps")
            os.close(fd)
            fd2, png_file = tempfile.mkstemp(suffix=".png")
            os.close(fd2)
            self.canvas.postscript(file=ps_file, colormode="color")
            img = Image.open(ps_file)
            img.save(png_file, "PNG")
            # Try xclip (X11) then xdotool, fall back to saving to temp location
            import subprocess
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-t", "image/png", "-i", png_file],
                capture_output=True, timeout=5,
            )
            if result.returncode == 0:
                self.app._output("📋 Canvas copied to clipboard.\n", "out_ok")
            else:
                # Try wl-copy (Wayland)
                result2 = subprocess.run(
                    ["wl-copy", "--type", "image/png"],
                    input=open(png_file, "rb").read(),
                    capture_output=True, timeout=5,
                )
                if result2.returncode == 0:
                    self.app._output("📋 Canvas copied to clipboard.\n", "out_ok")
                else:
                    self.app._output(
                        f"⚠ Clipboard copy requires xclip or wl-copy.\n"
                        f"  PNG saved to: {png_file}\n", "out_warn")
                    png_file = None  # don't delete — user may want it
        except ImportError:
            self.app._output(
                "⚠ Canvas clipboard copy requires Pillow (pip install Pillow).\n", "out_warn")
        except Exception as e:
            self.app._output(f"❌ Clipboard copy failed: {e}\n", "out_error")
        finally:
            for f in (ps_file, png_file):
                if f and os.path.exists(f):
                    try:
                        os.remove(f)
                    except OSError:
                        pass

    def export_svg(self) -> None:
        """Export the canvas to a crude SVG file."""
        filename = self.app.filedialog.asksaveasfilename(
            title="Export Canvas as SVG", defaultextension=".svg",
            filetypes=[("SVG Image", "*.svg"), ("All Files", "*.*")],
        )
        if not filename:
            return
        try:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            items = self.canvas.find_all()
            svg_lines = [
                f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                f'viewBox="0 0 {w} {h}">',
                f'<rect width="{w}" height="{h}" fill="{self.canvas.cget("bg")}"/>',
            ]

            def _color(raw: str, fallback: str = "none") -> str:
                """Return *raw* if non-empty, else *fallback*."""
                return raw.strip() if raw and raw.strip() else fallback

            def _flip_y(y: float) -> float:
                """Flip a tkinter Y coordinate to SVG coordinate space."""
                return h - y

            for item in items:
                itype = self.canvas.type(item)
                coords = self.canvas.coords(item)
                fill = _color(self.canvas.itemcget(item, "fill"))
                outline = _color(self.canvas.itemcget(item, "outline"))
                width = self.canvas.itemcget(item, "width") or "1"
                if itype == "line" and len(coords) >= 4:
                    svg_lines.append(
                        f'<line x1="{coords[0]}" y1="{_flip_y(coords[1])}" '
                        f'x2="{coords[2]}" y2="{_flip_y(coords[3])}" '
                        f'stroke="{fill}" stroke-width="{width}"/>'
                    )
                elif itype == "oval" and len(coords) >= 4:
                    cx = (coords[0] + coords[2]) / 2
                    cy = _flip_y((coords[1] + coords[3]) / 2)
                    rx = abs(coords[2] - coords[0]) / 2
                    ry = abs(coords[3] - coords[1]) / 2
                    svg_lines.append(
                        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                        f'fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
                    )
                elif itype == "rectangle" and len(coords) >= 4:
                    svg_lines.append(
                        f'<rect x="{coords[0]}" y="{_flip_y(coords[3])}" '
                        f'width="{coords[2]-coords[0]}" height="{coords[3]-coords[1]}" '
                        f'fill="{fill}" stroke="{outline}" stroke-width="{width}"/>'
                    )
            svg_lines.append("</svg>")
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(svg_lines))
            self.app._output(f"📸 Canvas exported to {filename}\n", "out_ok")
        except Exception as e:
            self.app._output(f"❌ SVG export failed: {e}\n", "out_error")

    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to the graphics area."""
        self.canvas.config(
            bg=theme["canvas_bg"], highlightbackground=theme["canvas_border"],
        )
        self.frame.config(bg=theme["editor_frame_bg"], fg=theme["editor_frame_fg"])

    def _on_resize(self, event) -> None:
        """Keep the turtle centre in sync when the canvas is resized."""
        interp = self.app.interpreter
        if (interp
                and hasattr(interp, 'turtle_graphics')
                and interp.turtle_graphics):
            interp.turtle_graphics["center_x"] = event.width // 2
            interp.turtle_graphics["center_y"] = event.height // 2

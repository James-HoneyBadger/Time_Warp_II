"""Status bar panel for Time Warp II."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


class StatusBar:
    """Bottom status bar showing cursor position, theme, and file info."""

    def __init__(self, app: TempleCodeApp) -> None:
        tk = app.tk
        self.app = app
        self._after_id = None

        self.frame = tk.Frame(app.root, bg="#007acc", height=22)
        self.frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.frame.pack_propagate(False)

        font = ("Arial", 9)
        self.labels: dict[str, object] = {}

        self.labels["file"] = tk.Label(
            self.frame, text="  No file  ", bg="#007acc", fg="white",
            font=font, anchor="w",
        )
        self.labels["file"].pack(side=tk.LEFT, padx=(5, 20))

        self.labels["cursor"] = tk.Label(
            self.frame, text="Ln 1, Col 1", bg="#007acc", fg="white",
            font=font, anchor="w",
        )
        self.labels["cursor"].pack(side=tk.LEFT, padx=(0, 20))

        from core.config import THEMES, FONT_SIZES
        self.labels["theme"] = tk.Label(
            self.frame, text=THEMES[app.current_theme]["name"],
            bg="#007acc", fg="white", font=font, anchor="e",
        )
        self.labels["theme"].pack(side=tk.RIGHT, padx=(0, 10))

        self.labels["font"] = tk.Label(
            self.frame,
            text=f"{app.current_font_family} {FONT_SIZES[app.current_font]['editor']}pt",
            bg="#007acc", fg="white", font=font, anchor="e",
        )
        self.labels["font"].pack(side=tk.RIGHT, padx=(0, 15))

    # ------------------------------------------------------------------

    def start_updates(self) -> None:
        """Begin the recurring cursor-position updater."""
        self._update()

    def cancel_updates(self) -> None:
        """Cancel the recurring updater (call before destroying the window)."""
        if self._after_id is not None:
            self.app.root.after_cancel(self._after_id)
            self._after_id = None

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to the status bar."""
        bg = theme.get("statusbar_bg", "#007acc")
        fg = theme.get("statusbar_fg", "#ffffff")
        self.frame.config(bg=bg)
        for lbl in self.labels.values():
            lbl.config(bg=bg, fg=fg)

    # ------------------------------------------------------------------

    def _update(self) -> None:
        """Periodically refresh the cursor position label."""
        try:
            widget = self.app.editor_text
            idx = widget.index(self.app.tk.INSERT) if hasattr(widget, 'index') else "1.0"
            line, col = idx.split(".")
            self.labels["cursor"].config(text=f"Ln {line}, Col {int(col)+1}")
        except Exception:
            pass
        self._after_id = self.app.root.after(250, self._update)

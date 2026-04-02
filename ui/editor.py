"""Editor panel for Time Warp II."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


class EditorPanel:
    """Code editor area with optional syntax highlighting and split view."""

    def __init__(self, app: TempleCodeApp, parent, *, pygments_ok: bool) -> None:
        tk = app.tk
        self.app = app

        from core.features.syntax_highlighting import SyntaxHighlightingText, LineNumberedText
        self._SyntaxHighlightingText = SyntaxHighlightingText
        self._LineNumberedText = LineNumberedText

        # Paned window for split editor
        self.paned = tk.PanedWindow(parent, orient=tk.VERTICAL, sashwidth=5, bg="#252526")
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Primary editor
        self.frame = tk.LabelFrame(
            self.paned, text="TempleCode Editor", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        self.paned.add(self.frame)

        if pygments_ok:
            self.text_widget = SyntaxHighlightingText(
                self.frame, language="templecode", theme="dark",
                bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        else:
            self.text_widget = LineNumberedText(
                self.frame, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        self.text_widget.pack(fill=tk.BOTH, expand=True)

        # Secondary editor (hidden until split-toggle)
        self.frame2 = tk.LabelFrame(
            self.paned, text="Editor 2", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )
        if pygments_ok:
            self.text_widget2 = SyntaxHighlightingText(
                self.frame2, language="templecode", theme="dark",
                bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        else:
            self.text_widget2 = LineNumberedText(
                self.frame2, bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            )
        self.text_widget2.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    #  Split editor
    # ------------------------------------------------------------------

    def toggle_split(self, split_var) -> None:
        """Show or hide the secondary editor pane."""
        if self.frame2 in self.paned.panes():
            self.paned.forget(self.frame2)
            split_var.set(False)
        else:
            self.paned.add(self.frame2)
            split_var.set(True)
            self._apply_theme_to_widget(self.text_widget2)

    # ------------------------------------------------------------------
    #  Theme / font
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict, theme_key: str) -> None:
        """Apply theme colours to both editor widgets."""
        from core.config import LINE_NUMBER_BG
        for editor in (self.text_widget, self.text_widget2):
            if editor is None:
                continue
            if hasattr(editor, 'text'):
                editor.text.config(
                    bg=theme["text_bg"], fg=theme["text_fg"],
                    insertbackground=theme["text_fg"],
                )
                if hasattr(editor, 'set_theme'):
                    editor.set_theme(theme_key)
                if hasattr(editor, 'line_numbers'):
                    editor.line_numbers.config(
                        bg=LINE_NUMBER_BG.get(theme_key, "#1e1e1e"),
                    )
            else:
                editor.config(
                    bg=theme["text_bg"], fg=theme["text_fg"],
                    insertbackground=theme["text_fg"],
                )
        for frame in (self.frame, self.frame2):
            if frame:
                frame.config(bg=theme["editor_frame_bg"], fg=theme["editor_frame_fg"])

    def apply_font(self, family: str, size: int) -> None:
        """Apply font family and size to both editor widgets."""
        for editor in (self.text_widget, self.text_widget2):
            if editor is None:
                continue
            if hasattr(editor, 'set_font'):
                editor.set_font((family, size))
            else:
                editor.config(font=(family, size))

    def _apply_theme_to_widget(self, editor) -> None:
        """Apply the current theme to a single editor widget."""
        from core.config import THEMES
        theme = THEMES[self.app.current_theme]
        if hasattr(editor, 'text'):
            editor.text.config(bg=theme["text_bg"], fg=theme["text_fg"],
                               insertbackground=theme["text_fg"])
            if hasattr(editor, 'set_theme'):
                editor.set_theme(self.app.current_theme)
        else:
            editor.config(bg=theme["text_bg"], fg=theme["text_fg"],
                          insertbackground=theme["text_fg"])
        from core.config import FONT_SIZES
        sz = FONT_SIZES[self.app.current_font]
        if hasattr(editor, 'set_font'):
            editor.set_font((self.app.current_font_family, sz["editor"]))
        else:
            editor.config(font=(self.app.current_font_family, sz["editor"]))

    # ------------------------------------------------------------------
    #  Current-line highlighting
    # ------------------------------------------------------------------

    def highlight_current_line(self) -> None:
        """Highlight the line containing the cursor."""
        from core.config import THEMES
        text_w = self.inner_text
        tk = self.app.tk
        text_w.tag_remove("current_line", "1.0", tk.END)
        current = text_w.index(tk.INSERT)
        line = current.split(".")[0]
        text_w.tag_add("current_line", f"{line}.0", f"{line}.end+1c")
        theme = THEMES.get(self.app.current_theme, THEMES["dark"])
        text_w.tag_configure("current_line", background=theme.get("highlight_line", "#2a2d2e"))
        text_w.tag_lower("current_line")

    # ------------------------------------------------------------------
    #  Code folding
    # ------------------------------------------------------------------

    def fold_all(self) -> None:
        """Hide lines between matching block openers and closers."""
        text_w = self.inner_text
        tk = self.app.tk
        content = text_w.get("1.0", tk.END)
        lines = content.split("\n")
        _OPENERS = {"FOR", "WHILE", "IF", "DO", "SELECT", "REPEAT"}
        _CLOSERS = {"NEXT", "WEND", "ENDIF", "LOOP", "END SELECT"}
        stack: list[int] = []
        regions: list[tuple[int, int]] = []
        for i, line in enumerate(lines):
            word = line.strip().split()[0].upper() if line.strip() else ""
            if word in _OPENERS:
                stack.append(i)
            elif word in _CLOSERS or line.strip().upper() in _CLOSERS:
                if stack:
                    start = stack.pop()
                    if i - start > 1:
                        regions.append((start + 1, i - 1))
        for start, end in reversed(regions):
            tag = f"fold_{start}_{end}"
            text_w.tag_add(tag, f"{start + 1}.0", f"{end + 1}.end+1c")
            text_w.tag_configure(tag, elide=True)

    def unfold_all(self) -> None:
        """Remove all code-folding tags."""
        text_w = self.inner_text
        for tag in list(text_w.tag_names()):
            if tag.startswith("fold_"):
                text_w.tag_delete(tag)

    # ------------------------------------------------------------------
    #  Convenience
    # ------------------------------------------------------------------

    @property
    def inner_text(self):
        """Return the underlying tk.Text widget."""
        w = self.text_widget
        return w.text if hasattr(w, 'text') else w

    # Proxy common tk.Text methods so callers don't need to know about
    # the SyntaxHighlightingText wrapper.

    def get(self, *args, **kw):
        return self.text_widget.get(*args, **kw)

    def delete(self, *args, **kw):
        return self.text_widget.delete(*args, **kw)

    def insert(self, *args, **kw):
        return self.text_widget.insert(*args, **kw)

    def index(self, *args, **kw):
        return self.text_widget.index(*args, **kw)

    def mark_set(self, *args, **kw):
        return self.text_widget.mark_set(*args, **kw)

    def see(self, *args, **kw):
        return self.text_widget.see(*args, **kw)

    def edit_undo(self):
        return self.text_widget.edit_undo()

    def edit_redo(self):
        return self.text_widget.edit_redo()

    def tag_add(self, *args, **kw):
        return self.text_widget.tag_add(*args, **kw)

    def tag_remove(self, *args, **kw):
        return self.text_widget.tag_remove(*args, **kw)

    def event_generate(self, *args, **kw):
        return self.text_widget.event_generate(*args, **kw)

    # Search / replace proxied for Find / Replace dialogs
    def clear_search_highlights(self):
        if hasattr(self.text_widget, 'clear_search_highlights'):
            self.text_widget.clear_search_highlights()

    def find_text(self, *args, **kw):
        if hasattr(self.text_widget, 'find_text'):
            return self.text_widget.find_text(*args, **kw)
        return None

    def highlight_search_results(self, *args, **kw):
        if hasattr(self.text_widget, 'highlight_search_results'):
            self.text_widget.highlight_search_results(*args, **kw)

    def replace_text(self, *args, **kw):
        if hasattr(self.text_widget, 'replace_text'):
            return self.text_widget.replace_text(*args, **kw)
        return None

    def replace_all(self, *args, **kw):
        if hasattr(self.text_widget, 'replace_all'):
            return self.text_widget.replace_all(*args, **kw)
        return 0

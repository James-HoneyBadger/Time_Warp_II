"""Tabbed multi-file editing for Time Warp II."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


@dataclass
class TabState:
    """Holds saved state for one editor tab."""
    file_path: str = ""
    content: str = ""
    cursor_pos: str = "1.0"
    modified: bool = False
    title: str = "Untitled"

    def display_name(self) -> str:
        name = os.path.basename(self.file_path) if self.file_path else self.title
        if self.modified:
            name += " •"
        return name


class TabManager:
    """Manages a set of editor tabs above the EditorPanel."""

    _TAB_BG = "#2d2d2d"
    _TAB_FG = "#bbbbbb"
    _TAB_ACTIVE_BG = "#1e1e1e"
    _TAB_ACTIVE_FG = "#ffffff"
    _TAB_HOVER_BG = "#383838"
    _CLOSE_FG = "#888888"
    _CLOSE_HOVER_FG = "#ffffff"

    def __init__(self, app: TempleCodeApp, parent) -> None:
        self.app = app
        tk = app.tk

        self.tabs: list[TabState] = []
        self.active_index: int = -1

        # Tab bar frame — sits above the editor
        self.bar = tk.Frame(parent, bg=self._TAB_BG, height=28)
        self.bar.pack(fill=tk.X, side=tk.TOP, before=app.editor_panel.paned)
        self.bar.pack_propagate(False)

        # Container for tab buttons (left-aligned)
        self._tab_frame = tk.Frame(self.bar, bg=self._TAB_BG)
        self._tab_frame.pack(side=tk.LEFT, fill=tk.Y)

        # "+" button to add a new tab
        self._add_btn = tk.Label(
            self.bar, text=" + ", bg=self._TAB_BG, fg=self._TAB_FG,
            font=("Courier", 11), cursor="hand2",
        )
        self._add_btn.pack(side=tk.LEFT, padx=(2, 0))
        self._add_btn.bind("<Button-1>", lambda e: self.new_tab())
        self._add_btn.bind("<Enter>", lambda e: self._add_btn.config(bg=self._TAB_HOVER_BG))
        self._add_btn.bind("<Leave>", lambda e: self._add_btn.config(bg=self._TAB_BG))

        # Widget references for each tab (label + close button)
        self._tab_widgets: list[dict[str, Any]] = []

        # Create the initial tab
        self.new_tab()

    # ------------------------------------------------------------------
    #  Public API
    # ------------------------------------------------------------------

    def new_tab(self, *, file_path: str = "", content: str = "",
                title: str = "Untitled", switch: bool = True) -> int:
        """Create a new tab and optionally switch to it.

        Returns the index of the new tab.
        """
        tab = TabState(file_path=file_path, content=content, title=title)
        self.tabs.append(tab)
        idx = len(self.tabs) - 1
        self._build_tab_widget(idx)
        if switch:
            self.switch_to(idx)
        return idx

    def close_tab(self, idx: int) -> bool:
        """Close a tab. Returns False if cancelled by the user."""
        if idx < 0 or idx >= len(self.tabs):
            return False

        tab = self.tabs[idx]
        if tab.modified:
            if not self.app.messagebox.askyesno(
                "Unsaved Changes",
                f"'{tab.display_name().rstrip(' •')}' has unsaved changes. Close anyway?",
            ):
                return False

        # If this is the active tab, save nothing — content is about to be discarded
        is_active = idx == self.active_index

        # Remove the tab
        self.tabs.pop(idx)
        self._destroy_tab_widget(idx)

        if not self.tabs:
            # Always keep at least one tab
            self.new_tab()
            return True

        # Adjust active index
        if is_active:
            new_idx = min(idx, len(self.tabs) - 1)
            self.active_index = -1  # force reload
            self.switch_to(new_idx)
        elif idx < self.active_index:
            self.active_index -= 1

        self._refresh_tab_bar()
        return True

    def switch_to(self, idx: int) -> None:
        """Save current tab state and switch to tab *idx*."""
        if idx < 0 or idx >= len(self.tabs):
            return
        if idx == self.active_index:
            return

        # Save the state of the currently active tab
        if 0 <= self.active_index < len(self.tabs):
            self._save_tab_state(self.active_index)

        self.active_index = idx

        # Restore the new tab's state into the editor
        self._restore_tab_state(idx)
        self._refresh_tab_bar()

        # Sync the app's file path and title
        tab = self.tabs[idx]
        self.app.current_file_path = tab.file_path
        self.app._dirty = tab.modified
        self.app._update_title()
        fname = os.path.basename(tab.file_path) if tab.file_path else "No file"
        if hasattr(self.app, '_status_labels') and "file" in self.app._status_labels:
            self.app._status_labels["file"].config(text=f"  {fname}  ")

    def active_tab(self) -> TabState | None:
        """Return the active TabState or None."""
        if 0 <= self.active_index < len(self.tabs):
            return self.tabs[self.active_index]
        return None

    def mark_modified(self) -> None:
        """Mark the active tab as modified."""
        tab = self.active_tab()
        if tab and not tab.modified:
            tab.modified = True
            self._refresh_tab_bar()

    def mark_saved(self, file_path: str = "") -> None:
        """Mark the active tab as saved, optionally updating its file path."""
        tab = self.active_tab()
        if tab:
            tab.modified = False
            if file_path:
                tab.file_path = file_path
                tab.title = os.path.basename(file_path)
            self._refresh_tab_bar()

    def open_in_tab(self, file_path: str, content: str) -> None:
        """Open a file in a new tab (or reuse an existing tab for that file)."""
        # Check if file is already open
        for i, tab in enumerate(self.tabs):
            if tab.file_path and os.path.abspath(tab.file_path) == os.path.abspath(file_path):
                self.switch_to(i)
                return

        # If the active tab is unmodified and empty, reuse it
        active = self.active_tab()
        if (active and not active.modified and not active.file_path
                and not active.content.strip()):
            idx = self.active_index
            active.file_path = file_path
            active.content = content
            active.title = os.path.basename(file_path)
            active.modified = False
            self._restore_tab_state(idx)
            self._refresh_tab_bar()
            self.app.current_file_path = file_path
            self.app._dirty = False
            self.app._update_title()
            return

        # Otherwise open in a new tab
        idx = self.new_tab(
            file_path=file_path, content=content,
            title=os.path.basename(file_path), switch=True,
        )

    def find_tab_by_path(self, file_path: str) -> int:
        """Return the index of a tab with the given path, or -1."""
        for i, tab in enumerate(self.tabs):
            if tab.file_path and os.path.abspath(tab.file_path) == os.path.abspath(file_path):
                return i
        return -1

    def close_others(self, keep_idx: int) -> None:
        """Close all tabs except the one at *keep_idx*."""
        # Close from the end so indices stay stable
        for i in range(len(self.tabs) - 1, -1, -1):
            if i != keep_idx:
                self.close_tab(i)

    def close_all(self) -> None:
        """Close all tabs (a new empty tab will be created)."""
        while len(self.tabs) > 1:
            idx = len(self.tabs) - 1 if self.active_index != len(self.tabs) - 1 else 0
            if not self.close_tab(idx):
                return  # user cancelled
        self.close_tab(0)

    # ------------------------------------------------------------------
    #  Internal: state save / restore
    # ------------------------------------------------------------------

    def _save_tab_state(self, idx: int) -> None:
        """Snapshot the editor content + cursor into the tab."""
        tab = self.tabs[idx]
        tk = self.app.tk
        try:
            tab.content = self.app.editor_text.get("1.0", tk.END)
            # Strip the trailing newline that tkinter always appends
            if tab.content.endswith("\n"):
                tab.content = tab.content[:-1]
            tab.cursor_pos = self.app.editor_text.index(tk.INSERT)
        except Exception:
            pass

    def _restore_tab_state(self, idx: int) -> None:
        """Load a tab's saved content + cursor into the editor."""
        tab = self.tabs[idx]
        tk = self.app.tk
        self.app.editor_text.delete("1.0", tk.END)
        if tab.content:
            self.app.editor_text.insert("1.0", tab.content)
        try:
            self.app.editor_text.mark_set(tk.INSERT, tab.cursor_pos)
            self.app.editor_text.see(tab.cursor_pos)
        except Exception:
            pass

    # ------------------------------------------------------------------
    #  Internal: tab bar widgets
    # ------------------------------------------------------------------

    def _build_tab_widget(self, idx: int) -> None:
        """Create label + close button widgets for a tab."""
        tk = self.app.tk
        tab = self.tabs[idx]

        frame = tk.Frame(self._tab_frame, bg=self._TAB_BG, padx=0, pady=0)
        frame.pack(side=tk.LEFT, padx=(0, 1))

        label = tk.Label(
            frame, text=f" {tab.display_name()} ",
            bg=self._TAB_BG, fg=self._TAB_FG,
            font=("Segoe UI", 9), cursor="hand2", pady=2,
        )
        label.pack(side=tk.LEFT)
        label.bind("<Button-1>", lambda e, i=idx: self.switch_to(i))
        label.bind("<Enter>", lambda e, lbl=label: self._on_tab_enter(lbl))
        label.bind("<Leave>", lambda e, lbl=label, i=idx: self._on_tab_leave(lbl, i))

        # Right-click context menu
        label.bind("<Button-3>", lambda e, i=idx: self._tab_context_menu(e, i))

        close_btn = tk.Label(
            frame, text="×", bg=self._TAB_BG, fg=self._CLOSE_FG,
            font=("Segoe UI", 9), cursor="hand2", pady=2,
        )
        close_btn.pack(side=tk.LEFT)
        close_btn.bind("<Button-1>", lambda e, i=idx: self.close_tab(i))
        close_btn.bind("<Enter>", lambda e, c=close_btn: c.config(fg=self._CLOSE_HOVER_FG))
        close_btn.bind("<Leave>", lambda e, c=close_btn: c.config(fg=self._CLOSE_FG))

        self._tab_widgets.insert(idx, {"frame": frame, "label": label, "close": close_btn})

    def _destroy_tab_widget(self, idx: int) -> None:
        """Remove the widgets for a tab."""
        if idx < len(self._tab_widgets):
            w = self._tab_widgets.pop(idx)
            w["frame"].destroy()

    def _refresh_tab_bar(self) -> None:
        """Update the visual state of all tab widgets."""
        for i, w in enumerate(self._tab_widgets):
            if i >= len(self.tabs):
                break
            tab = self.tabs[i]
            is_active = i == self.active_index
            bg = self._TAB_ACTIVE_BG if is_active else self._TAB_BG
            fg = self._TAB_ACTIVE_FG if is_active else self._TAB_FG
            w["frame"].config(bg=bg)
            w["label"].config(text=f" {tab.display_name()} ", bg=bg, fg=fg)
            w["close"].config(bg=bg)
            # Rebind with correct index (indices shift after close/reorder)
            w["label"].bind("<Button-1>", lambda e, idx=i: self.switch_to(idx))
            w["label"].bind("<Button-3>", lambda e, idx=i: self._tab_context_menu(e, idx))
            w["close"].bind("<Button-1>", lambda e, idx=i: self.close_tab(idx))

    def _on_tab_enter(self, label) -> None:
        if label.cget("bg") != self._TAB_ACTIVE_BG:
            label.config(bg=self._TAB_HOVER_BG)

    def _on_tab_leave(self, label, idx: int) -> None:
        bg = self._TAB_ACTIVE_BG if idx == self.active_index else self._TAB_BG
        label.config(bg=bg)

    def _tab_context_menu(self, event, idx: int) -> None:
        """Show a right-click context menu for a tab."""
        tk = self.app.tk
        menu = tk.Menu(self.bar, tearoff=0)
        menu.add_command(label="Close", command=lambda: self.close_tab(idx))
        menu.add_command(label="Close Others", command=lambda: self.close_others(idx))
        menu.add_command(label="Close All", command=self.close_all)
        menu.add_separator()
        tab = self.tabs[idx]
        if tab.file_path:
            menu.add_command(
                label="Copy Path",
                command=lambda: self._copy_path(tab.file_path),
            )
            menu.add_command(
                label="Reveal in File Manager",
                command=lambda: self._reveal_path(tab.file_path),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _copy_path(self, path: str) -> None:
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(path)

    def _reveal_path(self, path: str) -> None:
        import subprocess, sys
        folder = os.path.dirname(path)
        if sys.platform == "win32":
            os.startfile(folder)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    # ------------------------------------------------------------------
    #  Theme support
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to the tab bar."""
        bg = theme.get("editor_frame_bg", self._TAB_BG)
        self.bar.config(bg=bg)
        self._tab_frame.config(bg=bg)
        self._add_btn.config(bg=bg)
        # Override class-level defaults temporarily isn't needed — refresh
        # handles active/inactive styling already.  We just update the frame
        # backgrounds.
        self._refresh_tab_bar()

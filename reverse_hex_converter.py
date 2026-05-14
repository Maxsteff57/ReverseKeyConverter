# -*- coding: utf-8 -*-
"""
Reverse Hex Converter
Converts reverse keys to true keys by swapping every group of 4 bytes.
"""

import re
import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from datetime import datetime

# Try to import tkinterdnd2 for drag-and-drop support
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False

# Compiled pattern for a group of exactly 4 space-separated hex bytes (used for hover)
GROUP_OF_4_RE = re.compile(r'[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2}){3}')

# A contiguous run of space-separated 2-char hex bytes, bounded by non-word chars.
# (?<![A-Za-z0-9_]) — not preceded by a word character (avoids matching inside "07_56")
# (?![A-Za-z0-9_])  — not followed by a word character
_HEX_RUN_RE = re.compile(
    r'(?<![A-Za-z0-9_])[0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})*(?![A-Za-z0-9_])'
)


def _reverse_hex_run(match):
    """Reverse each group of 4 bytes within a single hex run."""
    bytes_list = match.group(0).split()
    transformed = []
    for i in range(0, len(bytes_list), 4):
        chunk = bytes_list[i:i + 4]
        transformed.extend(reversed(chunk))
    return ' '.join(transformed)


def transform_line(line):
    """
    Find all contiguous hex-byte runs in the line and reverse every group of 4.
    Non-hex content (prefixes, suffixes, separators like commas) is preserved as-is.
    """
    stripped = line.strip()
    if not stripped or not _HEX_RUN_RE.search(stripped):
        return line
    return _HEX_RUN_RE.sub(_reverse_hex_run, stripped)


def extract_hex_only(line):
    """
    Return only the *significant* hex-byte runs from *line* (runs with ≥ 4
    bytes), stripping all non-hex text (prefixes like "01 Key 3B:",
    suffixes like "Current", separators).  Short stray hex tokens that are
    part of labels (e.g. "01", "3B") are discarded.
    Runs are joined with a single space.
    """
    stripped = line.strip()
    if not stripped:
        return ''
    runs = _HEX_RUN_RE.findall(stripped)
    # Keep only runs with ≥ 4 bytes — short ones are label fragments
    significant = [r for r in runs if len(r.split()) >= 4]
    return ' '.join(significant) if significant else ''


def process_content(text, strip_extra=False):
    """Process multi-line text and return transformed text.
    If *strip_extra* is True, strip non-hex text FIRST, then transform.
    """
    lines = text.splitlines()
    result = []
    for line in lines:
        if strip_extra:
            line = extract_hex_only(line)
        converted = transform_line(line)
        result.append(converted)
    return '\n'.join(result)


def is_line_valid(line):
    """
    Validation rules:
      - Blank lines → True (skip)
      - Lines with no hex runs at all → True (not hex data, don't flag)
      - Lines where EVERY hex run has a byte count divisible by 4 → True
      - Lines where ANY hex run has a byte count NOT divisible by 4 → False
    """
    stripped = line.strip()
    if not stripped:
        return True

    runs = _HEX_RUN_RE.findall(stripped)
    if not runs:
        return True  # no hex content — not a key line, don't mark red

    # Only validate runs with 3+ bytes; shorter runs (1–2 bytes) are likely
    # labels or identifiers (e.g. "01" in "01 Key 3B:"), not data.
    significant = [r for r in runs if len(r.split()) >= 3]
    if not significant:
        return True

    return all(len(run.split()) % 4 == 0 for run in significant)


class ReverseHexConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reverse Hex Converter")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)

        self.current_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.strip_mode = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- File inputs ---
        file_frame = ttk.LabelFrame(main_frame, text="Файлы", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(file_frame, text="Исходный файл (Reverse Keys):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_entry = ttk.Entry(file_frame, textvariable=self.current_file_path, width=60)
        self.input_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(file_frame, text="Обзор...", command=self._browse_input).grid(row=0, column=2, pady=2)

        self.drop_frame = tk.Label(
            file_frame, text="Перетащите файл сюда",
            bg="#e0e0e0", relief="ridge", height=3
        )
        self.drop_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)

        if TKDND_AVAILABLE:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
            self.drop_frame.config(text="Перетащите файл сюда (Drag & Drop)")
        else:
            self.drop_frame.config(text="Drag & Drop недоступен. Используйте кнопку Обзор.")

        ttk.Label(file_frame, text="Сохранить результат (True Keys):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_entry = ttk.Entry(file_frame, textvariable=self.output_file_path, width=60)
        self.output_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(file_frame, text="Обзор...", command=self._browse_output).grid(row=2, column=2, pady=2)

        file_frame.columnconfigure(1, weight=1)

        # --- Buttons ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 10))

        ttk.Button(btn_frame, text="Очистить (Ctrl+D)", command=self._clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Копировать результат", command=self._copy_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Вставить (Ctrl+V)", command=self._paste_to_reverse).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(
            btn_frame, text="Только hex-байты",
            variable=self.strip_mode,
            command=self._auto_convert,
        ).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Сохранить (Ctrl+S) 💾", command=self._start_conversion).pack(side=tk.RIGHT, padx=5)

        # --- Text areas ---
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(1, weight=1)

        ttk.Label(text_frame, text="Реверсивные ключи (Reverse)", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 2))
        self.reverse_text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=('Consolas', 10))
        self.reverse_text.grid(row=1, column=0, sticky=tk.NSEW, padx=(0, 5))

        ttk.Label(text_frame, text="Настоящие ключи (True)", font=('Segoe UI', 9, 'bold')).grid(
            row=0, column=1, sticky=tk.W, pady=(0, 2))
        self.true_text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=('Consolas', 10))
        self.true_text.grid(row=1, column=1, sticky=tk.NSEW, padx=(5, 0))

        # --- Error log panel ---
        log_frame = ttk.LabelFrame(main_frame, text="Журнал ошибок", padding="5")
        log_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(log_frame, text="Очистить журнал (Ctrl+L)", command=self._clear_log).pack(
            anchor=tk.W, pady=(0, 3))
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=4, wrap=tk.WORD,
            font=('Consolas', 9), state=tk.DISABLED,
            background='#1e1e1e', foreground='#ff6b6b'
        )
        self.log_text.pack(fill=tk.X)

        # Allow Ctrl+C copy from the read-only log
        self.log_text.bind('<Control-c>', self._log_copy_selection)
        self.log_text.bind('<Button-3>', self._log_context_menu)

        self._bind_events()

    def _bind_events(self):
        # Hover highlighting
        self.reverse_text.bind('<Motion>', self._on_mouse_move)
        self.true_text.bind('<Motion>', self._on_mouse_move)
        self.reverse_text.bind('<Leave>', self._on_mouse_leave)
        self.true_text.bind('<Leave>', self._on_mouse_leave)

        # Auto-convert on edit
        self.reverse_text.bind('<<Modified>>', self._on_reverse_text_changed)

        # Hover highlight tag (green)
        self.reverse_text.tag_config('highlight', background='#90EE90', foreground='black')
        self.true_text.tag_config('highlight', background='#90EE90', foreground='black')

        # Validation error tag (red)
        self.reverse_text.tag_config('invalid', background='#FF9999', foreground='black')
        self.true_text.tag_config('invalid', background='#FF9999', foreground='black')

        # Green hover must visually override red validation
        self.reverse_text.tag_raise('highlight', 'invalid')
        self.true_text.tag_raise('highlight', 'invalid')

        self._current_highlight = None

        # Hotkeys
        self.root.bind('<Control-s>', lambda e: self._start_conversion())
        self.root.bind('<Control-o>', lambda e: self._browse_input())
        self.root.bind('<Control-l>', lambda e: self._clear_log())
        self.root.bind('<Control-d>', lambda e: self._clear_all())
        # Ctrl+V: bind <<Paste>> virtual event on reverse_text (tkinter translates
        # Ctrl+V to <<Paste>> for Text widgets — more reliable than raw key binding)
        self.reverse_text.bind('<<Paste>>', self._on_reverse_paste)
        # bind_all handles Ctrl+V when focus is outside text areas
        self.root.bind_all('<Control-v>', self._on_ctrl_v)

    # ------------------------------------------------------------------ #
    #  Auto-convert + validation                                           #
    # ------------------------------------------------------------------ #

    def _on_reverse_text_changed(self, event):
        self.reverse_text.edit_modified(False)
        self._auto_convert()

    def _auto_convert(self):
        reverse_content = self.reverse_text.get('1.0', tk.END)
        self.true_text.delete('1.0', tk.END)
        if reverse_content.strip():
            self.true_text.insert('1.0', process_content(
                reverse_content, strip_extra=self.strip_mode.get()))
        self._validate_and_highlight()

    def _validate_and_highlight(self):
        self.reverse_text.tag_remove('invalid', '1.0', tk.END)
        self.true_text.tag_remove('invalid', '1.0', tk.END)

        for widget in (self.reverse_text, self.true_text):
            content = widget.get('1.0', tk.END)
            for lineno, line in enumerate(content.splitlines(), start=1):
                if not is_line_valid(line):
                    widget.tag_add('invalid', f'{lineno}.0', f'{lineno}.end')

    # ------------------------------------------------------------------ #
    #  Hover highlighting                                                  #
    # ------------------------------------------------------------------ #

    def _on_mouse_leave(self, event):
        self._clear_all_highlight()

    def _on_mouse_move(self, event):
        self._highlight_group_sync(event.widget, event.x, event.y)

    def _clear_all_highlight(self):
        self.reverse_text.tag_remove('highlight', '1.0', tk.END)
        self.true_text.tag_remove('highlight', '1.0', tk.END)
        self._current_highlight = None

    def _highlight_group_sync(self, widget, x, y):
        pos = widget.index(f'@{x},{y}')
        if not pos:
            return

        line, col = pos.split('.')
        line = int(line)
        col = int(col)

        line_start = f'{line}.0'
        line_end = f'{line}.end'
        line_text = widget.get(line_start, line_end)

        groups = list(GROUP_OF_4_RE.finditer(line_text))
        if not groups:
            self._clear_all_highlight()
            return

        current_group_idx = next(
            (i for i, g in enumerate(groups) if g.start() <= col < g.end()), -1
        )
        if current_group_idx < 0:
            self._clear_all_highlight()
            return

        highlight_key = (line, current_group_idx)
        if self._current_highlight == highlight_key:
            return

        # Clear first, then store new key (avoid _clear_all_highlight overwriting it)
        self._clear_all_highlight()
        self._current_highlight = highlight_key

        group = groups[current_group_idx]
        widget.tag_add('highlight', f'{line}.{group.start()}', f'{line}.{group.end()}')

        other = self.true_text if widget == self.reverse_text else self.reverse_text
        other_groups = list(GROUP_OF_4_RE.finditer(other.get(line_start, line_end)))
        if len(other_groups) > current_group_idx:
            og = other_groups[current_group_idx]
            other.tag_add('highlight', f'{line}.{og.start()}', f'{line}.{og.end()}')

    # ------------------------------------------------------------------ #
    #  Clipboard                                                           #
    # ------------------------------------------------------------------ #

    def _on_reverse_paste(self, event):
        self._paste_to_reverse()
        return 'break'  # prevent double-paste from root binding

    def _on_ctrl_v(self, event):
        focused = self.root.focus_get()
        # Entry fields handle Ctrl+V natively (tk.Entry covers ttk.Entry too)
        if isinstance(focused, tk.Entry):
            return
        # reverse_text is handled by <<Paste>> binding — skip to avoid double-paste
        if focused is self.reverse_text:
            return
        self._paste_to_reverse()

    def _paste_to_reverse(self):
        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError as e:
            self._log_error(f"Буфер обмена пуст или недоступен: {e}")
            return
        # Replace "Reverse" -> "True" in pasted content
        clipboard_text = clipboard_text.replace('Reverse', 'True')
        try:
            insert_pos = self.reverse_text.index(tk.INSERT)
        except tk.TclError:
            insert_pos = tk.END
        self.reverse_text.insert(insert_pos, clipboard_text)

    def _copy_result(self):
        result = self.true_text.get('1.0', tk.END)
        if result.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            messagebox.showinfo("Копирование", "Результат скопирован в буфер обмена.")

    # ------------------------------------------------------------------ #
    #  File operations                                                     #
    # ------------------------------------------------------------------ #

    def _browse_input(self):
        path = filedialog.askopenfilename(
            title="Выберите файл с реверсивными ключами",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.current_file_path.set(path)
            self._load_input_file(path)
            if not self.output_file_path.get():
                base, ext = os.path.splitext(path)
                self.output_file_path.set(f"{base}_true{ext}")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Сохранить настоящие ключи",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.output_file_path.set(path)

    def _on_drop(self, event):
        path = event.data
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]
        self.current_file_path.set(path)
        self._load_input_file(path)
        if not self.output_file_path.get():
            base, ext = os.path.splitext(path)
            self.output_file_path.set(f"{base}_true{ext}")

    def _load_input_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.reverse_text.delete('1.0', tk.END)
            self.reverse_text.insert('1.0', content)
            self._auto_convert()
        except Exception as e:
            self._log_error(f"Не удалось загрузить файл: {e}")

    def _start_conversion(self):
        true_content = self.true_text.get('1.0', tk.END)
        if not true_content.strip():
            messagebox.showwarning("Внимание", "Нет данных для сохранения.")
            return

        out_path = self.output_file_path.get().strip()
        if not out_path:
            messagebox.showwarning("Внимание", "Укажите путь для сохранения в поле 'Сохранить результат'.")
            return

        try:
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(true_content)
            messagebox.showinfo("Готово", f"Результат сохранен:\n{out_path}")
        except Exception as e:
            self._log_error(f"Ошибка сохранения файла: {e}")

    def _clear_all(self):
        self.current_file_path.set("")
        self.output_file_path.set("")
        self.reverse_text.delete('1.0', tk.END)
        self.true_text.delete('1.0', tk.END)

    # ------------------------------------------------------------------ #
    #  Error log                                                           #
    # ------------------------------------------------------------------ #

    def _log_error(self, message: str):
        ts = datetime.now().strftime('%H:%M:%S')
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _log_copy_selection(self, event=None):
        try:
            selected = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected = self.log_text.get('1.0', tk.END).strip()
        if selected:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        return 'break'

    def _log_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Копировать выделенное", command=self._log_copy_selection)
        menu.add_command(label="Копировать всё", command=lambda: (
            self.root.clipboard_clear(),
            self.root.clipboard_append(self.log_text.get('1.0', tk.END).strip())
        ))
        menu.add_separator()
        menu.add_command(label="Очистить журнал", command=self._clear_log)
        menu.tk_popup(event.x_root, event.y_root)


def main():
    if TKDND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    app = ReverseHexConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

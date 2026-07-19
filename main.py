#!/usr/bin/python
import os
import sys
import tkinter as tk
from tkinter import filedialog

from bnf_editor import BnfEditor
from book_exporter import BookExporter
from dialog_manager import DialogManager
from line_numbers import LineNumbers
from markdown_text import MarkdownText
from replace_dialog import ReplaceDialog
from search_dialog import SearchDialog
from text_corrector import TextCorrector
from toc_list import TOCList
from tooltip import ToolTip


class SideBySideEditor:
    def __init__(self, root):
        self.search_started = None

        self.root = root
        self.root.title("MD Editor")

        self.orig_path = ""

        # Верхний фрейм с заголовком и кнопками
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)

        # Заголовок с названием файла
        self.file_title = tk.Label(
            self.top_frame, text="Файл не загружен", font=("Arial", 12, "bold")
        )
        self.file_title.pack(side=tk.TOP, fill=tk.X)
        # Привязываем клик левой кнопкой мыши к функции копирования
        self.file_title.bind("<Button-1>", self.copy_to_clipboard)

        # Фрейм для кнопок (в левом верхнем углу)
        self.buttons_frame = tk.Frame(self.top_frame)
        self.buttons_frame.pack(side=tk.LEFT, anchor="nw", pady=(5, 0))

        ## Кнопки с иконками

        # load files

        self.load_button = tk.Button(
            self.buttons_frame,
            text="📂",
            command=self.load_md_file_dialog,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.load_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.load_button, "Open File")

        # save files

        self.save_button = tk.Button(
            self.buttons_frame,
            text="💾",
            command=self.save_md_files,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.save_button, "Save Files")

        # export files to book

        self.export_book_menu_button = tk.Menubutton(
            self.buttons_frame,
            text="📖",
            relief=tk.RAISED,
            font=("Noto Color Emoji", 12),
        )
        self.export_book_menu = tk.Menu(
            self.export_book_menu_button, tearoff=0, font=("Arial", 12, "bold")
        )
        ToolTip(self.export_book_menu_button, "Export Book")

        # Список вариантов для выбора
        self.export_variants = {
            "Epub file": "epub",
            "Pdf file": "pdf",
        }

        for label, key in self.export_variants.items():
            self.export_book_menu.add_command(
                label=label, command=lambda cmd=key: self.export_book(cmd)
            )

        self.export_book_menu_button.config(menu=self.export_book_menu)
        self.export_book_menu_button.pack(side=tk.LEFT, padx=(0, 5))

        # reload files
        self.reload_button = tk.Button(
            self.buttons_frame,
            text="🔄",
            command=self.reload_md_files,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.reload_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.reload_button, "Reload Files")

        self.info_button = tk.Button(
            self.buttons_frame,
            text="❕",
            command=self.open_metadata_dialog,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.info_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.info_button, "File Info")

        self.correct_button = tk.Button(
            self.buttons_frame,
            text="📝",
            command=self.correct_text,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.correct_button.pack(side=tk.LEFT, padx=(0, 5))
        ToolTip(self.correct_button, "Correct text")

        self.exit_button = tk.Button(
            self.buttons_frame,
            text="❌",
            command=root.quit,
            font=("Noto Color Emoji", 12, "bold"),
        )
        self.exit_button.pack(side=tk.LEFT)
        ToolTip(self.exit_button, "Exit")

        # Панель форматирования справа
        self.format_frame = tk.Frame(self.top_frame)
        self.format_frame.pack(side=tk.RIGHT, anchor="ne", pady=(5, 0))

        self.bold_button = tk.Button(
            self.format_frame,
            text="**B**",
            command=lambda: self.apply_format("bold"),
            font=("Arial", 8, "bold"),
        )
        self.bold_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.bold_button, "bold format")

        self.italic_button = tk.Button(
            self.format_frame,
            text="*I*",
            command=lambda: self.apply_format("italic"),
            font=("Arial", 8, "italic"),
        )
        self.italic_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.italic_button, "italic format")

        self.h1_button = tk.Button(
            self.format_frame,
            text="H1",
            command=lambda: self.apply_format("h1"),
            font=("Arial", 8),
        )
        self.h1_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.h1_button, "h1 title format")

        self.h2_button = tk.Button(
            self.format_frame,
            text="H2",
            command=lambda: self.apply_format("h2"),
            font=("Arial", 8),
        )
        self.h2_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.h2_button, "h2 title format")

        self.h3_button = tk.Button(
            self.format_frame,
            text="H3",
            command=lambda: self.apply_format("h3"),
            font=("Arial", 8),
        )
        self.h3_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.h3_button, "h3 title format")

        self.h4_button = tk.Button(
            self.format_frame,
            text="H4",
            command=lambda: self.apply_format("h4"),
            font=("Arial", 8),
        )
        self.h4_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.h4_button, "h4 title format")

        self.h5_button = tk.Button(
            self.format_frame,
            text="H5",
            command=lambda: self.apply_format("h5"),
            font=("Arial", 8),
        )
        self.h5_button.pack(side=tk.LEFT, padx=2)
        ToolTip(self.h5_button, "h5 title format")

        # Основной контейнер
        container = tk.Frame(root)
        container.pack(fill=tk.BOTH, expand=True)

        # Создаем фреймы для каждого редактора с номерами строк
        # Левый редактор с оглавлением и номерами строк
        left_editor_frame = tk.Frame(container)
        left_editor_frame.grid(row=0, column=0, sticky="nsew")

        # Панель с кнопкой для левого TOC
        left_top_panel = tk.Frame(left_editor_frame)
        left_top_panel.pack(side=tk.TOP, fill=tk.X)
        self.toggle_left_toc_button = tk.Button(
            left_top_panel,
            text="👈",
            command=self.toggle_left_toc,
            font=("Noto Color Emoji", 10),
        )
        self.toggle_left_toc_button.pack(side=tk.LEFT, anchor="w", padx=2, pady=2)

        self.left_jump_entry = tk.Entry(left_top_panel, width=8)
        self.left_jump_entry.pack(side=tk.LEFT, pady=2)
        self.left_jump_entry.bind(
            "<Return>", lambda e: self.jump_to_line(self.left_jump_entry)
        )
        self.left_jump_entry_button = tk.Button(
            left_top_panel,
            text="Go",
            command=lambda: self.jump_to_line(self.left_jump_entry),
            font=("Noto Color Emoji", 10),
        )
        self.left_jump_entry_button.pack(side=tk.LEFT, anchor="w")
        self.left_search_button = tk.Button(
            left_top_panel,
            text="🔎",
            command=self.on_left_search,
            font=("Noto Color Emoji", 10),
        )
        ToolTip(self.left_search_button, "Search")
        self.left_search_button.pack(side=tk.LEFT, anchor="w")

        self.left_replace_button = tk.Button(
            left_top_panel,
            text="✏",
            command=self.on_left_replace,
            font=("Noto Color Emoji", 10),
        )
        ToolTip(self.left_replace_button, "Replace")
        self.left_replace_button.pack(side=tk.LEFT, anchor="w")

        # Основная часть левого редактора
        self.left_frame = tk.Frame(left_editor_frame)
        self.left_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.left_text = MarkdownText(self.left_frame, wrap="word")
        self.left_scroll = tk.Scrollbar(
            self.left_frame, command=self.on_scroll_left, width=15
        )

        # Левый редактор с оглавлением
        self.left_toc = TOCList(self.left_frame, self.left_text)
        self.left_toc_scroll = tk.Scrollbar(
            self.left_frame, orient=tk.VERTICAL, command=self.left_toc.yview, width=15
        )
        self.left_toc.configure(yscrollcommand=self.left_toc_scroll.set)

        self.left_toc.pack(side=tk.LEFT, fill=tk.Y)
        self.left_toc_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self.left_text.bind("<<Modified>>", self.on_left_text_modified)
        self.left_text.edit_modified(False)

        # Фрейм для номеров строк + поле перехода
        left_num_frame = tk.Frame(self.left_frame)
        left_num_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.left_line_numbers = LineNumbers(left_num_frame, width=50)
        self.left_line_numbers.pack(side=tk.TOP, fill=tk.Y, expand=True)
        self.left_line_numbers.attach(self.left_text)

        self.left_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Подсветка строки с курсором
        self.left_text.tag_configure(
            "current_line", background="#e7ff00", selectbackground="#77b8ff"
        )

        self.left_text.bind("<ButtonRelease-1>", self.highlight_current_line_left)
        self.left_text.bind("<Up>", self.highlight_current_line_left)
        self.left_text.bind("<Down>", self.highlight_current_line_left)
        self.left_text.bind("<Left>", self.highlight_current_line_left)
        self.left_text.bind("<Right>", self.highlight_current_line_left)

        root.bind("<Control-s>", lambda event: self.save_md_files())
        root.bind("<Control-o>", lambda event: self.load_md_file_dialog())

        self.left_text.configure(yscrollcommand=self.on_text_scroll_left)

        self.left_text.bind("<<Modified>>", self.on_left_text_modified)
        self.left_text.edit_modified(False)

        root.bind("<Control-f>", self.on_ctrl_f)
        root.bind("<Control-r>", self.on_ctrl_r)

        self.left_text.bind("<<Paste>>", lambda e: self.update_left_text_async())
        self.left_text.bind("<<Cut>>", lambda e: self.update_left_text_async())

        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            self.load_md_file(file_path)

    def update_left_text_async(self):
        self.left_text.after(300, self.update_left_text)

    def update_left_text(self):
        self.left_text.schedule_highlight_markdown()
        self.left_toc.schedule_update()

    def on_left_text_modified(self, *args):
        self.left_text.on_text_modified()
        line = int(self.left_text.index("insert").split(".")[0])
        text = self.left_text.get(f"{line}.0", f"{line}.end").lstrip()
        if text.startswith("#"):
            self.left_toc.schedule_update()
        elif self.left_toc.check_contains_text(text):
            self.left_toc.schedule_update()

    def open_metadata_dialog(self):
        if not self.orig_path:
            DialogManager.show_dialog("Ошибка", "Сначала откройте файл.")
            return
        BnfEditor(self.orig_path)

    def on_ctrl_f(self, event):
        # определяем, в каком текстовом поле был фокус при нажатии
        text_frame = self.root.focus_get()
        self.open_search_dialog(text_frame)

    def on_ctrl_r(self, event):
        # определяем, в каком текстовом поле был фокус при нажатии
        text_frame = self.root.focus_get()
        self.open_replace_dialog(text_frame)

    def on_left_search(self):
        self.open_search_dialog(self.left_text)

    def on_left_replace(self):
        self.open_replace_dialog(self.left_text)

    def open_search_dialog(self, text_frame):
        SearchDialog(self.root, text_frame)

    def open_replace_dialog(self, text_frame):
        ReplaceDialog(self.root, text_frame)

    def correct_text(self):
        self.text_corrector = TextCorrector(self.left_text)
        self.text_corrector.correct_text(self.orig_path)
        self.left_toc.schedule_update()

    def on_text_scroll_left(self, *args):
        self.left_line_numbers.redraw()
        self.left_scroll.set(args[0], args[1])

    def copy_to_clipboard(self, event=None):
        # Очищаем буфер обмена и копируем текст метки
        root.clipboard_clear()
        root.clipboard_append(self.file_title.cget("text"))

    def jump_to_line(self, entry_widget):
        try:
            line_num = int(entry_widget.get())

            self.left_text.mark_set("insert", f"{line_num}.0")
            self.left_text.see(f"{line_num}.0")

            self.left_text.focus_set()

        except ValueError:
            pass

    def toggle_left_toc(self):
        if self.left_toc.winfo_ismapped():
            self.left_toc.pack_forget()
            self.left_toc_scroll.pack_forget()
            self.toggle_left_toc_button.config(text="📑")  # скрыт
        else:
            self.left_toc = TOCList(self.left_frame, None)
            self.left_toc_scroll = tk.Scrollbar(
                self.left_frame, orient=tk.VERTICAL, command=self.left_toc.yview
            )
            self.left_toc.configure(yscrollcommand=self.left_toc_scroll.set)
            self.left_toc_scroll.pack(
                side=tk.LEFT, fill=tk.Y, before=self.left_line_numbers
            )
            self.left_toc.pack(side=tk.LEFT, fill=tk.Y, before=self.left_toc_scroll)
            self.left_toc.text_widget = self.left_text

            self.left_toc.update_toc()
            self.toggle_left_toc_button.config(text="👈")  # показан

    def apply_format(self, style):
        widget = self.root.focus_get()
        if widget == self.left_text:
            self.left_text.format_line(style)

    def on_scroll_left(self, *args):
        self.left_text.yview(*args)
        self.left_line_numbers.redraw()
        self.left_scroll.set(*args)  # фикс положения ползунка

    def on_scroll_left_toc(self, *args):
        self.left_toc.yview(*args)
        self.left_toc_scroll.set(*args)  # фикс положения ползунка

    def update_file_title(self):
        """Обновляет заголовок с названием файла"""
        if self.orig_path:
            filename, _ = os.path.splitext(os.path.basename(self.orig_path))
            base_name = filename.strip()
            self.file_title.config(text=f"{base_name}")
            self.root.title(base_name)
        else:
            self.file_title.config(text="Файл не загружен")
            self.root.title("MD Editor")

    def save_text_to_file(self, text_widget, path):
        content = text_widget.get("1.0", "end-1c")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def reload_md_files(self):
        """Перезагружает содержимое оригинального и переведённого файла с диска"""
        if not self.orig_path:
            DialogManager.show_dialog("Ошибка", "Файл не загружен")
            return

        try:
            # Сохраняем текущую прокрутку
            left_scroll_pos = self.left_text.yview()[0]

            with open(self.orig_path, "r", encoding="utf-8") as f:
                original_lines = f.read()

            self.left_text.delete("1.0", tk.END)

            self.left_text.insert(tk.END, original_lines)

            self.left_text.highlight_markdown()

            self.left_toc.schedule_update()

            # Восстанавливаем прокрутку
            self.left_text.update_idletasks()  # опционально, но помогает
            self.root.after_idle(lambda: self.left_text.yview_moveto(left_scroll_pos))

            DialogManager.show_dialog("Готово", "Файлы перезагружены с диска.")

        except Exception as e:
            DialogManager.show_dialog("Ошибка загрузки", str(e))

    def load_md_file_dialog(self):
        file_path = filedialog.askopenfilename(
            title="Выбери md файл", filetypes=[("Markdown", "*.md")]
        )
        if not file_path:
            return
        self.load_md_file(file_path)

    def load_md_file(self, file_path):

        self.orig_path = file_path

        try:
            if os.path.exists(self.orig_path):
                with open(self.orig_path, "r", encoding="utf-8") as f:
                    original_lines = f.read()
            else:
                original_lines = ""

            self.left_text.delete("1.0", tk.END)
            self.left_text.insert(tk.END, original_lines)
            self.left_text.highlight_markdown()

            self.left_text.mark_set("insert", "1.0")  # ставим курсор в начало
            self.left_text.see("insert")
            self.left_text.focus_set()

            self.left_toc.schedule_update()
            # Обновляем заголовок после загрузки файлов
            self.update_file_title()

        except Exception as e:
            DialogManager.show_dialog("Ошибка", str(e))

    def adjust_scroll_to_position(self, text_widget, target_index, target_y):
        """Корректирует прокрутку, чтобы указанная позиция была на заданной высоте"""
        try:
            bbox = text_widget.bbox(target_index)
            if bbox is None:
                return
            current_y = bbox[1]
            diff = target_y - current_y
            if abs(diff) > 5:
                line_height = bbox[3] if bbox[3] > 0 else 16
                scroll_lines = diff / line_height
                text_widget.yview_scroll(int(-scroll_lines), "units")
        except:
            pass

    def export_book(self, book_type):
        if not self.orig_path:
            DialogManager.show_dialog("Ошибка", "Файл не загружен")
            return

        original_lines = self.left_text.get("1.0", tk.END).strip().splitlines()

        max_len = len(original_lines)
        original_lines += [""] * (max_len - len(original_lines))

        BookExporter(self.orig_path, book_type, original_lines)

    def save_md_files(self):
        try:
            # 🔹 ЕСЛИ ФАЙЛЫ ЕЩЁ НЕ СОХРАНЯЛИСЬ
            if not self.orig_path:
                path = filedialog.asksaveasfilename(
                    title="Сохранить Markdown файлы",
                    defaultextension=".md",
                    filetypes=[("Markdown files", "*.md")],
                )

                if not path:
                    return  # пользователь отменил

                base, ext = os.path.splitext(path)

                self.orig_path = base + ".md"

            # 🔹 ПОЛУЧАЕМ ТЕКСТ
            original_text = self.left_text.get("1.0", "end-1c").splitlines()

            self.update_file_title()

            # 🔹 СОХРАНЕНИЕ
            with open(self.orig_path, "w", encoding="utf-8") as f:
                f.write("\n".join(original_text) + "\n")

            DialogManager.show_dialog("Успех", "Файлы сохранены.")

        except Exception as e:
            DialogManager.show_dialog("Ошибка сохранения", str(e))

    def highlight_current_line_left(self, event=None):
        # даём курсору переместиться, затем подсвечиваем
        self.root.after(
            1,
            lambda: self._highlight_line_with_sync(self.left_text),
        )
        # обновляем выделение текущего заголовка
        index = self.left_text.index("insert")
        line_num = index.split(".")[0]

        self.left_toc.update_selection_by_text_line(int(line_num))

    def _highlight_line_with_sync(self, src_text):
        self._highlight_line(src_text)

    def _highlight_line(self, text_widget):
        text_widget.tag_remove("current_line", "1.0", "end")
        index = text_widget.index("insert")
        line_start = f"{index.split('.')[0]}.0"
        line_end = f"{index.split('.')[0]}.end"
        text_widget.tag_add("current_line", line_start, line_end)


if __name__ == "__main__":
    root = tk.Tk()
    app = SideBySideEditor(root)
    root.mainloop()

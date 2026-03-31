import tkinter as tk
from tkinter import ttk

from src.ui.search_ui import ArcanaDictionaryApp
from src.ui.translator_ui import ArcanaTranslatorApp
from src.ui.editor_ui import ArcanaEditorApp


class ArcanaHomeApp:
    """
    Main application controller.

    This class manages which screen is currently visible.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Arcana Dictionary")
        self.root.geometry("950x650")

        self.current_screen = None
        self.show_home_screen()

    def clear_screen(self):
        """
        Remove the current screen before showing a new one.
        """
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_home_screen(self):
        """
        Show the first screen the user sees.
        """
        self.clear_screen()

        home_frame = ttk.Frame(self.root, padding=30)
        home_frame.pack(fill="both", expand=True)
        self.current_screen = home_frame

        title_label = ttk.Label(
            home_frame,
            text="Arcana Dictionary",
            font=("Arial", 22, "bold"),
        )
        title_label.pack(pady=(20, 10))

        subtitle_label = ttk.Label(
            home_frame,
            text="Choose what you want to use.",
            font=("Arial", 11),
        )
        subtitle_label.pack(pady=(0, 25))

        button_frame = ttk.Frame(home_frame)
        button_frame.pack(pady=10)

        search_button = ttk.Button(
            button_frame,
            text="Search Dictionary",
            command=self.show_search_screen,
            width=25,
        )
        search_button.pack(pady=8)

        translator_button = ttk.Button(
            button_frame,
            text="Translator",
            command=self.show_translator_screen,
            width=25,
        )
        translator_button.pack(pady=8)

        editor_button = ttk.Button(
            button_frame,
            text="Dictionary Editor",
            command=self.show_editor_screen,
            width=25,
        )
        editor_button.pack(pady=8)

    def show_search_screen(self):
        """
        Replace the home screen with the search screen.
        """
        self.clear_screen()

        search_container = ttk.Frame(self.root)
        search_container.pack(fill="both", expand=True)
        self.current_screen = search_container

        top_bar = ttk.Frame(search_container, padding=10)
        top_bar.pack(fill="x")

        back_button = ttk.Button(
            top_bar,
            text="← Back to Home",
            command=self.show_home_screen,
        )
        back_button.pack(side="left")

        search_frame = ttk.Frame(search_container)
        search_frame.pack(fill="both", expand=True)

        ArcanaDictionaryApp(search_frame)

    def show_translator_screen(self):
        """
        Replace the home screen with the translator screen.
        """
        self.clear_screen()

        translator_container = ttk.Frame(self.root)
        translator_container.pack(fill="both", expand=True)
        self.current_screen = translator_container

        top_bar = ttk.Frame(translator_container, padding=10)
        top_bar.pack(fill="x")

        back_button = ttk.Button(
            top_bar,
            text="← Back to Home",
            command=self.show_home_screen,
        )
        back_button.pack(side="left")

        translator_frame = ttk.Frame(translator_container)
        translator_frame.pack(fill="both", expand=True)

        ArcanaTranslatorApp(translator_frame)

    def show_editor_screen(self):
        """
        Replace the home screen with the dictionary editor screen.
        """
        self.clear_screen()

        editor_container = ttk.Frame(self.root)
        editor_container.pack(fill="both", expand=True)
        self.current_screen = editor_container

        top_bar = ttk.Frame(editor_container, padding=10)
        top_bar.pack(fill="x")

        back_button = ttk.Button(
            top_bar,
            text="← Back to Home",
            command=self.show_home_screen,
        )
        back_button.pack(side="left")

        editor_frame = ttk.Frame(editor_container)
        editor_frame.pack(fill="both", expand=True)

        ArcanaEditorApp(editor_frame)
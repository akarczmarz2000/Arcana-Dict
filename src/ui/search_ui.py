import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.logic.search_functions import (
    load_dictionary_data,
    partial_search,
    exact_search,
    english_search,
    exact_english_search,
)


class ArcanaDictionaryApp:
    def __init__(self, parent):
        self.parent = parent

        self.data = load_dictionary_data()
        self.current_results = []

        # ---------------- TOP FRAME ----------------
        top_frame = ttk.Frame(self.parent, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Search:").grid(row=0, column=0, padx=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        ttk.Label(top_frame, text="Mode:").grid(row=0, column=2, padx=5)

        self.search_mode_labels = {
            "Arcana (partial)": "arcana_partial",
            "Arcana (exact)": "arcana_exact",
            "English (broad)": "english",
            "English (exact)": "english_exact",
        }

        self.search_mode_var = tk.StringVar(value="Arcana (partial)")
        self.search_menu = ttk.Combobox(
            top_frame,
            textvariable=self.search_mode_var,
            values=list(self.search_mode_labels.keys()),
            state="readonly",
            width=25,
        )
        self.search_menu.grid(row=0, column=3, padx=5)

        ttk.Button(top_frame, text="Search", command=self.perform_search).grid(row=0, column=4, padx=5)
        ttk.Button(top_frame, text="Show All", command=self.show_all_entries).grid(row=0, column=5, padx=5)

        # -------- RESULT COUNT LABEL --------
        self.result_count_var = tk.StringVar(value="Results: 0")
        ttk.Label(self.parent, textvariable=self.result_count_var).pack(anchor="w", padx=15)

        # ---------------- MAIN FRAME ----------------
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill="both", expand=True)

        # LEFT
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y")

        results_frame = ttk.Frame(left_frame)
        results_frame.pack()

        self.results_listbox = tk.Listbox(results_frame, width=35, height=28)
        self.results_listbox.pack(side="left", fill="y")
        self.results_listbox.bind("<<ListboxSelect>>", self.show_selected_entry)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_listbox.config(yscrollcommand=scrollbar.set)

        # RIGHT
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))

        self.details_text = tk.Text(right_frame, wrap="word")
        self.details_text.pack(fill="both", expand=True)
        self.details_text.config(state="disabled")

        self.show_all_entries()

    def perform_search(self):
        query = self.search_var.get().strip()
        mode = self.search_mode_labels.get(self.search_mode_var.get(), "arcana_partial")

        if not query:
            messagebox.showwarning("Missing search", "Please type something")
            return

        if mode == "arcana_partial":
            results = partial_search(query, self.data)
        elif mode == "arcana_exact":
            results = exact_search(query, self.data)
        elif mode == "english":
            results = english_search(query, self.data)
        elif mode == "english_exact":
            results = exact_english_search(query, self.data)
        else:
            results = []

        self.update_results_list(results)

    def show_all_entries(self):
        self.update_results_list(self.data)

    def update_results_list(self, results):
        self.results_listbox.delete(0, tk.END)
        self.current_results = results

        self.result_count_var.set(f"Results: {len(results)}")

        for entry in results:
            word = entry.get("id", "Unknown")
            meanings = ", ".join(entry.get("literal_meaning", []))
            self.results_listbox.insert(tk.END, f"{word} - {meanings}")

        self.clear_details()

    def show_selected_entry(self, event=None):
        sel = self.results_listbox.curselection()
        if not sel:
            return

        entry = self.current_results[sel[0]]

        text = (
            f"Word: {entry.get('id')}\n"
            f"Meaning: {', '.join(entry.get('literal_meaning', []))}\n"
            f"Synonyms: {', '.join(entry.get('synonyms', []))}\n"
        )

        self.write_details(text)

    def write_details(self, text):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state="disabled")

    def clear_details(self):
        self.write_details("")
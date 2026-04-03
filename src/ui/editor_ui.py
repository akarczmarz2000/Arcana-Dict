import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.logic.editor_functions import (
    load_dictionary_data,
    add_entry_and_save,
    update_entry_and_save,
    delete_entry_and_save,
)


class ArcanaEditorApp:
    """
    Dictionary editor UI.

    Supports:
    - viewing all entries
    - selecting and editing an entry
    - creating a new entry
    - saving to dictionary.json
    - deleting from dictionary.json
    """

    def __init__(self, parent):
        self.parent = parent
        self.data = load_dictionary_data()
        self.current_index = None

        # ----------------------------------------------------
        # TOP BAR
        # ----------------------------------------------------
        top_bar = ttk.Frame(self.parent, padding=10)
        top_bar.pack(fill="x")

        ttk.Label(top_bar, text="Dictionary Editor", font=("Arial", 16, "bold")).pack(side="left")

        button_frame = ttk.Frame(top_bar)
        button_frame.pack(side="right")

        ttk.Button(button_frame, text="New Entry", command=self.new_entry).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Save Changes", command=self.save_current_entry).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Delete Entry", command=self.delete_current_entry).pack(side="left", padx=4)

        # ----------------------------------------------------
        # MAIN LAYOUT
        # ----------------------------------------------------
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE - entry list
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y")

        ttk.Label(left_frame, text="Entries").pack(anchor="w")

        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill="y", expand=False, pady=(5, 0))

        self.entry_listbox = tk.Listbox(list_frame, width=30, height=28)
        self.entry_listbox.pack(side="left", fill="y")
        self.entry_listbox.bind("<<ListboxSelect>>", self.on_entry_selected)

        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.entry_listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.entry_listbox.config(yscrollcommand=list_scrollbar.set)

        # RIGHT SIDE - editor fields
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))

        ttk.Label(right_frame, text="Entry Details").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self.id_var = tk.StringVar()
        self.literal_meaning_var = tk.StringVar()
        self.synonyms_var = tk.StringVar()
        self.interpretations_var = tk.StringVar()
        self.word_class_var = tk.StringVar()

        self._build_labeled_entry(right_frame, 1, "ID / Word:", self.id_var)
        self._build_labeled_entry(right_frame, 2, "Literal Meaning:", self.literal_meaning_var)
        self._build_labeled_entry(right_frame, 3, "Synonyms:", self.synonyms_var)
        self._build_labeled_entry(right_frame, 4, "Interpretations:", self.interpretations_var)
        self._build_labeled_entry(right_frame, 5, "Word Class:", self.word_class_var)

        ttk.Label(
            right_frame,
            text="For list fields, type values separated by commas.",
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(10, 0))

        right_frame.columnconfigure(1, weight=1)

        self.refresh_entry_list()

    # ----------------------------------------------------
    # UI HELPERS
    # ----------------------------------------------------
    def _build_labeled_entry(self, parent, row, label_text, variable):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="nw", padx=(0, 10), pady=4)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        return entry

    def refresh_entry_list(self):
        """
        Rebuild the visible entry list from self.data.
        """
        self.entry_listbox.delete(0, tk.END)

        for entry in self.data:
            word_id = entry.get("id", "Unknown")
            meanings = ", ".join(entry.get("literal_meaning", [])) if entry.get("literal_meaning") else "No meaning"
            self.entry_listbox.insert(tk.END, f"{word_id} - {meanings}")

    def clear_fields(self):
        self.id_var.set("")
        self.literal_meaning_var.set("")
        self.synonyms_var.set("")
        self.interpretations_var.set("")
        self.word_class_var.set("")

    def load_entry_into_fields(self, entry):
        """
        Put a selected entry into the editable form fields.
        """
        self.id_var.set(entry.get("id", ""))
        self.literal_meaning_var.set(", ".join(entry.get("literal_meaning", [])))
        self.synonyms_var.set(", ".join(entry.get("synonyms", [])))
        self.interpretations_var.set(", ".join(entry.get("interpretations", [])))
        self.word_class_var.set(", ".join(entry.get("word_class", [])))

    def build_entry_from_fields(self):
        """
        Convert the form fields back into a dictionary entry.

        Comma-separated fields stay as strings here.
        The logic file will clean them into lists.
        """
        return {
            "id": self.id_var.get().strip(),
            "literal_meaning": self.literal_meaning_var.get(),
            "synonyms": self.synonyms_var.get(),
            "interpretations": self.interpretations_var.get(),
            "word_class": self.word_class_var.get(),
        }

    # ----------------------------------------------------
    # ACTIONS
    # ----------------------------------------------------
    def on_entry_selected(self, event=None):
        selection = self.entry_listbox.curselection()
        if not selection:
            return

        self.current_index = selection[0]
        entry = self.data[self.current_index]
        self.load_entry_into_fields(entry)

    def new_entry(self):
        """
        Clear the form to start a new entry.
        """
        self.current_index = None
        self.entry_listbox.selection_clear(0, tk.END)
        self.clear_fields()

    def save_current_entry(self):
        """
        Save form changes to dictionary.json.

        If an entry is selected, update it.
        If no entry is selected, create a new one.
        """
        entry = self.build_entry_from_fields()

        try:
            if self.current_index is None:
                self.data = add_entry_and_save(self.data, entry)
                messagebox.showinfo("Entry added", "New entry saved to dictionary.json.")
            else:
                original_id = self.data[self.current_index].get("id", "")
                self.data = update_entry_and_save(self.data, original_id, entry)
                messagebox.showinfo("Entry updated", "Entry saved to dictionary.json.")

            self.refresh_entry_list()
            self.reselect_entry_by_id(entry["id"])

        except ValueError as error:
            messagebox.showwarning("Save failed", str(error))

        except Exception as error:
            messagebox.showerror("Unexpected error", f"Could not save entry.\n\n{error}")

    def delete_current_entry(self):
        """
        Delete the currently selected entry from dictionary.json.
        """
        if self.current_index is None:
            messagebox.showwarning("No selection", "Please select an entry to delete.")
            return

        entry = self.data[self.current_index]
        entry_id = entry.get("id", "Unknown")

        confirmed = messagebox.askyesno(
            "Delete entry",
            f"Delete entry '{entry_id}' from dictionary.json?",
        )
        if not confirmed:
            return

        try:
            self.data = delete_entry_and_save(self.data, entry_id)
            self.current_index = None
            self.refresh_entry_list()
            self.clear_fields()
            messagebox.showinfo("Entry deleted", f"Entry '{entry_id}' deleted and saved.")

        except ValueError as error:
            messagebox.showwarning("Delete failed", str(error))

        except Exception as error:
            messagebox.showerror("Unexpected error", f"Could not delete entry.\n\n{error}")

    def reselect_entry_by_id(self, entry_id):
        """
        After saving, find the entry again in the refreshed list and reselect it.
        """
        target_id = str(entry_id).strip().lower()

        for index, entry in enumerate(self.data):
            if str(entry.get("id", "")).strip().lower() == target_id:
                self.current_index = index
                self.entry_listbox.selection_clear(0, tk.END)
                self.entry_listbox.selection_set(index)
                self.entry_listbox.activate(index)
                self.entry_listbox.see(index)
                self.load_entry_into_fields(entry)
                return
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.logic.search_functions import load_dictionary_data
from src.logic.translator_functions import translate_text


class ArcanaTranslatorApp:
    """
    Translator screen UI.

    This version is built as a writing helper.
    It does not just dump text output.
    Instead it:
    - translates input into token-based suggestions
    - picks a default best option for each token
    - lets the user change the selected word for each token
    - lets the user inspect any suggested entry in a details panel
    """

    def __init__(self, parent):
        self.parent = parent
        self.data = load_dictionary_data()

        # Translation state.
        self.token_candidates = {}
        self.selected_candidates = {}
        self.inspected_entry = None

        # ----------------------------------------------------
        # TOP FRAME
        # ----------------------------------------------------
        top_frame = ttk.Frame(self.parent, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Translator", font=("Arial", 16, "bold")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 10)
        )

        ttk.Label(top_frame, text="Direction:").grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.direction_var = tk.StringVar(value="English to Arcana")
        self.direction_menu = ttk.Combobox(
            top_frame,
            textvariable=self.direction_var,
            values=["English to Arcana", "Arcana to English"],
            state="readonly",
            width=22,
        )
        self.direction_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(top_frame, text="Input:").grid(row=2, column=0, padx=5, pady=5, sticky="nw")

        self.input_text = tk.Text(top_frame, height=5, wrap="word")
        self.input_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        top_frame.columnconfigure(3, weight=1)

        button_frame = ttk.Frame(top_frame)
        button_frame.grid(row=3, column=1, columnspan=3, sticky="w", pady=10)

        ttk.Button(button_frame, text="Translate", command=self.perform_translation).pack(side="left", padx=(0, 8))
        ttk.Button(button_frame, text="Clear", command=self.clear_fields).pack(side="left")

        # Current phrase display.
        self.current_phrase_var = tk.StringVar(value="Current phrase: ")
        ttk.Label(self.parent, textvariable=self.current_phrase_var, padding=(10, 0)).pack(anchor="w")

        # ----------------------------------------------------
        # MAIN AREA
        # ----------------------------------------------------
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.pack(fill="both", expand=True)

        # LEFT SIDE - token suggestion cards
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(left_frame, text="Word Suggestions").pack(anchor="w")

        token_scroll_frame = ttk.Frame(left_frame)
        token_scroll_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.token_canvas = tk.Canvas(token_scroll_frame, highlightthickness=0)
        self.token_canvas.pack(side="left", fill="both", expand=True)

        token_scrollbar = ttk.Scrollbar(
            token_scroll_frame,
            orient="vertical",
            command=self.token_canvas.yview,
        )
        token_scrollbar.pack(side="right", fill="y")

        self.token_canvas.configure(yscrollcommand=token_scrollbar.set)

        self.token_inner_frame = ttk.Frame(self.token_canvas)
        self.token_window = self.token_canvas.create_window((0, 0), window=self.token_inner_frame, anchor="nw")

        self.token_inner_frame.bind("<Configure>", self._update_token_canvas_scrollregion)
        self.token_canvas.bind("<Configure>", self._resize_token_canvas_window)

        # RIGHT SIDE - dictionary entry details
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))

        ttk.Label(right_frame, text="Dictionary Entry Details").pack(anchor="w")

        details_frame = ttk.Frame(right_frame)
        details_frame.pack(fill="both", expand=True, pady=(5, 0))

        self.details_text = tk.Text(details_frame, wrap="word")
        self.details_text.pack(side="left", fill="both", expand=True)
        self.details_text.config(state="disabled")

        details_scrollbar = ttk.Scrollbar(
            details_frame,
            orient="vertical",
            command=self.details_text.yview,
        )
        details_scrollbar.pack(side="right", fill="y")

        self.details_text.config(yscrollcommand=details_scrollbar.set)

        self.write_details(
            "Translator ready.\n\n"
            "Enter text and click Translate.\n"
            "Select a suggested word to build your phrase.\n"
            "Click Inspect to view the full dictionary entry."
        )

    # ----------------------------------------------------
    # CANVAS HELPERS
    # ----------------------------------------------------
    def _update_token_canvas_scrollregion(self, event=None):
        self.token_canvas.configure(scrollregion=self.token_canvas.bbox("all"))

    def _resize_token_canvas_window(self, event):
        self.token_canvas.itemconfig(self.token_window, width=event.width)

    # ----------------------------------------------------
    # TRANSLATION
    # ----------------------------------------------------
    def perform_translation(self):
        input_value = self.input_text.get("1.0", tk.END).strip()
        direction = self.direction_var.get()

        if not input_value:
            messagebox.showwarning("Missing input", "Please type something to translate.")
            return

        result = translate_text(input_value, direction, self.data)

        if result.get("direction") == "english_to_arcana":
            self.load_english_to_arcana_result(result)
        elif result.get("direction") == "arcana_to_english":
            self.load_arcana_to_english_result(result)
        else:
            self.clear_token_cards()
            notes = result.get("notes", ["Unknown translation result."])
            self.write_details("\n".join(notes))

    def load_english_to_arcana_result(self, result):
        """
        Load token-based English to Arcana results into the modular UI.
        """
        self.clear_token_cards()
        self.token_candidates = {}
        self.selected_candidates = {}
        self.inspected_entry = None

        token_results = result.get("tokens", {})

        for token, groups in token_results.items():
            ordered_candidates = (
                groups.get("exact_literal", [])
                + groups.get("exact_synonym", [])
                + groups.get("close_literal", [])
                + groups.get("close_synonym", [])
            )

            seen_ids = set()
            unique_candidates = []
            for candidate in ordered_candidates:
                candidate_id = candidate.get("id", "")
                if candidate_id in seen_ids:
                    continue
                seen_ids.add(candidate_id)
                unique_candidates.append(candidate)

            self.token_candidates[token] = unique_candidates

            if unique_candidates:
                self.selected_candidates[token] = unique_candidates[0]
            else:
                self.selected_candidates[token] = None

        self.build_token_cards()
        self.update_current_phrase_display()

        notes = result.get("notes", [])
        if notes:
            self.write_details("\n".join(notes))
        else:
            self.write_details("Select Inspect on any candidate to view the full entry.")

    def load_arcana_to_english_result(self, result):
        """
        Arcana to English currently displays in the details panel.
        """
        self.clear_token_cards()
        self.token_candidates = {}
        self.selected_candidates = {}
        self.inspected_entry = None
        self.update_current_phrase_display()

        matches = result.get("matches", [])
        close_matches = result.get("close_matches", [])
        notes = result.get("notes", [])

        lines = ["Arcana to English results", ""]

        lines.append("Exact matches:")
        if matches:
            for match in matches:
                meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                synonyms = ", ".join(match.get("synonyms", [])) or "None"
                lines.append(f"- {match.get('id', 'Unknown')} -> meanings: {meanings} | synonyms: {synonyms}")
        else:
            lines.append("- None")

        lines.append("")
        lines.append("Close matches:")
        if close_matches:
            for match in close_matches:
                meanings = ", ".join(match.get("literal_meaning", [])) or "None"
                lines.append(f"- {match.get('id', 'Unknown')} -> {meanings}")
        else:
            lines.append("- None")

        if notes:
            lines.append("")
            lines.append("Notes:")
            for note in notes:
                lines.append(f"- {note}")

        self.write_details("\n".join(lines))

    # ----------------------------------------------------
    # TOKEN CARD BUILDING
    # ----------------------------------------------------
    def clear_token_cards(self):
        for widget in self.token_inner_frame.winfo_children():
            widget.destroy()

    def build_token_cards(self):
        """
        Build one card per input word.
        """
        self.clear_token_cards()

        if not self.token_candidates:
            ttk.Label(
                self.token_inner_frame,
                text="No token suggestions to display.",
            ).pack(anchor="w", pady=10)
            return

        for token, candidates in self.token_candidates.items():
            card = ttk.LabelFrame(self.token_inner_frame, text=f"Word: {token}", padding=10)
            card.pack(fill="x", expand=True, pady=6)

            selected_entry = self.selected_candidates.get(token)
            selected_id = selected_entry.get("id", "None") if selected_entry else "None"

            selected_label_var = tk.StringVar(value=f"Selected: {selected_id}")
            ttk.Label(card, textvariable=selected_label_var).pack(anchor="w", pady=(0, 8))

            if not candidates:
                ttk.Label(card, text="No suggestions found.").pack(anchor="w")
                continue

            selected_var = tk.StringVar(value=selected_id)

            for candidate in candidates:
                row = ttk.Frame(card)
                row.pack(fill="x", pady=2)

                candidate_id = candidate.get("id", "Unknown")
                meanings = ", ".join(candidate.get("literal_meaning", [])) or "None"
                radio_text = f"{candidate_id} -> {meanings}"

                radio = ttk.Radiobutton(
                    row,
                    text=radio_text,
                    variable=selected_var,
                    value=candidate_id,
                    command=lambda t=token, c=candidate, label_var=selected_label_var: self.select_candidate(t, c, label_var),
                )
                radio.pack(side="left", anchor="w")

                inspect_button = ttk.Button(
                    row,
                    text="Inspect",
                    command=lambda c=candidate: self.inspect_candidate(c),
                    width=10,
                )
                inspect_button.pack(side="right")

    def select_candidate(self, token, candidate, selected_label_var=None):
        self.selected_candidates[token] = candidate

        if selected_label_var is not None:
            selected_label_var.set(f"Selected: {candidate.get('id', 'Unknown')}")

        self.update_current_phrase_display()

    def inspect_candidate(self, candidate):
        self.inspected_entry = candidate
        self.show_entry_details(candidate)

    def update_current_phrase_display(self):
        if not self.selected_candidates:
            self.current_phrase_var.set("Current phrase: ")
            return

        parts = []
        for token, selected_entry in self.selected_candidates.items():
            if selected_entry:
                parts.append(selected_entry.get("id", "?"))
            else:
                parts.append(f"[{token}]")

        self.current_phrase_var.set(f"Current phrase: {' '.join(parts)}")

    # ----------------------------------------------------
    # DETAILS PANEL
    # ----------------------------------------------------
    def show_entry_details(self, entry):
        text = (
            f"Word: {entry.get('id', 'Unknown')}\n"
            f"Literal meanings: {', '.join(entry.get('literal_meaning', [])) or 'None'}\n"
            f"Synonyms: {', '.join(entry.get('synonyms', [])) or 'None'}\n"
            f"Word class: {', '.join(entry.get('word_class', [])) or 'None'}\n"
        )

        if "score" in entry and entry.get("score") is not None:
            text += f"Score: {entry.get('score')}\n"

        if entry.get("reasons"):
            text += f"Reasons: {', '.join(entry.get('reasons', []))}\n"

        self.write_details(text)

    def write_details(self, text):
        self.details_text.config(state="normal")
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.config(state="disabled")

    # ----------------------------------------------------
    # CLEAR
    # ----------------------------------------------------
    def clear_fields(self):
        self.input_text.delete("1.0", tk.END)
        self.token_candidates = {}
        self.selected_candidates = {}
        self.inspected_entry = None
        self.clear_token_cards()
        self.update_current_phrase_display()
        self.write_details("")
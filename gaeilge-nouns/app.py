"""
Gaeilge Nouns — practice app for Irish noun declension forms.
Run: python app.py
"""

import json
import random
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

DATA_FILE = Path(__file__).parent / "nouns.json"

LABELS = [
    ("nom_sg",  "nom_sg_article",  "Nominative Singular"),
    ("nom_pl",  "nom_pl_article",  "Nominative Plural"),
    ("gen_sg",  "gen_sg_article",  "Genitive Singular"),
    ("gen_pl",  "gen_pl_article",  "Genitive Plural"),
]

# Colours
BG         = "#1e1e2e"
SURFACE    = "#2a2a3e"
ACCENT     = "#89b4fa"
TEXT       = "#cdd6f4"
SUBTEXT    = "#a6adc8"
CORRECT    = "#a6e3a1"
WRONG      = "#f38ba8"
NEUTRAL    = "#585b70"
ENTRY_BG   = "#313244"
ENTRY_FG   = "#cdd6f4"
BTN_BG     = "#89b4fa"
BTN_FG     = "#1e1e2e"
BTN_HOVER  = "#74c7ec"


def load_nouns():
    if not DATA_FILE.exists():
        messagebox.showerror(
            "Data not found",
            f"Could not find {DATA_FILE}.\n\nPlease run the setup script first:\n  python scraper.py"
        )
        raise SystemExit(1)
    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    # Keep only nouns that have at least nom_sg
    return [n for n in data if n.get("nom_sg")]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.nouns = load_nouns()
        self.current = None
        self.entries = {}
        self.result_labels = {}

        self.title("Gaeilge — Noun Declension Practice")
        self.configure(bg=BG)
        self.resizable(False, False)
        self._build_ui()
        self._next_noun()

    def _build_ui(self):
        pad = {"padx": 24, "pady": 12}

        # Title
        tk.Label(
            self, text="Gaeilge — Noun Practice",
            font=("Helvetica", 18, "bold"),
            bg=BG, fg=ACCENT
        ).pack(pady=(28, 4))

        tk.Label(
            self, text="Fill in each form with the correct article.",
            font=("Helvetica", 10),
            bg=BG, fg=SUBTEXT
        ).pack(pady=(0, 16))

        # Noun display
        self.noun_frame = tk.Frame(self, bg=SURFACE, padx=20, pady=16)
        self.noun_frame.pack(fill="x", padx=24, pady=(0, 20))

        tk.Label(
            self.noun_frame, text="Noun",
            font=("Helvetica", 10), bg=SURFACE, fg=SUBTEXT
        ).pack(anchor="w")

        self.noun_label = tk.Label(
            self.noun_frame, text="",
            font=("Helvetica", 28, "bold"),
            bg=SURFACE, fg=TEXT
        )
        self.noun_label.pack(anchor="w")

        # Form fields
        self.fields_frame = tk.Frame(self, bg=BG)
        self.fields_frame.pack(fill="x", padx=24)

        for key, art_key, label in LABELS:
            row = tk.Frame(self.fields_frame, bg=BG)
            row.pack(fill="x", pady=6)

            tk.Label(
                row, text=label, width=22, anchor="w",
                font=("Helvetica", 11), bg=BG, fg=SUBTEXT
            ).pack(side="left")

            entry = tk.Entry(
                row, font=("Helvetica", 13),
                bg=ENTRY_BG, fg=ENTRY_FG,
                insertbackground=TEXT,
                relief="flat", bd=0,
                width=28,
                highlightthickness=1,
                highlightbackground=NEUTRAL,
                highlightcolor=ACCENT,
            )
            entry.pack(side="left", ipady=6, padx=(0, 10))
            entry.bind("<Return>", lambda e: self._check_answers())
            self.entries[key] = entry

            result = tk.Label(
                row, text="", font=("Helvetica", 11),
                bg=BG, fg=TEXT, width=30, anchor="w"
            )
            result.pack(side="left")
            self.result_labels[key] = result

        # Buttons
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=24)

        self.check_btn = self._make_button(btn_frame, "Check", self._check_answers, BTN_BG, BTN_FG)
        self.check_btn.pack(side="left", padx=8)

        self.next_btn = self._make_button(btn_frame, "Next Noun →", self._next_noun, SURFACE, ACCENT)
        self.next_btn.pack(side="left", padx=8)

        # Score bar
        self.score_var = tk.StringVar(value="")
        tk.Label(
            self, textvariable=self.score_var,
            font=("Helvetica", 10), bg=BG, fg=SUBTEXT
        ).pack(pady=(0, 16))

        self.session_correct = 0
        self.session_total = 0

    def _make_button(self, parent, text, cmd, bg, fg):
        btn = tk.Button(
            parent, text=text, command=cmd,
            font=("Helvetica", 12, "bold"),
            bg=bg, fg=fg,
            activebackground=BTN_HOVER, activeforeground=BTN_FG,
            relief="flat", padx=20, pady=8, cursor="hand2",
            bd=0
        )
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BTN_HOVER))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: b.config(bg=c))
        return btn

    def _next_noun(self):
        self.current = random.choice(self.nouns)
        self.noun_label.config(text=self.current["word"])

        for key, art_key, label in LABELS:
            self.entries[key].delete(0, "end")
            self.entries[key].config(highlightbackground=NEUTRAL)
            self.result_labels[key].config(text="", fg=TEXT)

        # Re-enable check button, focus first entry
        self.check_btn.config(state="normal")
        self.entries["nom_sg"].focus_set()

    def _check_answers(self):
        if not self.current:
            return

        correct_count = 0
        total = 0

        for key, art_key, label in LABELS:
            article_form = self.current.get(art_key)
            if not article_form:
                # No data for this form — skip
                self.result_labels[key].config(
                    text="(no data)", fg=SUBTEXT
                )
                self.entries[key].config(highlightbackground=NEUTRAL)
                continue

            total += 1
            student = self.entries[key].get().strip()
            correct = article_form.strip()

            if student.lower() == correct.lower() and student == correct:
                # Exact match including accents
                self.entries[key].config(highlightbackground=CORRECT)
                self.result_labels[key].config(text=f"✓  {correct}", fg=CORRECT)
                correct_count += 1
            elif student.lower() == correct.lower():
                # Right word but wrong accents
                self.entries[key].config(highlightbackground=WRONG)
                self.result_labels[key].config(
                    text=f"✗  {correct}  (check your fadas)", fg=WRONG
                )
            else:
                self.entries[key].config(highlightbackground=WRONG)
                self.result_labels[key].config(text=f"✗  {correct}", fg=WRONG)

        self.session_total += total
        self.session_correct += correct_count
        pct = int(100 * self.session_correct / self.session_total) if self.session_total else 0
        self.score_var.set(
            f"Session: {self.session_correct}/{self.session_total} correct ({pct}%)"
        )

        self.check_btn.config(state="disabled")

    def _on_close(self):
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app._on_close)
    app.mainloop()

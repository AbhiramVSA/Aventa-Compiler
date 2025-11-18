"""Tkinter-based visualizer for the Banker's Algorithm."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from .examples import available_presets, get_preset
from .model import SystemState


def _compute_trace(system_state: SystemState) -> tuple[bool, list[int] | None, list[str]]:
    """Run the safety algorithm while capturing explanatory trace output."""

    work = system_state.available[:]
    finish = [False] * system_state.num_processes
    safe_sequence: list[int] = []
    trace: list[str] = []

    step = 1
    while len(safe_sequence) < system_state.num_processes:
        progressed = False
        for pid in range(system_state.num_processes):
            if finish[pid]:
                continue
            need = system_state.need_matrix[pid]
            trace.append(
                f"Step {step}: Inspect P{pid} — Need {need}, Work {work}"
            )
            if all(need[j] <= work[j] for j in range(system_state.num_resources)):
                trace.append(
                    f"\tP{pid} can finish. Releasing allocation {system_state.allocation_matrix[pid]}"
                )
                work = [
                    work[j] + system_state.allocation_matrix[pid][j]
                    for j in range(system_state.num_resources)
                ]
                finish[pid] = True
                safe_sequence.append(pid)
                progressed = True
                step += 1
                break
        if not progressed:
            trace.append("System is UNSAFE — no process can proceed with current work vector.")
            return False, None, trace

    trace.append(f"System is SAFE. Safe sequence: {' → '.join(f'P{i}' for i in safe_sequence)}")
    return True, safe_sequence, trace


class BankersVisualizer(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Banker's Algorithm Visualizer")
        self.geometry("1150x760")
        self.resizable(False, False)

        self.presets = available_presets()
        default_key = self.presets[0].key if self.presets else ""

        self.num_processes_var = tk.IntVar(value=3)
        self.num_resources_var = tk.IntVar(value=3)
        self.scenario_var = tk.StringVar(value=default_key)
        self.preset_message_var = tk.StringVar(value="Select a preset to load curated matrices.")

        self.max_entries: list[list[tk.Entry]] = []
        self.alloc_entries: list[list[tk.Entry]] = []
        self.available_entries: list[tk.Entry] = []
        self.preset_cards: dict[str, ttk.Frame] = {}

        self._configure_styles()
        self._build_scrollable_shell()
        self._build_layout()
        self._rebuild_entry_grids()
        if default_key:
            self._load_example(default_key)
        else:
            self._reset_matrices()

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.configure("Card.TFrame", background="#f7f9fc", borderwidth=1, relief="solid")
        style.configure("CardActive.TFrame", background="#e4efff", borderwidth=2, relief="solid")
        style.configure("BadgeSafe.TLabel", foreground="#1c8c4c", padding=(6, 2))
        style.configure("BadgeUnsafe.TLabel", foreground="#b3261e", padding=(6, 2))
        style.configure("Result.TLabel", font=("Segoe UI", 11, "bold"), padding=(10, 6))

    def _build_scrollable_shell(self) -> None:
        self.content_canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.content_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.content_canvas.yview)
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        self.content_scrollbar.pack(side="right", fill="y")
        self.content_canvas.pack(side="left", fill="both", expand=True)

        self.content_frame = ttk.Frame(self.content_canvas)
        self.content_window = self.content_canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind(
            "<Configure>",
            lambda _: self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all")),
        )
        self.content_canvas.bind(
            "<Configure>",
            lambda event: self.content_canvas.itemconfigure(self.content_window, width=event.width),
        )
        self.content_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    # ------------------------------------------------------------------ UI
    def _build_layout(self) -> None:
        controls = ttk.Frame(self.content_frame)
        controls.pack(fill="x", padx=10, pady=(10, 6))

        ttk.Label(controls, text="Processes:").grid(row=0, column=0, padx=5)
        ttk.Spinbox(
            controls,
            from_=1,
            to=10,
            textvariable=self.num_processes_var,
            width=4,
            command=self._rebuild_entry_grids,
        ).grid(row=0, column=1, padx=5)

        ttk.Label(controls, text="Resources:").grid(row=0, column=2, padx=5)
        ttk.Spinbox(
            controls,
            from_=1,
            to=10,
            textvariable=self.num_resources_var,
            width=4,
            command=self._rebuild_entry_grids,
        ).grid(row=0, column=3, padx=5)

        ttk.Button(controls, text="Reset Matrices", command=self._reset_matrices).grid(row=0, column=4, padx=10)
        ttk.Button(controls, text="Blank Canvas", command=self._blank_canvas).grid(row=0, column=5, padx=5)
        ttk.Button(controls, text="Run Safety Check", command=self._run_safety).grid(row=0, column=6, padx=10)

        self._build_preset_panel()

        self.matrix_frame = ttk.Frame(self.content_frame)
        self.matrix_frame.pack(fill="x", padx=10)

        self.max_frame = ttk.LabelFrame(self.matrix_frame, text="Max Matrix")
        self.max_frame.grid(row=0, column=0, padx=5, pady=5)

        self.alloc_frame = ttk.LabelFrame(self.matrix_frame, text="Allocation Matrix")
        self.alloc_frame.grid(row=0, column=1, padx=5, pady=5)

        avail_frame = ttk.LabelFrame(self.matrix_frame, text="Available Vector")
        avail_frame.grid(row=0, column=2, padx=5, pady=5, sticky="n")
        self.available_entries_frame = ttk.Frame(avail_frame)
        self.available_entries_frame.pack(padx=5, pady=5)

        need_frame = ttk.LabelFrame(self.content_frame, text="Need Matrix (auto-computed)")
        need_frame.pack(fill="x", padx=10, pady=10)
        self.need_text = tk.Text(need_frame, height=6, width=80, state="disabled", font=("Consolas", 11))
        self.need_text.pack(fill="x", padx=5, pady=5)

        log_frame = ttk.LabelFrame(self.content_frame, text="Algorithm Trace")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_text = tk.Text(log_frame, state="disabled", font=("Consolas", 11))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self._configure_trace_tags()

        self.result_var = tk.StringVar(value="Run the safety check to begin.")
        self.result_label = ttk.Label(
            self.content_frame,
            textvariable=self.result_var,
            style="Result.TLabel",
            foreground="#1f6b99",
        )
        self.result_label.pack(pady=(0, 10))

    def _build_preset_panel(self) -> None:
        if not self.presets:
            return
        preset_frame = ttk.LabelFrame(self.content_frame, text="Preset Scenarios")
        preset_frame.pack(fill="x", padx=10, pady=(0, 10))
        container = ttk.Frame(preset_frame)
        container.pack(fill="x", padx=5, pady=5)

        for preset in self.presets:
            card = ttk.Frame(container, style="Card.TFrame", padding=8)
            card.pack(fill="x", padx=4, pady=4)
            card.columnconfigure(1, weight=1)
            self.preset_cards[preset.key] = card

            ttk.Radiobutton(
                card,
                variable=self.scenario_var,
                value=preset.key,
                command=self._on_preset_selected,
            ).grid(row=0, column=0, rowspan=2, padx=(0, 10))

            ttk.Label(card, text=preset.title, font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w")
            badge_style = "BadgeSafe.TLabel" if preset.badge.lower() == "safe" else "BadgeUnsafe.TLabel"
            ttk.Label(card, text=preset.badge.upper(), style=badge_style).grid(row=0, column=2, sticky="e", padx=(10, 0))

            ttk.Label(card, text=preset.description, wraplength=850, justify="left").grid(
                row=1,
                column=1,
                columnspan=2,
                sticky="w",
                pady=(2, 0),
            )

        ttk.Label(
            preset_frame,
            textvariable=self.preset_message_var,
            wraplength=1060,
            justify="left",
        ).pack(fill="x", padx=5, pady=(4, 0))

    def _configure_trace_tags(self) -> None:
        self.log_text.tag_configure("step", foreground="#1f6b99", font=("Consolas", 11, "bold"))
        self.log_text.tag_configure("action", foreground="#4a4a4a", lmargin1=20, lmargin2=40)
        self.log_text.tag_configure("safe", foreground="#1c8c4c", font=("Consolas", 11, "bold"))
        self.log_text.tag_configure("unsafe", foreground="#b3261e", font=("Consolas", 11, "bold"))

    # ---------------------------------------------------------------- Utility
    def _rebuild_entry_grids(self) -> None:
        for frame in (self.max_frame, self.alloc_frame):
            for widget in frame.winfo_children():
                widget.destroy()

        rows = self.num_processes_var.get()
        cols = self.num_resources_var.get()
        self.max_entries = self._build_grid(self.max_frame, rows, cols)
        self.alloc_entries = self._build_grid(self.alloc_frame, rows, cols)

        for widget in self.available_entries_frame.winfo_children():
            widget.destroy()
        self.available_entries = []
        for j in range(cols):
            entry = ttk.Entry(self.available_entries_frame, width=6, justify="center")
            entry.grid(row=0, column=j, padx=2, pady=2)
            entry.insert(0, "0")
            self.available_entries.append(entry)

        self._update_need_display([[0] * cols for _ in range(rows)])

    def _build_grid(self, parent: ttk.LabelFrame, rows: int, cols: int) -> list[list[tk.Entry]]:
        entries: list[list[tk.Entry]] = []
        for i in range(rows):
            row_entries: list[tk.Entry] = []
            for j in range(cols):
                entry = ttk.Entry(parent, width=6, justify="center")
                entry.grid(row=i, column=j, padx=2, pady=2)
                entry.insert(0, "0")
                row_entries.append(entry)
            entries.append(row_entries)
        return entries

    def _reset_matrices(self) -> None:
        for grid in (self.max_entries, self.alloc_entries):
            for row in grid:
                for entry in row:
                    entry.delete(0, tk.END)
                    entry.insert(0, "0")
        for entry in self.available_entries:
            entry.delete(0, tk.END)
            entry.insert(0, "0")
        rows = self.num_processes_var.get()
        cols = self.num_resources_var.get()
        self._update_need_display([[0] * cols for _ in range(rows)])
        self._log("Matrices reset to zero.")

    def _blank_canvas(self) -> None:
        self._rebuild_entry_grids()
        self._reset_matrices()
        self.scenario_var.set("custom")
        self.preset_message_var.set("Custom input: edit the matrices and press Run Safety Check.")
        self._highlight_selected_preset()

    def _on_preset_selected(self) -> None:
        self._load_example(self.scenario_var.get())

    def _load_example(self, scenario_key: str) -> None:
        preset = get_preset(scenario_key)
        if not preset:
            self._highlight_selected_preset()
            return

        state = preset.builder()
        self.num_processes_var.set(state.num_processes)
        self.num_resources_var.set(state.num_resources)
        self._rebuild_entry_grids()
        self._populate_matrix(self.max_entries, state.max_matrix)
        self._populate_matrix(self.alloc_entries, state.allocation_matrix)
        self._populate_vector(self.available_entries, state.available)
        self._update_need_display(state.need_matrix)
        self.preset_message_var.set(preset.description)
        self._log(f"Loaded preset: {preset.title}. Press Run Safety Check to visualize.")
        self._highlight_selected_preset()

    def _highlight_selected_preset(self) -> None:
        selected = self.scenario_var.get()
        for key, card in self.preset_cards.items():
            style = "CardActive.TFrame" if key == selected else "Card.TFrame"
            card.configure(style=style)

    def _on_mousewheel(self, event: tk.Event) -> None:  # type: ignore[override]
        if getattr(event, "delta", 0):
            self.content_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _populate_matrix(self, entries: list[list[tk.Entry]], matrix: list[list[int]]) -> None:
        for i, row in enumerate(entries):
            for j, entry in enumerate(row):
                entry.delete(0, tk.END)
                entry.insert(0, str(matrix[i][j]))

    def _populate_vector(self, entries: list[tk.Entry], data: list[int]) -> None:
        for entry, value in zip(entries, data):
            entry.delete(0, tk.END)
            entry.insert(0, str(value))

    def _collect_matrix(self, entries: list[list[tk.Entry]]) -> list[list[int]]:
        matrix = []
        for row in entries:
            matrix.append([self._safe_int(entry.get()) for entry in row])
        return matrix

    def _collect_vector(self, entries: list[tk.Entry]) -> list[int]:
        return [self._safe_int(entry.get()) for entry in entries]

    def _safe_int(self, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            messagebox.showerror("Invalid Input", f"Please enter integer values only. Invalid entry: '{value}'")
            raise

    def _run_safety(self) -> None:
        try:
            max_matrix = self._collect_matrix(self.max_entries)
            allocation_matrix = self._collect_matrix(self.alloc_entries)
            available = self._collect_vector(self.available_entries)
        except ValueError:
            return

        state = SystemState(
            num_processes=self.num_processes_var.get(),
            num_resources=self.num_resources_var.get(),
            max_matrix=max_matrix,
            allocation_matrix=allocation_matrix,
            available=available,
        )

        if not state.validate():
            messagebox.showerror("Invalid State", "Matrix dimensions or values are inconsistent. Please check your inputs.")
            return

        self._update_need_display(state.need_matrix)

        safe, sequence, trace = _compute_trace(state)
        self._render_trace(trace)

        if safe:
            seq_text = " → ".join(f"P{i}" for i in sequence or [])
            self.result_var.set(f"SAFE: Sequence {seq_text}")
            self.result_label.configure(foreground="#1c8c4c")
        else:
            self.result_var.set("UNSAFE: No safe sequence exists for this configuration")
            self.result_label.configure(foreground="#b3261e")

    def _render_trace(self, lines: list[str]) -> None:
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        for line in lines:
            tag = None
            stripped = line.lstrip()
            upper = stripped.upper()
            if upper.startswith("STEP"):
                tag = "step"
            elif upper.startswith("SYSTEM IS SAFE") or "SAFE SEQUENCE" in upper:
                tag = "safe"
            elif "UNSAFE" in upper:
                tag = "unsafe"
            elif line.startswith("\t"):
                tag = "action"

            if tag:
                self.log_text.insert(tk.END, line + "\n", tag)
            else:
                self.log_text.insert(tk.END, line + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)

    def _update_need_display(self, need_matrix: list[list[int]]) -> None:
        self.need_text.configure(state="normal")
        self.need_text.delete("1.0", tk.END)
        for row in need_matrix:
            self.need_text.insert(tk.END, "  ".join(f"{value:>3}" for value in row) + "\n")
        self.need_text.configure(state="disabled")

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)


def launch_visualizer() -> None:
    app = BankersVisualizer()
    app.mainloop()


if __name__ == "__main__":
    launch_visualizer()

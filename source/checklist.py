import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog
import json
import os
from dataclasses import dataclass
from tkinter import ttk   # for better-looking small labels if you want

# ====== Window Setup ======
root = tk.Tk()
root.title("EvoCreo Checklist v1.3.0")
root.configure(bg="lightblue")
root.geometry("600x600")
root.minsize(600, 600)

# ====== Data Model ======


@dataclass
class CreoEntry:
    cid: str
    name: str
    sprite_base: str
    # The four checkboxes' states (0 or 1)
    seen_var:   tk.IntVar
    caught_var: tk.IntVar
    gm_var:     tk.IntVar
    shiny_var:  tk.IntVar
    cb_seen:    tk.Checkbutton
    cb_caught:  tk.Checkbutton
    cb_gm:      tk.Checkbutton
    cb_shiny:   tk.Checkbutton
    # All widgets in this row (for hiding/showing during filter)
    all_widgets: list[tk.Widget]

    icon_photo: ImageTk.PhotoImage
    sprite_mode: str = "normal"
    icon_label: tk.Label = None


# ====== Global Variables ======
creo_entries: dict[str, CreoEntry] = {}
images = {}
toggle_seen = True
toggle_caught = True
toggle_gm = True
toggle_shiny = True
script_dir = os.path.dirname(os.path.abspath(__file__))

# ======= Stats Window ======
stats_window = None  # global reference to the stats window
stats_labels = {}    # store the label widgets so we can update text dynamically


def open_stats_window():
    global stats_window, stats_labels
    if stats_window and stats_window.winfo_exists():
        stats_window.lift()
        stats_window.focus_force()
        return
    stats_window = tk.Toplevel(root)
    stats_window.title("Checklist Stats")
    stats_window.configure(bg="lightblue")
    stats_window.geometry("300x300")
    stats_window.minsize(300, 200)
    stats_window.transient(root)
    # Reset stats_labels dictionary
    stats_labels = {}
    # Create labels and store references for updates
    tk.Label(stats_window, text="Checklist Stats", font=("Segoe UI", 10, "bold"),
             bg="lightblue").pack(pady=10)
    stats_labels["seen"] = tk.Label(stats_window, text="", bg="lightblue")
    stats_labels["seen"].pack(anchor="w", padx=20)
    stats_labels["caught"] = tk.Label(stats_window, text="", bg="lightblue")
    stats_labels["caught"].pack(anchor="w", padx=20)
    stats_labels["gm"] = tk.Label(stats_window, text="", bg="lightblue")
    stats_labels["gm"].pack(anchor="w", padx=20)
    stats_labels["shiny"] = tk.Label(stats_window, text="", bg="lightblue")
    stats_labels["shiny"].pack(anchor="w", padx=20)
    # Congratulatory label
    stats_labels["congrats"] = tk.Label(
        stats_window, text="", bg="lightblue", fg="green", font=("Segoe UI", 9, "bold"))
    stats_labels["congrats"].pack(pady=10)
    # Initial update
    update_stats_labels()


def update_stats_labels():
    if not stats_window or not stats_window.winfo_exists():
        return
    total = len(creo_entries)
    seen = sum(entry.seen_var.get() for entry in creo_entries.values())
    caught = sum(entry.caught_var.get() for entry in creo_entries.values())
    gm = sum(entry.gm_var.get() for entry in creo_entries.values())
    shiny = sum(entry.shiny_var.get() for entry in creo_entries.values())
    stats_labels["seen"].config(text=f"Seen: {seen}/{total}")
    stats_labels["caught"].config(text=f"Caught: {caught}/{total}")
    stats_labels["gm"].config(text=f"GM: {gm}/{total}")
    stats_labels["shiny"].config(text=f"Shiny: {shiny}/{total}")
    congrats_msgs = []
    if seen == total:
        congrats_msgs.append("🎉 Incredible! You've seen every single Creo!")
    if caught == total:
        congrats_msgs.append("🏆 Amazing! You've caught all the Creos!")
    if gm == total:
        congrats_msgs.append("✨ Legendary! You've GM'd all the Creos!")
    if shiny == total:
        congrats_msgs.append("🌟 Spectacular! You've caught every Shiny Creo!")
    stats_labels["congrats"].config(text="\n".join(congrats_msgs))

# ====== Helper Functions ======


def enforce_rules(cid: str):
    """Central place for auto-check + lock logic"""
    entry = creo_entries[cid]
    # Auto-check rules
    if entry.caught_var.get() or entry.gm_var.get() or entry.shiny_var.get():
        entry.seen_var.set(1)
    if entry.gm_var.get():
        entry.caught_var.set(1)
    # Lock / unlock checkboxes
    disable_seen = entry.gm_var.get() or entry.caught_var.get() or entry.shiny_var.get()
    disable_caught = entry.gm_var.get()
    entry.cb_seen.config(state="disabled" if disable_seen else "normal")
    entry.cb_caught.config(state="disabled" if disable_caught else "normal")


def toggle_all_category(category: str):
    toggle_var_name = f"toggle_{category}"
    toggle_var = globals()[toggle_var_name]
    # Decide action based on CURRENT state
    will_check = toggle_var
    new_value = 1 if will_check else 0
    var_attr = f"{category}_var"
    button_attr = f"btn_{category}"
    button = globals()[button_attr]
    changed = False
    for entry in creo_entries.values():
        cb = getattr(entry, f"cb_{category}")
        if not cb.winfo_viewable() or cb.cget("state") == "disabled":
            continue
        var = getattr(entry, var_attr)
        old_value = var.get()
        var.set(new_value)
        if old_value != new_value:
            changed = True
        if new_value == 1:
            if category == "caught":
                entry.seen_var.set(1)
            elif category == "gm":
                entry.seen_var.set(1)
                entry.caught_var.set(1)
            elif category == "shiny":
                entry.seen_var.set(1)
        enforce_rules(entry.cid)
    if changed:
        update_stats_labels()
    globals()[toggle_var_name] = not toggle_var
    next_is_check = globals()[toggle_var_name]
    button_text = f"{'Check' if next_is_check else 'Uncheck'} All {category.title()}"
    button.config(text=button_text)


def apply_filter(*args):
    """Hide/show rows based on search text and the 8 filter checkboxes"""
    query = filter_var.get().lower().strip()
    # Get all filter states (True = show only matching)
    filters = {
        "seen":     show_seen_var.get() == 1,
        "caught":   show_caught_var.get() == 1,
        "gm":       show_gm_var.get() == 1,
        "shiny":    show_shiny_var.get() == 1
    }
    for entry in creo_entries.values():
        show = True
        if query:
            name_match = query in entry.name.lower()
            try:
                id_match = int(query) == int(entry.cid)
            except ValueError:
                id_match = False
            if not (name_match or id_match):
                show = False
        if filters["seen"] and entry.seen_var.get() != 1:
            show = False
        if filters["caught"] and entry.caught_var.get() != 1:
            show = False
        if filters["gm"] and entry.gm_var.get() != 1:
            show = False
        if filters["shiny"] and entry.shiny_var.get() != 1:
            show = False
        for widget in entry.all_widgets:
            widget.grid() if show else widget.grid_remove()
    update_scrollregion()
    update_stats_labels()


def load_creos(path):
    with open(path, "r") as f:
        return json.load(f)


def update_scrollregion():
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(event):
    if canvas.yview() != (0.0, 1.0):
        if os.name == 'nt':
            canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        elif os.name == 'darwin':
            canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")


# ====== Top Frame with Filter & Checkboxes ======
top_frame = tk.Frame(root, bg="lightblue")
top_frame.pack(fill="x", padx=5, pady=5)
# Row 1: Filter
filter_frame = tk.Frame(top_frame, bg="lightblue")
filter_frame.pack(fill="x", pady=2)
# Inner frame to hold label + entry
filter_inner = tk.Frame(filter_frame, bg="lightblue")
filter_inner.pack(anchor="center")  # This centers horizontally
tk.Label(filter_inner, text="Filter:", bg="lightblue").pack(
    side="left", padx=(0, 5))
filter_var = tk.StringVar()
filter_var.trace_add("write", apply_filter)
tk.Entry(filter_inner, textvariable=filter_var, width=30).pack(side="left")
# ===== Row 2: Show Seen / Show Caught, centered =====
checkbox_frame = tk.Frame(top_frame, bg="lightblue")
checkbox_frame.pack(fill="x", pady=2, padx=5)
# Inner frame to hold the checkboxes, centered
checkbox_inner_frame = tk.Frame(checkbox_frame, bg="lightblue")
checkbox_inner_frame.pack(anchor="center")  # Centers horizontally
show_seen_var = tk.IntVar(value=0)
show_caught_var = tk.IntVar(value=0)
show_gm_var = tk.IntVar(value=0)
show_shiny_var = tk.IntVar(value=0)
tk.Checkbutton(checkbox_inner_frame, text="Seen", variable=show_seen_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="Caught", variable=show_caught_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="GM", variable=show_gm_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="Shiny", variable=show_shiny_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
# ===== Row 3: Check All Seen / Check All Caught, Check All GM / Check All Shiny, centered =====
check_frame = tk.Frame(top_frame, bg="lightblue")
check_frame.pack(fill="x", pady=2)
# Inner frame to hold buttons, centered
buttons_inner_frame = tk.Frame(check_frame, bg="lightblue")
# Centers the inner frame horizontally
buttons_inner_frame.pack(anchor="center")
btn_seen = tk.Button(buttons_inner_frame, text="Check All Seen")
btn_seen.pack(side="left", padx=10)
btn_caught = tk.Button(buttons_inner_frame, text="Check All Caught")
btn_caught.pack(side="left", padx=10)
btn_gm = tk.Button(buttons_inner_frame, text="Check All GM")
btn_gm.pack(side="left", padx=10)
btn_shiny = tk.Button(buttons_inner_frame, text="Check All Shiny")
btn_shiny.pack(side="left", padx=10)
btn_seen.config(command=lambda: toggle_all_category("seen"))
btn_caught.config(command=lambda: toggle_all_category("caught"))
btn_gm.config(command=lambda: toggle_all_category("gm"))
btn_shiny.config(command=lambda: toggle_all_category("shiny"))
# Row 4: Info label
info_label = tk.Label(
    top_frame,
    text="Note: Caught Creos always mark Seen.\nGM locks both Seen and Caught.\nShiny locks only Seen; Caught remains editable.",
    bg="lightblue",
    fg="darkblue")
info_label.pack(fill="x", pady=2, padx=5)
# ====== Metadata Label ======
tk.Label(root, text="Accurate as of Jan 19, 2026 | Source: In-game",
         bg="lightblue").pack(side="bottom", pady=5)

# ====== Canvas & Scrollbar (Centered Table) ======
canvas_wrapper = tk.Frame(root, bg="lightblue")
canvas_wrapper.pack(fill="both", expand=True)
# Inner frame to center everything
center_frame = tk.Frame(canvas_wrapper, bg="lightblue")
center_frame.pack(anchor="center", expand=True)
# Canvas for scrollable content
canvas = tk.Canvas(center_frame, bg="lightblue", width=550, height=425,
                   highlightthickness=0, bd=0, relief="flat")
scrollbar = tk.Scrollbar(center_frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
# Pack canvas and scrollbar side by side
canvas.pack(side="left", fill="both", expand=False)
scrollbar.pack(side="left", fill="y")
# Frame inside canvas to hold the table, centered
scrollable_frame = tk.Frame(canvas, bg="lightblue")
table_window = canvas.create_window(
    (0, 0), window=scrollable_frame, anchor="n")
# Function to center table when resizing


def center_table(event):
    canvas_width = canvas.winfo_width()
    table_width = scrollable_frame.winfo_reqwidth()
    x_offset = max((canvas_width - table_width) // 2, 0)
    canvas.coords(table_window, x_offset, 0)


scrollable_frame.bind("<Configure>", lambda e: update_scrollregion())
canvas.bind("<Configure>", center_table)
# Mouse wheel scrolling
canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", on_mousewheel)
canvas.bind_all("<Button-5>", on_mousewheel)

HEADER_WIDTH = {
    "GM\n(Obtained)": 8,
    "Shiny": 9,
    "Name\n(Click for Wiki)": 16,
    "Icon\n(Click to Cycle)": 16,
}
# Column headers
headers = ["ID", "Name\n(Click for Wiki)", "Icon\n(Click to Cycle)",
           "Seen", "Caught", "GM\n(Obtained)", "Shiny"]
for col, text in enumerate(headers):
    tk.Label(scrollable_frame, text=text,
             font=("Segoe UI", 9, "bold"),
             bg="lightblue",
             width=HEADER_WIDTH.get(text, 6),
             anchor="center",
             justify="center"
             ).grid(row=0, column=col, padx=4, pady=2)

# ====== Sprite loader uses sprite_base ======


def load_creo_sprite(sprite_base: str, mode: str = "normal") -> ImageTk.PhotoImage:
    suffix_map = {"normal": "_ns", "gm": "_gms", "shiny": "_ss"}
    suffix = suffix_map.get(mode, "_ns")
    subfolder = mode

    candidates = [
        f"{sprite_base}{suffix}.webp",
        f"{sprite_base}{suffix}.png",
        f"{sprite_base}_{suffix.lstrip('_')}.webp",
        f"{sprite_base}_{suffix.lstrip('_')}.png",
    ]

    fallback = os.path.join(script_dir, "placeholder", "placeholder.png")

    for filename in candidates:
        path = os.path.join(script_dir, "icons", subfolder, filename)
        if os.path.exists(path):
            try:
                return ImageTk.PhotoImage(Image.open(path))
            except Exception as e:
                print(f"Failed to load {path}: {e}")

    return ImageTk.PhotoImage(Image.open(fallback))


# ====== create_creo_row now computes sprite_base ======


def create_creo_row(creo_id: str, creo_data: dict):
    name = creo_data.get("name", "???").strip()

    # Clean name for filename matching (adjust if your filenames need different cleaning)
    sprite_base = (
        name.replace(" ", "_")
        .replace("'", "")
        .replace("-", "_")
        .replace(":", "")
    )

    seen_var = tk.IntVar(value=0)
    caught_var = tk.IntVar(value=0)
    gm_var = tk.IntVar(value=0)
    shiny_var = tk.IntVar(value=0)

    widgets = []
    row_num = len(creo_entries) + 1

    # Column 0 - ID
    w = tk.Label(scrollable_frame, text=creo_id, width=4, bg="lightblue")
    w.grid(row=row_num, column=0, padx=2)
    widgets.append(w)

    # Column 1 - Name (clickable to wiki)
    w = tk.Label(scrollable_frame, text=name,
                 fg="blue", bg="lightblue", anchor="w")
    w.grid(row=row_num, column=1, sticky="w", padx=10)
    w.bind("<Button-1>", lambda e, n=name: webbrowser.open_new(
        f"https://evocreo.fandom.com/wiki/{n.replace(' ', '_')}"))
    widgets.append(w)
    # Column 2 - Icon + mode indicator
    photo = load_creo_sprite(sprite_base, "normal")

    # Create a container frame for icon + badge
    icon_container = tk.Frame(scrollable_frame, bg="lightblue")
    icon_container.grid(row=row_num, column=2, padx=2)

    icon_label = tk.Label(icon_container, image=photo, bg="lightblue")
    icon_label.pack()

    # Small mode indicator label (bottom-right corner)
    mode_label = tk.Label(
        icon_container,
        text="N",               # will be updated later
        font=("Segoe UI", 7, "bold"),
        fg="#444444",
        bg="#ffffff",         # very light semi-transparent gray
        bd=1, relief="solid",
        padx=2, pady=0
    )
    mode_label.place(relx=1.0, rely=1.0, anchor="se")   # bottom-right

    # ← important: add container, not just label
    widgets.append(icon_container)
    # (so filtering hides the whole thing)

    def update_mode_label(mode):
        if mode == "normal":
            txt = "N"
            fg = "#444444"          # dark gray
            bg = "#e8e8e8"        # very light gray, ~50% opacity

        elif mode == "gm":
            txt = "GM"
            fg = "#0066cc"          # strong blue (shiny vibe)
            bg = "#e6f0ff"        # very pale blue, ~80% opacity
        elif mode == "shiny":
            txt = "S"
            fg = "#d4a017"          # gold / golden yellow
            bg = "#fffacd"        # very pale lemon/champagne, ~80% opacity

        mode_label.config(text=txt, fg=fg, bg=bg)

    # Initial update
    update_mode_label("normal")

    def cycle_sprite(event=None):
        entry = creo_entries[creo_id]
        modes = ["normal", "gm", "shiny"]
        current_idx = modes.index(entry.sprite_mode)
        next_mode = modes[(current_idx + 1) % 3]
        entry.sprite_mode = next_mode
        new_photo = load_creo_sprite(entry.sprite_base, next_mode)
        entry.icon_photo = new_photo
        images[creo_id] = new_photo
        icon_label.config(image=new_photo)
        update_mode_label(next_mode)           # ← update badge

    icon_label.bind("<Button-1>", cycle_sprite)
    mode_label.bind("<Button-1>", cycle_sprite)

    # Checkboxes
    def on_change():
        enforce_rules(creo_id)
        update_stats_labels()

    cb_seen = tk.Checkbutton(
        scrollable_frame, variable=seen_var, bg="lightblue", command=on_change)
    cb_seen.grid(row=row_num, column=3)
    widgets.append(cb_seen)

    def on_caught():
        if caught_var.get() == 1:
            seen_var.set(1)
        on_change()

    cb_caught = tk.Checkbutton(
        scrollable_frame, variable=caught_var, bg="lightblue", command=on_caught)
    cb_caught.grid(row=row_num, column=4)
    widgets.append(cb_caught)

    def on_gm():
        if gm_var.get() == 1:
            seen_var.set(1)
            caught_var.set(1)
        on_change()

    cb_gm = tk.Checkbutton(scrollable_frame, variable=gm_var,
                           bg="lightblue", command=on_gm)
    cb_gm.grid(row=row_num, column=5)
    widgets.append(cb_gm)

    def on_shiny():
        if shiny_var.get() == 1:
            seen_var.set(1)
        on_change()

    cb_shiny = tk.Checkbutton(
        scrollable_frame, variable=shiny_var, bg="lightblue", command=on_shiny)
    cb_shiny.grid(row=row_num, column=6)
    widgets.append(cb_shiny)

    entry = CreoEntry(
        cid=creo_id,
        name=name,
        sprite_base=sprite_base,
        icon_photo=photo,
        sprite_mode="normal",
        seen_var=seen_var,
        caught_var=caught_var,
        gm_var=gm_var,
        shiny_var=shiny_var,
        cb_seen=cb_seen,
        cb_caught=cb_caught,
        cb_gm=cb_gm,
        cb_shiny=cb_shiny,
        all_widgets=widgets,
        icon_label=icon_label
    )
    creo_entries[creo_id] = entry
    enforce_rules(creo_id)

# ====== Save / Load and Clear ======


def save_checklist():
    """Save current states to JSON"""
    if not creo_entries:
        messagebox.showinfo("Nothing to save", "No Creos loaded.")
        return
    data = {}
    for cid, entry in creo_entries.items():
        data[cid] = {
            "seen": entry.seen_var.get(),
            "caught": entry.caught_var.get(),
            "gm": entry.gm_var.get(),
            "shiny": entry.shiny_var.get(),
        }
    path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Save Checklist"
    )
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", f"Saved to:\n{path}")
    except Exception as e:
        messagebox.showerror("Error", f"Save failed:\n{e}")


def load_checklist():
    """Load states from JSON (with backwards compatibility for checklist files from before 1.2.0)"""
    if not creo_entries:
        messagebox.showinfo("Nothing loaded", "Load Creos first.")
        return

    path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Load Checklist"
    )
    if not path:
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            saved = json.load(f)

        updated = False  # flag to know if we need to upgrade the file

        for cid, entry in creo_entries.items():
            if cid in saved:
                data = saved[cid]

                # ── Backwards compatibility for old saves (missing gm/shiny) ──
                if "gm" not in data:
                    data["gm"] = 0
                    updated = True
                if "shiny" not in data:
                    data["shiny"] = 0
                    updated = True
                # ──────────────────────────────────────────────────────────────

                entry.seen_var.set(data.get("seen", 0))
                entry.caught_var.set(data.get("caught", 0))
                entry.gm_var.set(data.get("gm", 0))
                entry.shiny_var.set(data.get("shiny", 0))

                # Enforce rules after loading (same as old code)
                if entry.caught_var.get() == 1:
                    entry.seen_var.set(1)
                if entry.gm_var.get() == 1 or entry.shiny_var.get() == 1:
                    entry.seen_var.set(1)
                    entry.caught_var.set(1)

        # Re-apply rules + refresh everything
        for entry in creo_entries.values():
            enforce_rules(entry.cid)
        update_stats_labels()
        apply_filter()

        messagebox.showinfo("Loaded", f"Loaded from:\n{path}")

        # If we added missing keys, overwrite the file (same as old behavior)
        if updated:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(saved, f, indent=2)
            except Exception as e:
                # silent fail is fine
                print("Could not upgrade old save file:", e)

    except Exception as e:
        messagebox.showerror("Error", f"Load failed:\n{e}")


def clear_checklist():
    """Reset all checkboxes"""
    if not messagebox.askyesno("Clear?", "Reset all checkboxes?"):
        return
    for entry in creo_entries.values():
        entry.seen_var.set(0)
        entry.caught_var.set(0)
        entry.gm_var.set(0)
        entry.shiny_var.set(0)
        enforce_rules(entry.cid)
    update_stats_labels()
    apply_filter()
    messagebox.showinfo("Cleared", "All checkboxes reset.")


# ====== Menu ======
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
file_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load Checklist", command=load_checklist)
file_menu.add_command(label="Save Checklist", command=save_checklist)
file_menu.add_separator()
file_menu.add_command(label="Clear Checklist", command=clear_checklist)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Open Stats", command=open_stats_window)

# ====== Load Creos ======
creos = load_creos(os.path.join(script_dir, "creos1.json"))
for cid, data in creos.items():
    if cid == "metadata":
        continue
    create_creo_row(cid, data)

# ====== Initial Scroll Update ======
update_scrollregion()
apply_filter()
root.mainloop()

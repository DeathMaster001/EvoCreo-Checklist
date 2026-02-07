import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog
from tkinter import PhotoImage
import json
import os
from dataclasses import dataclass
from tkinter import ttk   # for better-looking small labels if you want

# ====== Window Setup ======
root = tk.Tk()
root.title("EvoCreo Checklist v1.3.0")
root.configure(bg="lightblue")
root.geometry("700x750")
root.minsize(700, 750)

mode_var = tk.StringVar(value="")  # empty at startup

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
    rank_var:   tk.IntVar
    cb_seen:    tk.Checkbutton
    cb_caught:  tk.Checkbutton
    cb_gm:      tk.Checkbutton
    cb_shiny:   tk.Checkbutton
    sb_rank:    tk.Spinbox
    # All widgets in this row (for hiding/showing during filter)
    all_widgets: list[tk.Widget]
    icon_photo: ImageTk.PhotoImage

    grid_info: dict = None
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

try:
    icon_path = os.path.join(script_dir, "icons", "app", "app.png")
    img = Image.open(icon_path).convert("RGBA")
    tk_icon = ImageTk.PhotoImage(img)
    root.iconphoto(False, tk_icon)
except Exception as e:
    print("Could not load program icon:", e)


def update_stats_labels():
    """
    Update the totals_label under info_label with current checklist stats,
    including Seen, Caught, GM, Shiny counts and congratulatory messages.
    """
    total = len(creo_entries)
    if total == 0:
        totals_label.config(text="No Creos loaded.")
        return

    seen = sum(entry.seen_var.get() for entry in creo_entries.values())
    caught = sum(entry.caught_var.get() for entry in creo_entries.values())
    gm = sum(entry.gm_var.get() for entry in creo_entries.values())
    shiny = sum(entry.shiny_var.get() for entry in creo_entries.values())

    # Base totals text
    if mode_var.get() == "basic":
        text = f"Totals | Seen: {seen}/{total} | Caught: {caught}/{total}"
    else:  # advanced
        text = (f"Totals | Seen: {seen}/{total} | Caught: {caught}/{total} | "
                f"GM: {gm}/{total} | Shiny: {shiny}/{total}")

    # Congratulatory messages
    congrats_msgs = []
    if seen == total:
        congrats_msgs.append("🎉 Incredible! You've seen every Creo!")
    if caught == total:
        congrats_msgs.append("🏆 Amazing! You've caught all the Creos!")
    if gm == total and mode_var.get() == "advanced":
        congrats_msgs.append("✨ Legendary! You've GM'd all the Creos!")
    if shiny == total and mode_var.get() == "advanced":
        congrats_msgs.append("🌟 Spectacular! You've caught every Shiny Creo!")

    if congrats_msgs:
        text += "\n" + "\n".join(congrats_msgs)

    totals_label.config(text=text)


# ====== Helper Functions ======


def choose_startup_mode_modal():
    """Show a modal to pick Basic or Advanced checklist mode with fancy Help buttons."""

    modal = tk.Toplevel(root)
    modal.title("Select Checklist Mode")
    modal.transient(root)
    modal.grab_set()
    modal.resizable(False, False)

    # --- Set the icon for the modal ---
    try:
        modal.iconphoto(False, tk_icon)  # reuse the same tk_icon as root
    except Exception as e:
        print("Could not set modal icon:", e)

    w, h = 400, 180

    frame = tk.Frame(modal, bg="lightblue", bd=2, relief="raised")
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Select Checklist Mode:",
             bg="lightblue", font=("Segoe UI", 11, "bold")).pack(pady=15)

    def show_help(mode):
        if mode == "basic":
            text = (
                "Basic Mode:\n"
                "- Similar to the in-game Creopedia.\n"
                "- Tracks Seen and Caught only.\n"
                "- Caught Creos always mark Seen.\n"
                "- Simplified for quick use.\n\n"
                "Can be converted to Advanced later."
            )
        else:
            text = (
                "Advanced Mode:\n"
                "- For completionists.\n"
                "- Tracks Seen, Caught, GM, Shiny, and Rank.\n"
                "- GM locks both Seen and Caught.\n"
                "- Shiny locks only Seen.\n"
                "- Provides more stats and totals."
            )
        tk.messagebox.showinfo(f"{mode.title()} Mode Help", text)

    def set_mode(mode):
        mode_var.set(mode)
        modal.destroy()

    # --- Helper to create circular blue button with white '?' ---
    def create_help_button(parent, command):
        btn = tk.Button(parent, text="?", command=command,
                        fg="white", bg="#007acc", font=("Segoe UI", 10, "bold"),
                        bd=0, relief="raised", width=2, height=1)
        btn.config(highlightthickness=0)
        return btn

    # ----- Buttons row for Basic -----
    basic_frame = tk.Frame(frame, bg="lightblue")
    basic_frame.pack(pady=5)
    tk.Button(basic_frame, text="Basic", width=12,
              command=lambda: set_mode("basic")).pack(side="left", padx=5)
    create_help_button(basic_frame, lambda: show_help(
        "basic")).pack(side="left", padx=5)

    # ----- Buttons row for Advanced -----
    adv_frame = tk.Frame(frame, bg="lightblue")
    adv_frame.pack(pady=5)
    tk.Button(adv_frame, text="Advanced", width=12,
              command=lambda: set_mode("advanced")).pack(side="left", padx=5)
    create_help_button(adv_frame, lambda: show_help(
        "advanced")).pack(side="left", padx=5)

    # ===== Center modal =====
    def center_modal():
        if modal.winfo_exists():
            root.update_idletasks()
            x = root.winfo_rootx() + (root.winfo_width() - w) // 2
            y = root.winfo_rooty() + (root.winfo_height() - h) // 2
            modal.geometry(f"{w}x{h}+{x}+{y}")
            modal.after(50, center_modal)

    root.update_idletasks()
    center_modal()
    modal.attributes("-topmost", True)
    modal.after(0, lambda: modal.attributes("-topmost", False))
    root.wait_window(modal)


def enforce_rules(cid: str):
    """Central place for auto-check + lock logic"""
    entry = creo_entries[cid]

    # ----- BASIC MODE -----
    if mode_var.get() == "basic":
        if entry.caught_var.get():
            entry.seen_var.set(1)
            entry.cb_seen.config(state="disabled")
        else:
            entry.cb_seen.config(state="normal")

        entry.cb_caught.config(state="normal")
        return

    # ----- ADVANCED MODE -----
    if entry.caught_var.get() or entry.gm_var.get() or entry.shiny_var.get():
        entry.seen_var.set(1)
    if entry.gm_var.get():
        entry.caught_var.set(1)

    disable_seen = entry.gm_var.get() or entry.caught_var.get() or entry.shiny_var.get()
    disable_caught = entry.gm_var.get()

    entry.cb_seen.config(state="disabled" if disable_seen else "normal")
    entry.cb_caught.config(state="disabled" if disable_caught else "normal")


def toggle_all_category(category: str):
    var_attr = f"{category}_var"
    button_attr = f"btn_{category}"
    button = globals()[button_attr]

    # Only affect visible + editable checkboxes
    entries = [
        e for e in creo_entries.values()
        if getattr(e, f"cb_{category}").winfo_ismapped()
        and getattr(e, f"cb_{category}").cget("state") == "normal"
    ]

    if not entries:
        button.config(state="disabled")
        return

    # Decide new state (toggle)
    all_checked = all(getattr(e, var_attr).get() == 1 for e in entries)
    new_value = 0 if all_checked else 1

    # Apply new value
    for e in entries:
        getattr(e, var_attr).set(new_value)
        # auto-checks like Caught->Seen or GM->Caught+Seen
        enforce_rules(e.cid)

    # --- VERY IMPORTANT ---
    # Update all toggle buttons to reflect auto-check changes
    for cat_update in ["seen", "caught", "gm", "shiny"]:
        update_toggle_button_text(cat_update)

    # Update stats label
    update_stats_labels()


def apply_filter(*args):
    """Hide/show rows based on search text and the 4 filter checkboxes"""

    # --- Force-disable GM/Shiny filters in Basic mode ---
    if mode_var.get() == "basic":
        show_gm_var.set(0)
        show_shiny_var.set(0)

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
            if not show:
                widget.grid_remove()
                continue

            # Respect Basic / Advanced mode
            if mode_var.get() == "basic" and widget in entry.advanced_widgets:
                widget.grid_remove()
            else:
                widget.grid()

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
# --- Add filter checkbox variables if not already defined ---
show_seen_var = tk.IntVar(value=0)
show_caught_var = tk.IntVar(value=0)
show_gm_var = tk.IntVar(value=0)
show_shiny_var = tk.IntVar(value=0)

# --- Place checkboxes to the right of the entry in the same row ---
tk.Checkbutton(filter_inner, text="Seen", variable=show_seen_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
tk.Checkbutton(filter_inner, text="Caught", variable=show_caught_var,
               bg="lightblue", command=apply_filter).pack(side="left", padx=10)
cb_filter_gm = tk.Checkbutton(filter_inner, text="GM", variable=show_gm_var,
                              bg="lightblue", command=apply_filter)
cb_filter_gm.pack(side="left", padx=10)
cb_filter_shiny = tk.Checkbutton(filter_inner, text="Shiny", variable=show_shiny_var,
                                 bg="lightblue", command=apply_filter)
cb_filter_shiny.pack(side="left", padx=10)


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
    text="",
    bg="lightblue",
    fg="darkblue")
info_label.pack(fill="x", pady=2, padx=5)
# ===== Extra totals label =====
totals_label = tk.Label(top_frame, text="", bg="lightblue",
                        fg="darkgreen", font=("Segoe UI", 9))
totals_label.pack(fill="x", pady=2, padx=5)
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
canvas = tk.Canvas(center_frame, bg="lightblue", width=650, height=430,
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

header_widgets = {}

HEADER_WIDTH = {
    "Name\n(Click for Wiki)": 16,
    "Icon\n(Click to Cycle)": 16,
    "GM\n(Obtained)": 8
}
# Column headers
headers = ["ID", "Name\n(Click for Wiki)", "Icon\n(Click to Cycle)",
           "Seen", "Caught", "GM\n(Obtained)", "Shiny", "Rank"]
for col, text in enumerate(headers):
    lbl = tk.Label(scrollable_frame, text=text,
                   font=("Segoe UI", 9, "bold"),
                   bg="lightblue",
                   width=HEADER_WIDTH.get(text, 6),
                   anchor="center",
                   justify="center")
    lbl.grid(row=0, column=col, padx=4, pady=2)
    lbl._grid_info = lbl.grid_info()   # save its grid info
    header_widgets[text] = lbl          # store in dict

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


# ====== Creates Creo Rows (ID, Name, Icon + Mode badge, Seen, Caught, GM, Shiny and Rank) ======
def create_creo_row(creo_id: str, creo_data: dict):
    name = creo_data.get("name", "???").strip()

    # Clean name for filename matching
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
    rank_var = tk.IntVar(value=0)  # Rank 0 = unset

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

    # Column 2 - Icon + mode badge
    photo = load_creo_sprite(sprite_base, "normal")
    icon_container = tk.Frame(scrollable_frame, bg="lightblue")
    icon_container.grid(row=row_num, column=2, padx=2)
    icon_label = tk.Label(icon_container, image=photo, bg="lightblue")
    icon_label.pack()
    mode_label = tk.Label(
        icon_container,
        text="N",
        font=("Segoe UI", 7, "bold"),
        fg="#444444",
        bg="#e8e8e8",
        bd=1,
        relief="solid",
        padx=2, pady=0
    )
    mode_label.place(relx=1.0, rely=1.0, anchor="se")
    widgets.append(icon_container)

    def update_mode_label(mode):
        if mode == "normal":
            txt, fg, bgc = "N", "#444444", "#e8e8e8"
        elif mode == "gm":
            txt, fg, bgc = "GM", "#0066cc", "#e6f0ff"
        elif mode == "shiny":
            txt, fg, bgc = "S", "#d4a017", "#fffacd"
        mode_label.config(text=txt, fg=fg, bg=bgc)

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
        update_mode_label(next_mode)

    icon_label.bind("<Button-1>", cycle_sprite)
    mode_label.bind("<Button-1>", cycle_sprite)

    # Column 3 - Seen
    cb_seen = tk.Checkbutton(scrollable_frame, variable=seen_var, bg="lightblue",
                             command=lambda: [enforce_rules(creo_id),
                                              update_stats_labels(),
                                              # ✅ update all toggle buttons
                                              *(update_toggle_button_text(cat) for cat in ["seen", "caught", "gm", "shiny"])])
    cb_seen.grid(row=row_num, column=3)
    widgets.append(cb_seen)

    # Column 4 - Caught
    cb_caught = tk.Checkbutton(scrollable_frame, variable=caught_var, bg="lightblue",
                               command=lambda: [seen_var.set(1) if caught_var.get() else None,
                                                enforce_rules(creo_id),
                                                update_stats_labels(),
                                                # ✅ update all toggle buttons
                                                *(update_toggle_button_text(cat) for cat in ["seen", "caught", "gm", "shiny"])])
    cb_caught.grid(row=row_num, column=4)
    widgets.append(cb_caught)

    # Column 5 - GM
    cb_gm = tk.Checkbutton(scrollable_frame, variable=gm_var, bg="lightblue",
                           command=lambda: [seen_var.set(1), caught_var.set(1) if gm_var.get() else None,
                                            enforce_rules(creo_id),
                                            update_stats_labels(),
                                            # ✅ update all toggle buttons
                                            *(update_toggle_button_text(cat) for cat in ["seen", "caught", "gm", "shiny"])])
    cb_gm.grid(row=row_num, column=5)
    cb_gm._grid_info = cb_gm.grid_info()
    widgets.append(cb_gm)

    # Column 6 - Shiny
    cb_shiny = tk.Checkbutton(scrollable_frame, variable=shiny_var, bg="lightblue",
                              command=lambda: [seen_var.set(1) if shiny_var.get() else None,
                                               enforce_rules(creo_id),
                                               update_stats_labels(),
                                               # ✅ update all toggle buttons
                                               *(update_toggle_button_text(cat) for cat in ["seen", "caught", "gm", "shiny"])])
    cb_shiny.grid(row=row_num, column=6)
    cb_shiny._grid_info = cb_shiny.grid_info()
    widgets.append(cb_shiny)

    # Column 7 - Rank Spinbox
    sb_rank = tk.Spinbox(scrollable_frame, from_=0, to=10,
                         width=3, textvariable=rank_var)
    sb_rank.grid(row=row_num, column=7)
    sb_rank._grid_info = sb_rank.grid_info()
    widgets.append(sb_rank)

    # Create CreoEntry
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
        rank_var=rank_var,
        cb_seen=cb_seen,
        cb_caught=cb_caught,
        cb_gm=cb_gm,
        cb_shiny=cb_shiny,
        sb_rank=sb_rank,
        all_widgets=widgets,
        icon_label=icon_label
    )
    entry.advanced_widgets = {entry.cb_gm, entry.cb_shiny, entry.sb_rank}

    entry.rank_var = rank_var  # save rank variable
    creo_entries[creo_id] = entry

    # Enforce rules and apply Basic/Advanced mode
    enforce_rules(creo_id)
    apply_mode_to_entry(entry, mode_var.get())

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
            "rank": entry.rank_var.get()
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

        updated = False  # track if we need to upgrade old save

        for cid, entry in creo_entries.items():
            if cid in saved:
                data = saved[cid]

                # Backwards compatibility
                if "gm" not in data:
                    data["gm"] = 0
                    updated = True
                if "shiny" not in data:
                    data["shiny"] = 0
                    updated = True
                if "rank" not in data:
                    data["rank"] = 0
                    updated = True

                # Load values
                entry.seen_var.set(data.get("seen", 0))
                entry.caught_var.set(data.get("caught", 0))
                entry.gm_var.set(data.get("gm", 0))
                entry.shiny_var.set(data.get("shiny", 0))
                entry.rank_var.set(data.get("rank", 0))

                # Enforce auto-check rules
                enforce_rules(cid)

        # Refresh stats, filters, and scroll region
        update_stats_labels()
        apply_filter()
        update_scrollregion()

        # Re-apply current mode to ensure correct visibility
        toggle_mode()

        messagebox.showinfo("Loaded", f"Loaded from:\n{path}")

        # Upgrade old save files if needed
        if updated:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(saved, f, indent=2)
            except Exception as e:
                print("Could not upgrade old save file:", e)

    except Exception as e:
        messagebox.showerror("Error", f"Load failed:\n{e}")


def clear_checklist():
    """Reset all checkboxes and rank values to 0"""
    if not messagebox.askyesno("Clear?", "Reset everything?"):
        return
    for entry in creo_entries.values():
        entry.seen_var.set(0)
        entry.caught_var.set(0)
        entry.gm_var.set(0)
        entry.shiny_var.set(0)
        entry.rank_var.set(0)
        enforce_rules(entry.cid)
    update_stats_labels()
    apply_filter()
    messagebox.showinfo("Cleared", "Everything has been reset.")


def toggle_mode():
    """Switch between Basic and Advanced mode for all entries."""
    mode = mode_var.get()

    # ---- Filter checkboxes ----
    if mode == "basic":
        cb_filter_gm.pack_forget()
        cb_filter_shiny.pack_forget()
        show_gm_var.set(0)
        show_shiny_var.set(0)
    else:
        cb_filter_gm.pack(side="left", padx=10)
        cb_filter_shiny.pack(side="left", padx=10)

    # ---- Check-all buttons ----
    if mode == "basic":
        btn_gm.pack_forget()
        btn_shiny.pack_forget()
    else:
        btn_gm.pack(side="left", padx=10)
        btn_shiny.pack(side="left", padx=10)

    # Apply to every Creo row
    for entry in creo_entries.values():
        apply_mode_to_entry(entry, mode)

    # Enable/disable GM/Shiny buttons
    btn_gm.config(state="normal" if mode == "advanced" else "disabled")
    btn_shiny.config(state="normal" if mode == "advanced" else "disabled")

    # Update headers to match mode
    update_headers()

    # Update scroll region
    update_scrollregion()

    # ===== Update info_label text depending on mode =====
    if mode == "basic":
        info_label.config(
            text="Basic Mode: Similar to the Creopedia found in-game.\n"
                 "Seen and Caught are visible.\n"
                 "Caught Creos always mark Seen.")
    else:
        info_label.config(
            text="Advanced Mode: Has more features for completionists.\n"
                 "GM and Shiny columns visible.\n"
                 "GM locks both Seen and Caught.\n"
                 "Shiny locks only Seen; Caught remains editable.\n"
                 "Rank is being worked on.")


def update_headers():
    mode = mode_var.get()
    hide_in_basic = {"GM\n(Obtained)", "Shiny", "Rank"}
    for text, widget in header_widgets.items():
        if text in hide_in_basic:
            if mode == "basic":
                widget.grid_remove()
            else:
                # restore exact original grid info
                widget.grid(**widget._grid_info)

# ===== Helper: Show/hide GM, Shiny, Rank widgets per entry =====


def apply_mode_to_entry(entry: CreoEntry, mode: str):
    """Show or hide GM, Shiny, Rank, and enforce lock rules for Basic/Advanced mode."""
    if mode == "basic":
        # Hide all advanced widgets
        for w in entry.advanced_widgets:
            w.grid_remove()
    else:  # advanced
        # Show all advanced widgets
        for w in entry.advanced_widgets:
            if hasattr(w, "_grid_info") and w._grid_info:
                w.grid(**w._grid_info)

        # Re-enforce lock rules for advanced mode
        enforce_rules(entry.cid)


def update_toggle_button_text(category: str):
    var_attr = f"{category}_var"
    button_attr = f"btn_{category}"
    button = globals()[button_attr]

    # Only consider checkboxes that are visible AND editable
    entries = [
        e for e in creo_entries.values()
        if getattr(e, f"cb_{category}").winfo_ismapped()
        and getattr(e, f"cb_{category}").cget("state") == "normal"
    ]

    if not entries:
        button.config(text=f"Check All {category.title()}", state="disabled")
        return

    button.config(state="normal")
    all_checked = all(getattr(e, var_attr).get() == 1 for e in entries)
    button.config(
        text=f"{'Uncheck' if all_checked else 'Check'} All {category.title()}")


# Only show Advanced conversion if user started in Basic
def convert_to_advanced():
    if mode_var.get() == "advanced":
        messagebox.showinfo("Already Advanced",
                            "Your checklist is already Advanced.")
        return
    if messagebox.askyesno(
        "Convert to Advanced?",
        "Convert this Basic checklist to Advanced?\n\n"
        "This will unlock GM, Shiny, and Rank tracking.\n\n"
            "While you can technically switch back to Basic, advanced data will remain hidden."):

        mode_var.set("advanced")
        toggle_mode()

        # ✅ Update all toggle buttons and totals immediately
        for cat in ["seen", "caught", "gm", "shiny"]:
            update_toggle_button_text(cat)
        update_stats_labels()

        messagebox.showinfo(
            "Converted", "Your checklist is now Advanced!")


# ====== Menu ======
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Load Checklist", command=load_checklist)
file_menu.add_command(label="Save Checklist", command=save_checklist)
file_menu.add_separator()
file_menu.add_command(label="Clear Checklist", command=clear_checklist)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu)
view_menu.add_command(label="Convert to Advanced Checklist",
                      command=convert_to_advanced)

choose_startup_mode_modal()  # User picks mode first
toggle_mode()                # Apply the selected mode

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

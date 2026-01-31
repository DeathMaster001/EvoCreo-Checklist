import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import filedialog
import json
import os

# ====== Window Setup ======
root = tk.Tk()
root.title("EvoCreo Checklist v1.1.0")
root.configure(bg="lightblue")
root.geometry("600x600")
root.minsize(600, 600)

# ======= Stats Window ======
stats_window = None  # global reference to the stats window
stats_labels = {}  # store the label widgets so we can update text dynamically


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
        return  # window not open, nothing to update

    total = len(checkbox_vars)
    seen = sum(v["seen"].get() for v in checkbox_vars.values())
    caught = sum(v["caught"].get() for v in checkbox_vars.values())
    gm = sum(v["gm"].get() for v in checkbox_vars.values())
    shiny = sum(v["shiny"].get() for v in checkbox_vars.values())

    stats_labels["seen"].config(text=f"Seen: {seen}/{total}")
    stats_labels["caught"].config(text=f"Caught: {caught}/{total}")
    stats_labels["gm"].config(text=f"GM: {gm}/{total}")
    stats_labels["shiny"].config(text=f"Shiny: {shiny}/{total}")

    # Congratulatory messages
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


# ====== Global Variables ======
checkbox_vars = {}
row_frames = {}
images = {}
toggle_seen = True
toggle_caught = True
toggle_gm = True
toggle_shiny = True

script_dir = os.path.dirname(os.path.abspath(__file__))

# ====== Helper Functions ======


def update_seen_caught_lock(cid):
    seen_cb = row_frames[cid]["widgets"][3]
    caught_cb = row_frames[cid]["widgets"][4]
    gm = checkbox_vars[cid]["gm"].get()
    shiny = checkbox_vars[cid]["shiny"].get()
    caught = checkbox_vars[cid]["caught"].get()

    # Auto-check Seen if needed
    if caught or gm or shiny:
        checkbox_vars[cid]["seen"].set(1)

    # Only auto-check Caught if GM (Shiny does NOT auto-check Caught)
    if gm:
        checkbox_vars[cid]["caught"].set(1)

    # Lock checkboxes based on rules
    if gm:
        # GM locks both
        seen_cb.config(state="disabled")
        caught_cb.config(state="disabled")
    elif shiny:
        # Shiny locks Seen only
        seen_cb.config(state="disabled")
        caught_cb.config(state="normal")
    elif caught:
        # Caught locks Seen only
        seen_cb.config(state="disabled")
        caught_cb.config(state="normal")
    else:
        # Normal, everything editable
        seen_cb.config(state="normal")
        caught_cb.config(state="normal")


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
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="Caught", variable=show_caught_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="GM", variable=show_gm_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="Shiny", variable=show_shiny_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)

# ===== Row 3: Filter checkboxes 2 centered =====
checkbox_frame2 = tk.Frame(top_frame, bg="lightblue")
checkbox_frame2.pack(fill="x", pady=2, padx=5)

# Inner frame to hold the checkboxes, centered
checkbox_inner_frame2 = tk.Frame(checkbox_frame2, bg="lightblue")
checkbox_inner_frame2.pack(anchor="center")  # Centers horizontally

show_unseen_var = tk.IntVar(value=0)
show_uncaught_var = tk.IntVar(value=0)
show_ungm_var = tk.IntVar(value=0)
show_unshiny_var = tk.IntVar(value=0)

tk.Checkbutton(checkbox_inner_frame2, text="Not Seen", variable=show_unseen_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame2, text="Not Caught", variable=show_uncaught_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame2, text="Not GM", variable=show_ungm_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame2, text="Not Shiny", variable=show_unshiny_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)


# ===== Row 4: Check All Seen / Check All Caught, Check All GM / Check All Shiny, centered =====
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

# Row 5: Info label
info_label = tk.Label(
    top_frame,
    text="Note: Caught Creos always mark Seen.\nGM locks both Seen and Caught.\nShiny locks only Seen; Caught remains editable.",
    bg="lightblue",
    fg="darkblue")
info_label.pack(fill="x", pady=2, padx=5)

# ====== Button Functions ======


def toggle_all_seen():
    global toggle_seen
    for cid, vars in checkbox_vars.items():
        seen_cb = row_frames[cid]["widgets"][3]
        if seen_cb.winfo_viewable() and seen_cb.cget("state") != "disabled":
            vars["seen"].set(1 if toggle_seen else 0)
    btn_seen.config(
        text="Uncheck All Seen" if toggle_seen else "Check All Seen")
    # Apply locks after changes
    for cid in checkbox_vars:
        update_seen_caught_lock(cid)
    update_stats_labels()
    toggle_seen = not toggle_seen


def toggle_all_caught():
    global toggle_caught
    for cid, vars in checkbox_vars.items():
        caught_cb = row_frames[cid]["widgets"][4]
        if caught_cb.winfo_viewable() and caught_cb.cget("state") != "disabled":
            vars["caught"].set(1 if toggle_caught else 0)
            if vars["caught"].get() == 1:
                vars["seen"].set(1)
    btn_caught.config(
        text="Uncheck All Caught" if toggle_caught else "Check All Caught")
    for cid in checkbox_vars:
        update_seen_caught_lock(cid)
    update_stats_labels()
    toggle_caught = not toggle_caught


def toggle_all_gm():
    global toggle_gm
    for cid, vars in checkbox_vars.items():
        gm_cb = row_frames[cid]["widgets"][5]
        if gm_cb.winfo_viewable() and gm_cb.cget("state") != "disabled":
            vars["gm"].set(1 if toggle_gm else 0)
            if vars["gm"].get() == 1:
                vars["seen"].set(1)
                vars["caught"].set(1)
    btn_gm.config(text="Uncheck All GM" if toggle_gm else "Check All GM")
    for cid in checkbox_vars:
        update_seen_caught_lock(cid)
    update_stats_labels()
    toggle_gm = not toggle_gm


def toggle_all_shiny():
    global toggle_shiny
    for cid, vars in checkbox_vars.items():
        shiny_cb = row_frames[cid]["widgets"][6]
        if shiny_cb.winfo_viewable() and shiny_cb.cget("state") != "disabled":
            vars["shiny"].set(1 if toggle_shiny else 0)
            if vars["shiny"].get() == 1:
                vars["seen"].set(1)
                vars["caught"].set(1)
    btn_shiny.config(
        text="Uncheck All Shiny" if toggle_shiny else "Check All Shiny")
    for cid in checkbox_vars:
        update_seen_caught_lock(cid)
    update_stats_labels()
    toggle_shiny = not toggle_shiny


btn_seen.config(command=toggle_all_seen)
btn_caught.config(command=toggle_all_caught)
btn_gm.config(command=toggle_all_gm)
btn_shiny.config(command=toggle_all_shiny)
filter_var.trace_add("write", lambda *args: apply_filter())

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
    "Name (Click for Wiki)": 16,
}

# Column headers
headers = ["ID", "Name (Click for Wiki)", "Icon",
           "Seen", "Caught", "GM\n(Obtained)", "Shiny"]
for col, text in enumerate(headers):
    tk.Label(scrollable_frame, text=text,
             font=("Segoe UI", 9, "bold"),
             bg="lightblue",
             width=HEADER_WIDTH.get(text, 6),
             anchor="center",
             justify="center"
             ).grid(row=0, column=col, padx=4, pady=2)


# ====== Create Rows ======
def create_creo_row(creo_id, creo_data):
    seen_var = tk.IntVar()
    caught_var = tk.IntVar()
    gm_var = tk.IntVar()
    shiny_var = tk.IntVar()
    checkbox_vars[creo_id] = {
        "seen": seen_var, "caught": caught_var, "gm": gm_var, "shiny": shiny_var}

    row = len(row_frames) + 1
    widgets = []

    # ID label
    w = tk.Label(scrollable_frame, text=creo_id, width=4, bg="lightblue")
    w.grid(row=row, column=0, padx=2)
    widgets.append(w)

    # Name
    w = tk.Label(scrollable_frame,
                 text=f"{creo_data.get("name", "")}", fg="blue", bg="lightblue", anchor="w")
    w.grid(row=row, column=1, sticky="w", padx=10)
    w.bind("<Button-1>", lambda e: webbrowser.open_new(
        f"https://evocreo.fandom.com/wiki/{creo_data.get("name", "").replace(" ", "_")}"))
    widgets.append(w)

    # Icon
    img_path = os.path.join(script_dir, creo_data.get("icon", ""))
    if not os.path.exists(img_path):
        img_path = os.path.join(script_dir, "placeholder", "placeholder.png")
    try:
        img = Image.open(img_path)
    except:
        img = Image.open(os.path.join(
            script_dir, "placeholder", "placeholder.png"))
    photo = ImageTk.PhotoImage(img)
    images[creo_id] = photo
    w = tk.Label(scrollable_frame, image=photo, bg="lightblue")
    w.grid(row=row, column=2, padx=2)
    widgets.append(w)

    # Seen checkbox
    seen_cb = tk.Checkbutton(
        scrollable_frame, variable=seen_var, bg="lightblue",
        command=lambda cid=creo_id: [
            update_seen_caught_lock(cid), update_stats_labels()]
    )
    seen_cb.grid(row=row, column=3)
    widgets.append(seen_cb)

    # Caught checkbox with auto-update for Seen
    def caught_clicked(cid=creo_id):
        if checkbox_vars[cid]["caught"].get() == 1:
            checkbox_vars[cid]["seen"].set(1)
        update_seen_caught_lock(cid)
        update_stats_labels()
    caught_cb = tk.Checkbutton(scrollable_frame, variable=caught_var, bg="lightblue",
                               command=caught_clicked)
    caught_cb.grid(row=row, column=4)
    widgets.append(caught_cb)

    # GM checkbox with auto-update for Seen / Caught
    def gm_clicked(cid=creo_id):
        if checkbox_vars[cid]["gm"].get():
            checkbox_vars[cid]["seen"].set(1)
            checkbox_vars[cid]["caught"].set(1)
        update_seen_caught_lock(cid)
        update_stats_labels()
    gm_cb = tk.Checkbutton(
        scrollable_frame, variable=gm_var, bg="lightblue", command=gm_clicked)
    gm_cb.grid(row=row, column=5)
    widgets.append(gm_cb)

    # Shiny checkbox with auto-update for Seen
    def shiny_clicked(cid=creo_id):
        if checkbox_vars[cid]["shiny"].get():
            checkbox_vars[cid]["seen"].set(1)  # Always mark Seen
            # Do NOT auto-check Caught to allow edge cases where Shiny isn't caught
        update_seen_caught_lock(cid)
        update_stats_labels()
    shiny_cb = tk.Checkbutton(
        scrollable_frame, variable=shiny_var, bg="lightblue", command=shiny_clicked)
    shiny_cb.grid(row=row, column=6)
    widgets.append(shiny_cb)

    row_frames[creo_id] = {"seen_var": seen_var,
                           "caught_var": caught_var, "gm_var": gm_var, "shiny_var": shiny_var, "widgets": widgets}


# ====== Filter Function ======
def apply_filter(*args):
    query = filter_var.get().lower().strip()
    seen_only = show_seen_var.get() == 1
    caught_only = show_caught_var.get() == 1
    gm_only = show_gm_var.get() == 1
    shiny_only = show_shiny_var.get() == 1
    unseen_only = show_unseen_var.get() == 1
    uncaught_only = show_uncaught_var.get() == 1
    ungm_only = show_ungm_var.get() == 1
    unshiny_only = show_unshiny_var.get() == 1

    for cid, data in row_frames.items():
        creo_name = creos[cid]["name"].lower()
        seen_checked = data["seen_var"].get()
        caught_checked = data["caught_var"].get()
        gm_checked = data["gm_var"].get()
        shiny_checked = data["shiny_var"].get()

        show = True

        if query:
            # Match numeric ID exactly
            id_match = False
            try:
                qnum = int(query)
                if int(cid) == qnum:
                    id_match = True
            except ValueError:
                pass

            # Match name substring
            name_match = query in creo_name

            # Show only if either matches
            if not (id_match or name_match):
                show = False

        # Seen Only: must be seen
        if seen_only and seen_checked != 1:
            show = False

        # Caught Only: must be caught
        if caught_only and caught_checked != 1:
            show = False

        # GM Only
        if gm_only and gm_checked != 1:
            show = False

        # Shiny Only
        if shiny_only and shiny_checked != 1:
            show = False

        # Unseen Only: must NOT be seen
        if unseen_only and seen_checked != 0:
            show = False

        # Uncaught Only: must NOT be caught
        if uncaught_only and caught_checked != 0:
            show = False

        # UnGM Only
        if ungm_only and gm_checked != 0:
            show = False

        # UnShiny Only
        if unshiny_only and shiny_checked != 0:
            show = False

        for w in data["widgets"]:
            if show:
                w.grid()
            else:
                w.grid_remove()

    update_scrollregion()
    update_stats_labels()


def clear_checklist():
    if messagebox.askyesno("Clear Checklist", "Are you sure you want to clear all checkboxes?"):
        for cid, vars in checkbox_vars.items():
            vars["seen"].set(0)
            vars["caught"].set(0)
            vars["gm"].set(0)
            vars["shiny"].set(0)
            update_seen_caught_lock(cid)
        update_stats_labels()
        messagebox.showinfo("Checklist Cleared",
                            "All checkboxes have been reset.")


# ====== Save / Load with File Dialog ======
def save_checklist():
    checked = {cid: {"seen": vars["seen"].get(), "caught": vars["caught"].get(), "gm": vars["gm"].get(), "shiny": vars["shiny"].get()}
               for cid, vars in checkbox_vars.items()}

    save_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Save Checklist"
    )

    if save_path:
        try:
            with open(save_path, "w") as f:
                json.dump(checked, f, indent=2)
            messagebox.showinfo("Checklist Saved",
                                f"Saved {len(checked)} Creo(s) successfully!")
        except Exception as e:
            messagebox.showerror("Error Saving Checklist", str(e))


def open_checklist():
    load_path = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Open Checklist"
    )

    if load_path:
        try:
            with open(load_path, "r") as f:
                saved = json.load(f)

            updated = False  # Track if we added missing keys

            for cid, vars in checkbox_vars.items():
                data = saved.get(cid, {})

                # Ensure gm and shiny exist
                if "gm" not in data:
                    data["gm"] = 0
                    updated = True
                if "shiny" not in data:
                    data["shiny"] = 0
                    updated = True

                # Update the checkbox variables
                vars["seen"].set(data.get("seen", 0))
                vars["caught"].set(data.get("caught", 0))
                vars["gm"].set(data.get("gm", 0))
                vars["shiny"].set(data.get("shiny", 0))
                # Enforce rules after loading values
                if vars["caught"].get() == 1:
                    vars["seen"].set(1)

                if vars["gm"].get() == 1 or vars["shiny"].get() == 1:
                    vars["seen"].set(1)
                    vars["caught"].set(1)

                update_seen_caught_lock(cid)

                if stats_window and stats_window.winfo_exists():
                    update_stats_labels()

                # Save the updated values back to saved dict
                saved[cid] = data

            # If any keys were added, overwrite the file so checklist supports them
            if updated:
                with open(load_path, "w") as f:
                    json.dump(saved, f, indent=2)

            messagebox.showinfo("Checklist Loaded",
                                f"Loaded {len(saved)} Creo(s) successfully!")
        except Exception as e:
            messagebox.showerror("Error Loading Checklist", str(e))
    else:
        messagebox.showwarning(
            "No File Selected", "No file was selected to load.")


# ====== Menu ======
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
file_menu = tk.Menu(menu_bar, tearoff=0)
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_checklist)
file_menu.add_command(label="Save", command=save_checklist)
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

root.mainloop()

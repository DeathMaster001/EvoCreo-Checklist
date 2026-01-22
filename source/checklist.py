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

# ====== Global Variables ======
checkbox_vars = {}
row_frames = {}
images = {}
toggle_seen = True
toggle_caught = True

script_dir = os.path.dirname(os.path.abspath(__file__))

# ====== Helper Functions ======


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
tk.Label(filter_frame, text="Filter (Name or ID):",
         bg="lightblue").pack(fill="x", pady=2, padx=5)
filter_var = tk.StringVar()
filter_entry = tk.Entry(filter_frame, textvariable=filter_var, width=30)
filter_entry.pack(pady=2, padx=5)

# ===== Row 2: Show Seen / Show Caught, centered =====
checkbox_frame = tk.Frame(top_frame, bg="lightblue")
checkbox_frame.pack(fill="x", pady=2, padx=5)

# Inner frame to hold the checkboxes, centered
checkbox_inner_frame = tk.Frame(checkbox_frame, bg="lightblue")
checkbox_inner_frame.pack(anchor="center")  # Centers horizontally

show_seen_var = tk.IntVar(value=0)
show_caught_var = tk.IntVar(value=0)

tk.Checkbutton(checkbox_inner_frame, text="Seen Only", variable=show_seen_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)
tk.Checkbutton(checkbox_inner_frame, text="Caught Only", variable=show_caught_var,
               bg="lightblue", command=lambda: apply_filter()).pack(side="left", padx=10)


# ===== Row 3: Check All Seen / Check All Caught, centered =====
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

# Row 4: Info label
info_label = tk.Label(top_frame, text="Note: Caught Creos are always Seen — Seen checkboxes are locked.",
                      bg="lightblue", fg="darkblue")
info_label.pack(fill="x", pady=2, padx=5)


# ====== Button Functions ======


def toggle_all_seen():
    global toggle_seen
    for cid, vars in checkbox_vars.items():
        seen_cb = row_frames[cid]["widgets"][0]
        if seen_cb.cget("state") != "disabled":
            vars["seen"].set(1 if toggle_seen else 0)
    btn_seen.config(
        text="Uncheck All Seen" if toggle_seen else "Check All Seen")
    toggle_seen = not toggle_seen


def toggle_all_caught():
    global toggle_caught
    for cid, vars in checkbox_vars.items():
        vars["caught"].set(1 if toggle_caught else 0)
        # Enforce Caught → Seen
        if vars["caught"].get() == 1:
            vars["seen"].set(1)
            row_frames[cid]["widgets"][0].config(state="disabled")
        else:
            row_frames[cid]["widgets"][0].config(state="normal")
    btn_caught.config(
        text="Uncheck All Caught" if toggle_caught else "Check All Caught")
    toggle_caught = not toggle_caught


btn_seen.config(command=toggle_all_seen)
btn_caught.config(command=toggle_all_caught)
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
canvas = tk.Canvas(center_frame, bg="lightblue", width=500, height=400)
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


# Column headers
headers = ["Seen", "Caught", "ID", "Icon", "Name (Click for Wiki)"]
for col, text in enumerate(headers):
    tk.Label(scrollable_frame, text=text, font=("Segoe UI", 9, "bold"),
             bg="lightblue", width=16 if text == "Name (Click for Wiki)" else 6).grid(row=0, column=col, padx=5, pady=2, sticky="w")


# ====== Create Rows ======


def create_creo_row(creo_id, creo_data):
    seen_var = tk.IntVar()
    caught_var = tk.IntVar()
    checkbox_vars[creo_id] = {"seen": seen_var, "caught": caught_var}

    row = len(row_frames) + 1
    widgets = []

    # Seen checkbox
    seen_cb = tk.Checkbutton(
        scrollable_frame, variable=seen_var, bg="lightblue")
    seen_cb.grid(row=row, column=0)
    widgets.append(seen_cb)

    # Caught checkbox with auto-update for Seen
    def caught_clicked(cid=creo_id):
        if checkbox_vars[cid]["caught"].get() == 1:
            checkbox_vars[cid]["seen"].set(1)
            row_frames[cid]["widgets"][0].config(state="disabled")
        else:
            row_frames[cid]["widgets"][0].config(state="normal")
    caught_cb = tk.Checkbutton(scrollable_frame, variable=caught_var, bg="lightblue",
                               command=caught_clicked)
    caught_cb.grid(row=row, column=1)
    widgets.append(caught_cb)

    # ID label
    w = tk.Label(scrollable_frame, text=creo_id, width=4, bg="lightblue")
    w.grid(row=row, column=2, padx=2)
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
    w.grid(row=row, column=3, padx=2)
    widgets.append(w)

    # Name
    w = tk.Label(scrollable_frame,
                 text=f"{creo_data.get("name", "")}", fg="blue", bg="lightblue", anchor="w")
    w.grid(row=row, column=4, sticky="w", padx=5)
    w.bind("<Button-1>", lambda e: webbrowser.open_new(
        f"https://evocreo.fandom.com/wiki/{creo_data.get("name", "").replace(" ", "_")}"))
    widgets.append(w)

    row_frames[creo_id] = {"seen_var": seen_var,
                           "caught_var": caught_var, "widgets": widgets}


# ====== Filter Function ======
def apply_filter(*args):
    query = filter_var.get().lower().strip()
    seen_only = show_seen_var.get() == 1
    caught_only = show_caught_var.get() == 1

    for cid, data in row_frames.items():
        creo_name = creos[cid]["name"].lower()
        seen_checked = data["seen_var"].get()
        caught_checked = data["caught_var"].get()

        show = True

        # Filter by ID: exact match only
        if query:
            if cid != query and query not in creo_name:
                show = False

        # Filter by Seen Only: must be seen AND NOT caught
        if seen_only and not (seen_checked == 1 and caught_checked == 0):
            show = False

        # Filter by Caught Only
        if caught_only and caught_checked != 1:
            show = False

        for w in data["widgets"]:
            if show:
                w.grid()
            else:
                w.grid_remove()

    update_scrollregion()


# ====== Save / Load with File Dialog ======
def save_checklist():
    checked = {cid: {"seen": vars["seen"].get(), "caught": vars["caught"].get()}
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


def load_checklist():
    load_path = filedialog.askopenfilename(
        defaultextension=".json",
        filetypes=[("JSON Files", "*.json")],
        title="Load Checklist"
    )

    if load_path:
        try:
            with open(load_path, "r") as f:
                saved = json.load(f)
            for cid, vars in checkbox_vars.items():
                data = saved.get(cid, {})
                vars["seen"].set(data.get("seen", 0))
                vars["caught"].set(data.get("caught", 0))
                if vars["caught"].get() == 1:
                    vars["seen"].set(1)
                    row_frames[cid]["widgets"][0].config(state="disabled")
                else:
                    row_frames[cid]["widgets"][0].config(state="normal")
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
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save Checklist", command=save_checklist)
file_menu.add_command(label="Load Checklist", command=load_checklist)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# ====== Load Creos ======
creos = load_creos(os.path.join(script_dir, "creos1.json"))
for cid, data in creos.items():
    if cid == "metadata":
        continue
    create_creo_row(cid, data)

# ====== Initial Scroll Update ======
update_scrollregion()

root.mainloop()

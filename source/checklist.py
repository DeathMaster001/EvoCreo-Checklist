import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os

# Window properties
root = tk.Tk()
root.title("EvoCreo Offline Checklist")
root.configure(bg="lightblue")
root.geometry("800x600")
root.minsize(450, 300)
root['borderwidth'] = 5
root['relief'] = 'sunken'

# Top frame for buttons
top_frame = tk.Frame(root, bg="lightblue")
top_frame.pack(fill="x", padx=5, pady=5)


def check_all():
    for var in checkbox_vars.values():
        var.set(1)


def uncheck_all():
    for var in checkbox_vars.values():
        var.set(0)


tk.Button(top_frame, text="Check All",
          command=check_all).pack(side="left", padx=2)
tk.Button(top_frame, text="Uncheck All",
          command=uncheck_all).pack(side="left", padx=2)

row_frames = {}  # key: row_frame widget, value: creo_data
row_order = []   # list of row_frame in original order

# ===== Add filter entry =====
tk.Label(top_frame, text="Filter by Name:",
         bg="lightblue").pack(side="left", padx=5)
filter_var = tk.StringVar()
filter_entry = tk.Entry(top_frame, textvariable=filter_var)
filter_entry.pack(side="left", padx=5)

# ===== Filter function =====


def update_scrollregion():
    canvas.update_idletasks()  # make sure geometry updates
    canvas.configure(scrollregion=canvas.bbox("all"))


def apply_filter(*args):
    query = filter_var.get().lower()

    # Hide all first
    for row_frame in row_order:
        row_frame.pack_forget()

    # Repack in original order only if they match filter
    for row_frame in row_order:
        creo_data = row_frames[row_frame]
        if query in creo_data["name"].lower():
            row_frame.pack(fill="x", anchor="w", padx=5, pady=2)

    # ✅ Fix scrolling
    update_scrollregion()       # recalc scrollable area
    canvas.yview_moveto(0)      # scroll to top


filter_var.trace_add("write", apply_filter)

# ===== Functions for saving/loading checklist =====


def save_checklist():
    # Collect all checked Creos
    checked = {cid: True for cid, var in checkbox_vars.items()
               if var.get() == 1}

    save_path = os.path.join(script_dir, "checklist_save.json")
    with open(save_path, "w") as f:
        json.dump(checked, f, indent=2)

    # Show success popup
    messagebox.showinfo("Checklist Saved",
                        f"Saved {len(checked)} Creo(s) successfully!")


def load_checklist():
    save_path = os.path.join(script_dir, "checklist_save.json")
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            saved = json.load(f)
        for cid, var in checkbox_vars.items():
            var.set(1 if saved.get(cid) else 0)
        # Show success popup
        messagebox.showinfo("Checklist Loaded",
                            f"Loaded {len(saved)} Creo(s) successfully!")
    else:
        # Show warning if no save exists
        messagebox.showwarning(
            "No Save Found", "No saved checklist file was found.")


# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="Save Checklist", command=save_checklist)
file_menu.add_command(label="Load Checklist", command=load_checklist)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

checkbox_vars = {}  # key: creo_id, value: IntVar()

# Canvas + scrollbar
canvas = tk.Canvas(root, bg="lightblue")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="lightblue")

# Make the canvas scrollable
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def _on_mousewheel(event):
    if os.name == 'nt':  # Windows
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    elif os.name == 'darwin':  # macOS
        canvas.yview_scroll(-1 * int(event.delta), "units")
    else:  # Linux (event.num is used)
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")


# Windows / macOS
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Linux (scroll up / down)
canvas.bind_all("<Button-4>", _on_mousewheel)
canvas.bind_all("<Button-5>", _on_mousewheel)

# Get the dictionary of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Build the full path to creos.json
creos_path = os.path.join(script_dir, "creos1.json")

# Open the file and load the JSON data
with open(creos_path, "r") as f:
    creos = json.load(f)

# Store PhotoImage objects so they don't get garbage collected
images = {}

# Loop over all Creos
for creo_id, creo_data in creos.items():
    var = tk.IntVar()
    checkbox_vars[creo_id] = var  # store for later

    # Create a horizontal frame for this row
    row_frame = tk.Frame(scrollable_frame, bg="lightblue")
    row_frame.pack(fill="x", anchor="w", padx=5, pady=2)

    row_frames[row_frame] = creo_data
    row_order.append(row_frame)

    # 1️⃣ Checkbox
    chk = tk.Checkbutton(row_frame, variable=var, bg="lightblue")
    chk.pack(side="left")

    # 2️⃣ Number label
    tk.Label(row_frame, text=creo_id, width=4,
             bg="lightblue").pack(side="left", padx=2)

    # 3️⃣ Icon
    img_path = os.path.join(script_dir, creo_data["icon"])
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path)
        except Exception:
            img = Image.open(os.path.join(
                script_dir, "placeholder", "placeholder.png"))
    else:
        img = Image.open(os.path.join(
            script_dir, "placeholder", "placeholder.png"))

    photo = ImageTk.PhotoImage(img)
    images[creo_id] = photo  # keep reference
    tk.Label(row_frame, image=photo, bg="lightblue").pack(side="left", padx=2)

    # 4️⃣ Name label
    tk.Label(row_frame, text=creo_data["name"],
             bg="lightblue").pack(side="left", padx=5)

root.mainloop()

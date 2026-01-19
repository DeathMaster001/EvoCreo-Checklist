import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os

# ====== Window Setup ======
root = tk.Tk()
root.title("EvoCreo Offline Checklist")
root.configure(bg="lightblue")
root.geometry("800x600")
root.minsize(450, 300)
root['borderwidth'] = 5
root['relief'] = 'sunken'

# ====== Global Variables ======
checkbox_vars = {}
row_frames = {}
row_order = []
images = {}

# ====== Top Frame with Buttons & Filter ======
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

tk.Label(top_frame, text="Filter by Name:",
         bg="lightblue").pack(side="left", padx=5)
filter_var = tk.StringVar()
filter_entry = tk.Entry(top_frame, textvariable=filter_var)
filter_entry.pack(side="left", padx=5)

# ====== Metadata Label ======
tk.Label(root, text="Accurate as of Jan 18, 2026 | Source: In-game",
         bg="lightblue").pack(side="bottom", pady=5)

# ====== Canvas & Scrollbar Setup ======
canvas = tk.Canvas(root, bg="lightblue")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="lightblue")
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")


def update_scrollregion():
    canvas.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(event):
    if os.name == 'nt':  # Windows
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")
    elif os.name == 'darwin':  # macOS
        canvas.yview_scroll(-1 * int(event.delta), "units")
    else:  # Linux
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")


# Bind scrolling
canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", on_mousewheel)
canvas.bind_all("<Button-5>", on_mousewheel)

# ====== Helper Functions ======
script_dir = os.path.dirname(os.path.abspath(__file__))


def load_creos(path):
    with open(path, "r") as f:
        return json.load(f)


def create_creo_row(creo_id, creo_data):
    """Create a single row with checkbox, icon, ID, and name."""
    var = tk.IntVar()
    checkbox_vars[creo_id] = var

    frame = tk.Frame(scrollable_frame, bg="lightblue")
    frame.pack(fill="x", anchor="w", padx=5, pady=2)

    # Checkbox
    tk.Checkbutton(frame, variable=var, bg="lightblue").pack(side="left")
    # ID
    tk.Label(frame, text=creo_id, width=4,
             bg="lightblue").pack(side="left", padx=2)
    # Image
    img_path = os.path.join(script_dir, creo_data["icon"])
    if not os.path.exists(img_path):
        img_path = os.path.join(script_dir, "placeholder", "placeholder.png")
    try:
        img = Image.open(img_path)
    except Exception:
        img = Image.open(os.path.join(
            script_dir, "placeholder", "placeholder.png"))
    photo = ImageTk.PhotoImage(img)
    images[creo_id] = photo
    tk.Label(frame, image=photo, bg="lightblue").pack(side="left", padx=2)
    # Name
    tk.Label(frame, text=creo_data["name"],
             bg="lightblue").pack(side="left", padx=5)

    row_frames[frame] = creo_data
    row_order.append(frame)


def update_scrollbar():
    """Show/hide scrollbar based on currently visible rows."""
    update_scrollregion()
    visible_count = sum(1 for f in row_order if f.winfo_ismapped())

    if visible_count == 0 or (canvas.bbox("all") and canvas.bbox("all")[3] <= canvas.winfo_height()):
        scrollbar.pack_forget()
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")
    else:
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel)
        canvas.bind_all("<Button-5>", on_mousewheel)

# ====== Filtering ======


def apply_filter(*args):
    query = filter_var.get().lower()

    for frame in row_order:
        frame.pack_forget()

    for frame in row_order:
        if query in row_frames[frame]["name"].lower():
            frame.pack(fill="x", anchor="w", padx=5, pady=2)

    canvas.yview_moveto(0)
    update_scrollbar()


filter_var.trace_add("write", apply_filter)

# ====== Save / Load Checklist ======


def save_checklist():
    checked = {cid: True for cid, var in checkbox_vars.items()
               if var.get() == 1}
    save_path = os.path.join(script_dir, "checklist_save.json")
    with open(save_path, "w") as f:
        json.dump(checked, f, indent=2)
    messagebox.showinfo("Checklist Saved",
                        f"Saved {len(checked)} Creo(s) successfully!")


def load_checklist():
    save_path = os.path.join(script_dir, "checklist_save.json")
    if os.path.exists(save_path):
        with open(save_path, "r") as f:
            saved = json.load(f)
        for cid, var in checkbox_vars.items():
            var.set(1 if saved.get(cid) else 0)
        messagebox.showinfo("Checklist Loaded",
                            f"Loaded {len(saved)} Creo(s) successfully!")
    else:
        messagebox.showwarning(
            "No Save Found", "No saved checklist file was found.")


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

for creo_id, creo_data in creos.items():
    if creo_id == "metadata":
        continue  # skip metadata entry
    create_creo_row(creo_id, creo_data)


# ====== Initial scrollbar check ======
update_scrollbar()

root.mainloop()

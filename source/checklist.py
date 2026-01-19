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
images = {}

# Keep track of toggle state
toggle_seen = True  # True = next click will check all
toggle_caught = True


# ====== Top Frame with Buttons & Filter ======
top_frame = tk.Frame(root, bg="lightblue")
top_frame.pack(fill="x", padx=5, pady=5)


def toggle_all_seen():
    global toggle_seen
    for vars in checkbox_vars.values():
        vars["seen"].set(1 if toggle_seen else 0)
    toggle_seen = not toggle_seen  # flip for next click


def toggle_all_caught():
    global toggle_caught
    for vars in checkbox_vars.values():
        vars["caught"].set(1 if toggle_caught else 0)
    toggle_caught = not toggle_caught


tk.Label(top_frame, text="Filter by Name or ID:",
         bg="lightblue").pack(side="left", padx=5)
filter_var = tk.StringVar()
filter_entry = tk.Entry(top_frame, textvariable=filter_var)
filter_entry.pack(side="left", padx=5)

tk.Button(top_frame, text="Toggle All Seen",
          command=toggle_all_seen).pack(side="left", padx=2)
tk.Button(top_frame, text="Toggle All Caught",
          command=toggle_all_caught).pack(side="left", padx=2)

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


canvas.bind_all("<MouseWheel>", on_mousewheel)
canvas.bind_all("<Button-4>", on_mousewheel)
canvas.bind_all("<Button-5>", on_mousewheel)

# ====== Column Headers ======
headers = ["Seen", "Caught", "ID", "Icon", "Name"]
for col, text in enumerate(headers):
    tk.Label(scrollable_frame, text=text, font=("Segoe UI", 9, "bold"),
             bg="lightblue", width=12 if text == "Name" else 6
             ).grid(row=0, column=col, padx=5, pady=2, sticky="w")

# ====== Helper Functions ======
script_dir = os.path.dirname(os.path.abspath(__file__))


def load_creos(path):
    with open(path, "r") as f:
        return json.load(f)


def create_creo_row(creo_id, creo_data):
    seen_var = tk.IntVar()
    caught_var = tk.IntVar()
    checkbox_vars[creo_id] = {"seen": seen_var, "caught": caught_var}

    row = len(row_frames) + 1  # header is row 0
    widgets = []

    # Seen / Caught checkboxes
    w = tk.Checkbutton(scrollable_frame, variable=seen_var, bg="lightblue")
    w.grid(row=row, column=0)
    widgets.append(w)

    w = tk.Checkbutton(scrollable_frame, variable=caught_var, bg="lightblue")
    w.grid(row=row, column=1)
    widgets.append(w)

    # ID
    w = tk.Label(scrollable_frame, text=creo_id, width=4, bg="lightblue")
    w.grid(row=row, column=2, padx=2)
    widgets.append(w)

    # Icon (keep original size)
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
    w = tk.Label(scrollable_frame, text=creo_data.get(
        "name", ""), bg="lightblue", anchor="w")
    w.grid(row=row, column=4, sticky="w", padx=5)
    widgets.append(w)

    row_frames[creo_id] = {"seen_var": seen_var,
                           "caught_var": caught_var, "widgets": widgets}

# ====== Filtering ======


def apply_filter(*args):
    query = filter_var.get().lower()
    for cid, data in row_frames.items():
        # Check exact ID match OR partial name match
        if query == cid.lower() or query in creos[cid]["name"].lower():
            for w in data["widgets"]:
                w.grid()  # show
        else:
            for w in data["widgets"]:
                w.grid_remove()  # hide
    update_scrollregion()


filter_var.trace_add("write", apply_filter)

# ====== Save / Load Checklist ======


def save_checklist():
    checked = {
        cid: {
            "seen": vars["seen"].get(),
            "caught": vars["caught"].get()
        } for cid, vars in checkbox_vars.items()
    }
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
        for cid, vars in checkbox_vars.items():
            data = saved.get(cid, {})
            vars["seen"].set(data.get("seen", 0))
            vars["caught"].set(data.get("caught", 0))
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

for cid, data in creos.items():
    if cid == "metadata":
        continue
    create_creo_row(cid, data)

# ====== Initial scrollbar check ======
update_scrollregion()

root.mainloop()

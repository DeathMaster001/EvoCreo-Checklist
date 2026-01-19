# EvoCreo Checklist

A simple offline checklist app for EvoCreo to track **Seen** and **Caught** Creos.  
Works completely offline and allows filtering, auto-updating Seen/Caught statuses, and saving/loading your progress.

---

## ✨ Features

- View all Creos with icons, ID, and names in a **scrollable, centered table**.
- **Filter Creos by Name or ID** (exact match for ID).
- **Seen Only** and **Caught Only** checkboxes to filter your checklist.
- **Auto-update**: marking a Creo as caught automatically marks it as seen.
- **Check All / Uncheck All** buttons for Seen and Caught statuses.
- Save and load your checklist to a local JSON file.
- Full mouse scrolling support.

---

## 🛠 Installation

1. Make sure you have **Python 3** installed.
2. Install dependencies:
```bash
pip install pillow
```

3. Clone the repository:
```bash
git clone https://github.com/yourusername/evocreo-checklist.git
cd evocreo-checklist
```

---

## ▶️ Usage

Run the checklist app with:

```bash
python source/checklist.py
```
- Use the Filter box to search for Creos by ID (exact match) or Name (partial match).
- Toggle Seen Only / Caught Only checkboxes to filter your list.
- Use Check All / Uncheck All buttons to mark multiple Creos at once.
- Save progress via File → Save Checklist.
- Load saved progress via File → Load Checklist.

---

## 💡 Tips

- Typing a Creo ID in the filter box shows only that ID (exact match).
- Seen Only shows Creos marked as Seen but not Caught.
- Caught Only shows only Creos that have been caught.
- Clicking Check All Caught automatically checks Seen for those Creos.  
Seen checkboxes are disabled while Caught is checked.

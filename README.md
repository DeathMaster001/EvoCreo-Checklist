# EvoCreo Checklist

A simple offline checklist app for EvoCreo to track **Seen**, **Caught**, **GM**, and **Shiny** Creos.  
Works completely offline and allows filtering, auto-updating statuses, and saving/loading your progress.

![EvoCreo-Checklist window](https://i.imgur.com/NZOSckD.png)

---

## ✨ Features

- View all Creos with icons, ID, and names in a **scrollable, centered table**.
- **Filter Creos by Name, ID, GM, or Shiny** (exact match for ID).
- **Seen Only / Caught Only / GM / Shiny** filters, plus “Not Seen / Not Caught / Not GM / Not Shiny”.
- **Auto-update**:
  - Catching a Creo automatically marks it as Seen.
  - GM checkboxes automatically mark Seen and Caught and lock both.
  - Shiny checkboxes automatically mark Seen; Caught remains editable.
- **Check All / Uncheck All** buttons for Seen, Caught, GM, and Shiny statuses.
- **Stats window** (Edit → Open Stats) shows totals for Seen, Caught, GM, and Shiny, with congratulatory messages for completion.
- Save and load your checklist to a local JSON file.
- Full mouse scrolling support across Windows, Mac, and Linux.

---

## 🛠 Installation

1. Make sure you have **Python 3** installed.
2. Install dependencies:
```bash
pip install pillow
```

3. Clone the repository:
```bash
git clone https://github.com/DeathMaster001/evocreo-checklist.git
cd evocreo-checklist
```

---

## ▶️ Usage

Run the checklist app with:

```bash
python source/checklist.py
```
- Use the Filter box to search for Creos by ID (exact match) or Name (partial match).
- Toggle Seen Only, Caught Only, GM, or Shiny checkboxes to filter your list.
- Use “Not Seen / Not Caught / Not GM / Not Shiny” checkboxes for reverse filters.
- Use Check All / Uncheck All buttons to mark multiple Creos at once.
- Open Stats window via Edit → Open Stats to view totals and completion messages.
- Clear all checkboxes via File → Clear Checklist.
- Open saved progress via File → Open.
- Save progress via File → Save.

---

## 💡 Tips

- Typing a Creo ID in the filter box shows only that ID (exact match).
- Seen Only shows Creos marked as Seen but not Caught.
- Caught Only shows only Creos that have been caught; this automatically locks Seen checkboxes.
- GM checkboxes lock both Seen and Caught.
- Shiny checkboxes lock only Seen; Caught can still be changed manually.

---
## Disclaimer

This is an unofficial, fan-made EvoCreo tool.  
Not affiliated with or endorsed by Ilmfinity or EvoCreo.  
All game assets belong to their respective owners.

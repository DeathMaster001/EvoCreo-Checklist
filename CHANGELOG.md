# Changelog

## [1.2.0] - 2026-01-30
### Added
- **GM and Shiny support**
  - Separate checkboxes for GM (Genetically Modified) and Shiny Creos.
  - GM checkboxes automatically mark Seen and Caught and lock both to prevent accidental changes.
  - Shiny checkboxes automatically mark Seen; Caught remains editable.

- **Expanded filters**
  - Added filtering options for GM and Shiny, as well as “Not Seen / Not Caught / Not GM / Not Shiny”.
  - Filters can now be combined with existing Seen / Caught filters for precise searches.

- **Checklist Stats window**
  - New Stats window accessible from the Edit menu.
  - Displays totals for Seen, Caught, GM, and Shiny.
  - Shows congratulatory messages when all Creos in a category are completed.

- **UI Improvements**
  - Checkbox rows now include ID, Name, Icon, Seen, Caught, GM, and Shiny.
  - Info label updated to explain the new locking behavior for GM and Shiny.
  - Centered and reorganized filter and checkbox layout for clarity.

- **Save / Load Enhancements**
  - GM and Shiny states are now saved and loaded properly.
  - Loading older checklists automatically adds GM and Shiny fields if missing.

### Fixed / Improved
- All checkbox toggles (Check All / Uncheck All) now correctly respect GM and Shiny locking rules.
- Improved auto-centering of the scrollable table.
- Mouse wheel scrolling works consistently across Windows, Mac, and Linux.

## [1.1.0] - 2026-01-21
### Added
- Clicking a Creo’s name now opens its corresponding EvoCreo fandom wiki page.

## [1.0.1] - 2026-01-19
### Fixed / Improved
- Added Windows file dialogs for **Save Checklist** and **Load Checklist**.
- Prevents losing progress when running the standalone `.exe`.
- Ensures users can choose where to save/load their checklist.

## [1.0.0] - 2026-01-19
### Added
- Initial release of **EvoCreo Checklist**.
- Track **Seen** and **Caught** Creos offline.
- View all Creos with icons, ID, and names in a **scrollable, centered table**.
- Filter Creos by Name or ID (exact match for ID).
- **Seen Only** and **Caught Only** checkboxes to filter the list.
- **Check All / Uncheck All** buttons for Seen and Caught statuses.
- Save and load checklist to a local JSON file.
- Full mouse scrolling support.

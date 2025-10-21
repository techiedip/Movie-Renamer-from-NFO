# 🎬 Rename from NFO

**rename_from_nfo.py** is a cross-platform Python automation tool that scans movie folders, reads movie titles from corresponding `.nfo` files, and renames the matching movie files with clean, human-readable titles.

It replaces or removes special characters, ensures filenames are filesystem-safe, and provides dry-run and confirmation options to keep your library tidy and consistent.

---

## 🧩 Features

- Automatically extracts movie titles from `.nfo` files.
- Renames corresponding video files (same basename) with the full title.
- Replaces `:` with `-` and strips unwanted special characters.
- Handles XML-style and plain-text `.nfo` formats.
- Supports recursive scanning of nested folders.
- Safe **dry-run** mode for testing before renaming.
- Automatically resolves filename collisions by appending `(1)`, `(2)`, etc.
- Cross-platform (works on macOS, Windows, and Linux).

---

## ⚙️ Requirements

- **Python 3.8+**
- Works with standard libraries (no external dependencies).

---

## 🚀 How to Use

### 1️⃣ Save the script
Save the following Python file as:

```
rename_from_nfo.py
```

in your desired location.

### 2️⃣ Run a dry run
Run this command to preview what will happen without making changes:

```bash
python3 rename_from_nfo.py /path/to/movies --recursive --dry-run
```

This scans the given folder (and all subfolders) for `.nfo` files and lists the rename operations that would occur.

### 3️⃣ Perform renaming (interactive confirmation)
Once you're satisfied with the preview:

```bash
python3 rename_from_nfo.py /path/to/movies --recursive
```

You’ll be prompted for confirmation before renaming files.

### 4️⃣ Perform renaming without confirmation (unsafe mode)
Use this only if you’re sure:

```bash
python3 rename_from_nfo.py /path/to/movies --recursive --yes
```

---

## 🧠 Notes & Safeguards

- ✅ **Dry Run Mode:** Use `--dry-run` to preview changes before renaming.
- ✅ **Extension Safety:** The script preserves movie file extensions (`.mkv`, `.mp4`, `.avi`, etc.).
- ✅ **Collision Handling:** If a target filename already exists, it will append `(1)`, `(2)`, etc.
- ✅ **Recursive Scan:** Use `--recursive` to process all subfolders.
- ✅ **Encoding Safe:** Reads `.nfo` files using UTF-8 (with fallback to ISO-8859-1).
- ⚠️ **Backups Recommended:** Always back up your collection before bulk renames.
- ⚠️ **Sanitization Rules:**
  - Replaces `:` → `-`
  - Removes non-alphanumeric characters (except spaces, `-`, `_`, `.`, `(`, `)`, `[`, `]`)
  - Collapses multiple spaces into one
- ⚠️ **File Matching:** Matches movie files by basename (case-insensitive, punctuation ignored).
  Example:  
  `My.Movie.2020.nfo` will rename `My_Movie_2020.mkv`.

---

## 🧰 Example

Suppose you have:

```
Movies/
├── Inception (2010).nfo
├── Inception (2010).mkv
├── Interstellar.nfo
└── Interstellar.mp4
```

Running:

```bash
python3 rename_from_nfo.py Movies --recursive --dry-run
```

Might output:

```
Planned actions (2):
  Inception (2010).mkv  ->  Inception.mkv  (from NFO: Inception (2010).nfo | raw title: Inception)
  Interstellar.mp4  ->  Interstellar.mkv  (from NFO: Interstellar.nfo | raw title: Interstellar)
```

Then, run again without `--dry-run` to actually rename.

---

## 🧱 Advanced Usage

| Flag | Description |
|------|--------------|
| `--recursive` / `-r` | Scan folders recursively |
| `--dry-run` / `-n` | Preview changes without renaming |
| `--yes` / `-y` | Skip confirmation prompt |
| `--help` | Show command help |

---

## 🖋️ Example Output

```
[OK] Renamed: My.Movie.2020.mkv -> The Great Movie.mkv
[WARN] Could not extract title from BrokenFile.nfo
[SKIP] File already has desired name.
```

---

## 💡 Tips

- Add more extensions to the `MOVIE_EXTS` set inside the script if you use uncommon formats.
- You can combine this script with tools like **MediaElch** or **TinyMediaManager** that generate `.nfo` files for a cleaner workflow.
- Works great with media servers like **Kodi**, **Plex**, or **Jellyfin** to maintain consistent naming conventions.

---

## 🧾 License

This script is released under the MIT License.  
You are free to use, modify, and distribute it — attribution appreciated but not required.

---

## 🪶 Author’s Note

This tool was made to simplify the often messy process of organizing movie collections where `.nfo` metadata files already contain the right titles. It ensures your media library stays clean, searchable, and consistent — without breaking links or metadata integrity.

---

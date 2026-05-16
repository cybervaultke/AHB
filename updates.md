# AHB Script Updates & Documentation

## [2026-05-16] - Security & Firebase Integration

### Added
- **Firebase Authentication:** Moved key validation from hardcoded hashes to a secure Firebase Realtime Database.
- **Subscription Expiry:** Keys now have expiry dates (7, 15, or 30 days) tracked in Firebase.
- **Admin Management:** Added `admin.py` for managing keys and setting expiry durations.
- **Global Exit:** Added `/exit` command functionality to all inputs.
- **Ctrl+C Handling:** Pressing `Ctrl+C` now returns the user to the main menu instead of crashing.
- **Automatic Updates:** Script now checks for new versions via GitHub and provides re-clone instructions.

### Changed
- **Persistence:** Removed key persistence (access key is required on every run).
- **Task Persistence:** Task completion (YouTube/WhatsApp) is now stored in `.ahb_data.json`.
- **Security:** Critical credentials (`serviceAccountKey.json`) must be managed locally and **NEVER** pushed to GitHub.

---

## 🔒 Security Policy
**NEVER PUSH `serviceAccountKey.json` TO GITHUB.**
This file contains sensitive Firebase credentials. It is listed in the project's `.gitignore` and must remain local to your deployment environment. If accidentally pushed, revoke the credentials in the Firebase Console immediately.

---

## 🛠 Admin Management
To approve a user, use the `admin.py` script:
```bash
python3 admin.py
```
This script will prompt you for the key, the owner's name, and the duration (7, 15, or 30 days) to automatically calculate the expiry date in Firebase.

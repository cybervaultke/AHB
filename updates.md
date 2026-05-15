# AHB Script Updates & Documentation

## [2024-05-16] - Multi-Layer Security and Task Integration

### Added
- **3-Level Key Encryption:** Implemented a robust multi-layer encryption scheme (Base64 -> MD5 -> SHA256) for approval keys.
- **Mandatory Task Menu:** Persistent task completion system. Users must confirm YouTube and WhatsApp tasks to unlock the key entry.
- **Persistent Session Storage:** `.ahb_data.json` stores task progress and the approved key.

### Changed
- **Removed Shell Redirects:** Eliminated `xdg-open` and `am start` for a non-intrusive experience.
- **Improved UI Navigation:** Replaced `os.system('clear')` with ANSI escape codes.
- **Fixed Initialization Crash:** Corrected the order of `install_missing()` and fixed its implementation.

---

## 🔑 Key Generation Guide (3-Level Encryption)

To generate a valid hash for an approval key, follow these three steps in sequence:

1.  **Level 1: Base64 Encoding**
    - Take the plain text key (e.g., `ALI-12345`).
    - Convert it to a Base64 string.
    - *Result for ALI-12345:* `QUxJLTEyMzQ1`

2.  **Level 2: MD5 Hashing**
    - Take the Base64 string from Step 1.
    - Calculate its MD5 hash (hex format).
    - *Result for QUxJLTEyMzQ1:* `983c276a605f63d0387a2d480877992a`

3.  **Level 3: SHA256 Hashing**
    - Take the MD5 hex string from Step 2.
    - Calculate its SHA256 hash (hex format).
    - *Final Hash for ALI-12345:* `a688efe698e43127fe85f5c0c7777d45cbee8203ddfae0c598617c1a96ae46ef`

### Verified Active Hashes:
- **ALI-12345:** `a688efe698e43127fe85f5c0c7777d45cbee8203ddfae0c598617c1a96ae46ef`
- **GM-2025:** `8052a8f347ef4ed171ed168fc611ed72dc195f600003f6790b0b037ea4d0e832`
- **VIP-786:** `1fbaddfd357c8fcf522c2012d294f04a826a109807d51c719681d5ec6f669eb3`

---

## 🛠 Troubleshooting
If the CLI crashes or keys are marked invalid:
1. Ensure `base64` is imported in your environment.
2. Check if `.ahb_data.json` is corrupted (delete it to reset).
3. Verify that all tasks are marked as complete (✅) in the menu.

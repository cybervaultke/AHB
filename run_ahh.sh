#!/usr/bin/env bash
# Decrypt ahh.enc and execute the original Python script.
# Usage: ./run_ahh.sh <password>

if [[ -z "$1" ]]; then
  echo "Usage: $0 <password>"
  exit 1
fi

PASSWORD="$1"
ENC_FILE="ahh.enc"
TMP_PY="./ahh_decrypted.py"

# Remove previous decrypted file if exists
[[ -f "$TMP_PY" ]] && rm -f "$TMP_PY"

# Decrypt the file
openssl enc -aes-256-cbc -d -in "$ENC_FILE" -out "$TMP_PY" -k "$PASSWORD"
DECRYPT_STATUS=$?
if [[ $DECRYPT_STATUS -ne 0 ]]; then
  echo "Decryption failed"
  # Open WhatsApp to request password (replace with appropriate link)
  termux-open "https://wa.me/+923052962654?text=Please%20provide%20the%20decryption%20password"
  exit 1
fi

# Execute the decrypted script
python3 "$TMP_PY"
# Success message
echo "AHB tool launched successfully!"

# Clean up
rm -f "$TMP_PY"

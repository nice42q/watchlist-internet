import requests
import json
import os
import re
import sys
import hashlib
from datetime import datetime

CSV_URL = "https://www.watchlist-internet.at/liste-betruegerischer-shops/csv/"
DEBUG_DIR = "debug"
RAW_CSV_PATH = os.path.join(DEBUG_DIR, "watchlist.csv")
BLACKLIST_TXT_PATH = os.path.join(DEBUG_DIR, "blacklist.txt")

# Array for local runtime logs
process_logs = []


def log(level, message):
    formatted_msg = f"{level:<9} {message}"
    print(formatted_msg)
    process_logs.append(formatted_msg)


def clean_domain(raw_string):
    s = raw_string.strip(' \t\n\r"').lower()
    s = re.sub(r"^https?://", "", s)
    s = s.split('/')[0]
    s = s.strip(' \t\n\r"')
    
    if s.startswith("www."):
        s = s[4:]
        
    if "." in s and " " not in s:
        if re.match(r"^([0-9]{1,3}\.){3}[0-9]{1,3}$", s):
            return None
            
        try:
            punycode_domain = s.encode("idna").decode("ascii")
            if re.fullmatch(r"^(?:[a-z0-9-]+\.)+[a-z]{2,}$", punycode_domain):
                return punycode_domain
            else:
                return None
        except Exception:
            return None
            
    return None


def main():
    log("[SYSTEM]", "Pipeline execution triggered.")
    log("[SYSTEM]", "Starting fetch of the Watchlist Internet database...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(CSV_URL, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        log("[ERROR]", f"Connection failed: {e}")
        sys.exit(1)

    os.makedirs(DEBUG_DIR, exist_ok=True)

    new_csv_bytes = response.content
    new_hash = hashlib.sha256(new_csv_bytes).hexdigest()

    if os.path.exists(RAW_CSV_PATH):
        with open(RAW_CSV_PATH, "rb") as f:
            old_hash = hashlib.sha256(f.read()).hexdigest()
        
        if new_hash == old_hash:
            log("[SUCCESS]", "Integrity check: No updates on source page. Local blocklist is up-to-date.")
            sys.exit(0)

    log("[SYSTEM]", "Delta detected or baseline assets missing. Parsing remote database...")

    lines = response.text.splitlines()
    
    seen_domains = set()
    valid_domains = []
    invalid_entries = []
    duplicate_entries = []

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        if ";" in line_stripped:
            raw_entry = line_stripped.split(";")[0]
            cleaned = clean_domain(raw_entry)
            
            if cleaned:
                if cleaned in seen_domains:
                    duplicate_entries.append(cleaned)
                else:
                    seen_domains.add(cleaned)
                    valid_domains.append(cleaned)
            else:
                raw_cleaned = raw_entry.strip(' \t\n\r"')
                if raw_cleaned and raw_cleaned not in ["shopname", "domain/muster"]: 
                    invalid_entries.append(raw_cleaned)
        else:
            raw_cleaned = line_stripped.strip(' \t\n\r"')
            if raw_cleaned:
                invalid_entries.append(raw_cleaned)

    if not valid_domains:
        log("[ERROR]", "Empty list protection triggered: 0 valid domains found. Aborting.")
        sys.exit(1)

    valid_domains = sorted(valid_domains)
    duplicate_entries = sorted(duplicate_entries)
    invalid_entries = sorted(invalid_entries)

    log("[STATS]", f"Total entries parsed:     {len(lines)}")
    log("[STATS]", f"Invalid lines filtered:   {len(invalid_entries)}")
    log("[STATS]", f"Duplicate lines removed:  {len(duplicate_entries)}")
    log("[STATS]", f"Valid, unique domains:    {len(valid_domains)}")

    log("[SYSTEM]", "Writing all updated blocklist files...")
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. AdBlock format (blocklist.txt) with full metadata header
    with open("blocklist.txt", "w", encoding="utf-8") as f:
        f.write("[Adblock Plus 2.0]\n")
        f.write("# Pi-hole DNS Blocklist: Watchlist Internet\n")
        f.write(f"# Source: {CSV_URL}\n")
        f.write("# Pi-hole Source: https://github.com/nice42q/watchlist-internet\n")
        f.write(f"# Last update: {now}\n")
        f.write("#\n")
        f.write("# --- Analysis statistics for this update ---\n")
        f.write(f"# Total valid domains:       {len(valid_domains)}\n")
        f.write(f"# Duplicate entries removed: {len(duplicate_entries)}\n")
        f.write(f"# Invalid lines filtered:    {len(invalid_entries)}\n")
        f.write(f"# {'-'*43}\n#\n")
        for d in valid_domains:
            f.write(f"||{d}^\n")

    # 2. Hosts format (blocklist-hosts.txt)
    with open("blocklist-hosts.txt", "w", encoding="utf-8") as f:
        f.write("# Watchlist Internet Blocklist – Hosts Format\n")
        for d in valid_domains:
            f.write(f"0.0.0.0 {d}\n")

    # 3. Plain domain list (blocklist-domains.txt)
    with open("blocklist-domains.txt", "w", encoding="utf-8") as f:
        for d in valid_domains:
            f.write(f"{d}\n")

    # 4. Save Raw CSV for future hashing cycles
    with open(RAW_CSV_PATH, "wb") as f:
        f.write(new_csv_bytes)

    # 5. Write enhanced Debug Report (debug/blacklist.txt)
    log("[SYSTEM]", f"Writing enhanced debug report to {BLACKLIST_TXT_PATH}...")
    with open(BLACKLIST_TXT_PATH, "w", encoding="utf-8") as f:
        f.write(f"# {'='*78}\n")
        f.write(f"# WATCHLIST INTERNET BLACKLIST – REPORT & DEBUG LOG\n")
        f.write(f"# {'='*78}\n#\n")
        
        f.write(f"# -- RUNTIME PROCESS LOG --\n")
        for log_line in process_logs:
            f.write(f"# {log_line}\n")
        f.write("#\n")

        f.write(f"# {'-'*78}\n")
        f.write(f"# REMOVED DUPLICATE ENTRIES ({len(duplicate_entries)})\n")
        f.write(f"# These domains were present multiple times within the source CSV list.\n")
        f.write(f"# {'-'*78}\n")
        if duplicate_entries:
            for entry in duplicate_entries:
                f.write(f"{entry}\n")
        else:
            f.write("# (no duplicates found)\n")

        f.write(f"# {'-'*78}\n")
        f.write(f"# FILTERED INVALID ENTRIES ({len(invalid_entries)})\n")
        f.write(f"# These entries did not match a valid domain schema.\n")
        f.write(f"# {'-'*78}\n")
        if invalid_entries:
            for entry in invalid_entries:
                f.write(f"{entry}\n")
        else:
            f.write("# (no invalid entries found)\n")

    # 6. Write Stats Schema JSON for GitHub Shields Badge
    stats = {
        "schemaVersion": 1,
        "label": "Blocklist entries",
        "message": f"{len(valid_domains)}",
        "color": "red"
    }
    with open("stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4)

    log("[SUCCESS]", "All pipeline assets compiled and saved successfully!")


if __name__ == "__main__":
    main()

# 🛡️ Watchlist Internet Blocklist for Pi‑hole

>[!NOTE]
> **Missing a fake shop?** If you come across a fraudulent online shop, phishing site, or subscription trap, you can report it directly on the [Watchlist Internet Reporting Form](https://www.watchlist-internet.at/melde-formular/) so it can be added to the source list and automatically included here.

[![Update Blocklist](https://github.com/nice42q/watchlist-internet/actions/workflows/update_blocklist.yml/badge.svg)](https://github.com/nice42q/watchlist-internet/actions)
![GitHub Last Commit](https://img.shields.io/github/last-commit/nice42q/watchlist-internet?label=Last%20update&color=blue)
![Blocklist entries](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/nice42q/watchlist-internet/main/stats.json)

This repository provides an automatically updated DNS blocklist in three formats, containing fake shop domains collected from the official [Watchlist Internet](https://www.watchlist-internet.at/) database:

| File | Format | Typical use |
|------|--------|-------------|
| **[`blocklist.txt`](https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist.txt)** | **AdBlock (`\|\|domain^`)** | **Pi‑hole, uBlock Origin, Adblock Plus, Brave** |
| [`blocklist-hosts.txt`](https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist-hosts.txt) | Hosts (`0.0.0.0 domain`) | Pi‑hole, AdGuard Home, `/etc/hosts`, Diversion |
| [`blocklist-domains.txt`](https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist-domains.txt) | Plain domains | AdGuard Home, custom scripts |

All files are regenerated every 6 hours and only updated if the upstream list changes. An integrity check prevents publishing an empty list.

## 🚀 How to use in Pi-hole

1. Go to your Pi-hole admin dashboard.
2. Navigate to **Adlists** (*Group Management → Adlists*).
3. Paste **one** of the following URLs into the **Address** field:
   - AdBlock format (recommended):  
     `https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist.txt`
   - Hosts format:  
     `https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist-hosts.txt`
4. Click **Add blocklist**.
5. **Update** your gravity list (*Tools → Update Gravity* → **Update** or run `pihole -g`).

## 🏠 Compatible with AdGuard Home

Both the AdBlock list and the plain domain list work with **AdGuard Home**.

1. Go to your AdGuard Home dashboard → **Filters** → **DNS blocklists**.
2. Click **Add blocklist** → **Add a custom list**.
3. Enter a name (e.g., "Watchlist Internet Fakeshops") and one of these URLs:
   - `https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist.txt` (AdBlock)
   - `https://raw.githubusercontent.com/nice42q/watchlist-internet/main/blocklist-domains.txt` (plain domains)
4. Click **Save**.

## 🔄 Automation & Safety

The workflow runs every 6 hours at 24 minutes past the hour **(00:24, 06:24, 12:24, 18:24 UTC)**.  
`cron: '24 */6 * * *'`

**Built-in protections:**
- If the fetched list contains **0 valid domains**, the pipeline **stops with an error** and no files are updated. This prevents an empty blocklist from being distributed.
- Subdomains (`www.`), protocols (`https://`), and URL paths are automatically cleaned.
- Duplicate entries and invalid domains are filtered out automatically.

A failed run is visible in the [Actions tab](https://github.com/nice42q/watchlist-internet/actions) and will never overwrite the existing blocklist.

## ⚠️ Disclaimer & False Positives

This is an unofficial project and is not affiliated with, maintained by, or endorsed by Watchlist Internet.  
The script and the generated blocklists are provided **as-is** – without any warranty.

* **False Positives:** If a legitimate domain is blocked, please note that this repository automatically mirrors the data provided by Watchlist Internet. Please contact them directly or whitelist the domain locally in your Pi-hole / AdGuard Home.
* **Scraper Issues:** If the blocklist is empty or the format breaks, please [open an issue](https://github.com/nice42q/watchlist-internet/issues) here on GitHub.

## 📜 License

The code in this repository is open-source. However, the original domain data comes from [watchlist-internet.at](https://www.watchlist-internet.at/). Please respect their terms of use.

## 🙏 Acknowledgements

* **Watchlist Internet** for maintaining the crucial fake shop and phishing database.
* The **Pi‑hole community** for the great blocking ecosystem.

**Happy scam‑free browsing!** 🛡️

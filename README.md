# iden8.py - Product Data Scraper

A Playwright-based Python script that automates login to the Iden hiring challenge website, navigates to the Product Catalog, and extracts product data from an infinite scroll table.

## Overview

This script performs the following operations:
1. **Authentication**: Logs into `https://hiring.idenhq.com/` using provided credentials
2. **Session Management**: Saves and reuses browser storage state to avoid repeated logins
3. **Navigation**: Steps through the UI menu to reach the Product Catalog
4. **Data Extraction**: Scrolls through an infinite table and extracts product information
5. **Data Output**: Writes product data to a JSON Lines file (`data/products.json`)

## Prerequisites

- Python 3.7+
- [Playwright](https://playwright.dev/python/) (`pip install playwright`)
- Playwright browsers installed (`playwright install chromium`)
- Brave Browser installed at `/usr/bin/brave-browser` (or modify `executable_path` in code)

## Installation

```bash
pip install playwright
playwright install chromium
```

## Configuration

### Credentials

The script uses the following default credentials (can be overridden via environment variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `USER_NAME` | `jjeyaprakash58@gmail.com` | Login email |
| `PASSWORD` | `MKYqT1k4` | Login password |

To override:
```bash
export USER_NAME="your-email@example.com"
export PASSWORD="your-password"
```

### Other Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADLESS` | `False` | Run browser in headless mode |
| `STORAGE_STATE` | `data/Storage_state.json` | Path to save browser session |
| `OUTPUT_FILE` | `data/products.json` | Path to output JSON file |

## Usage

```bash
python iden.py
```

## Output

The script creates `data/products.json` with one JSON object per line:

```json
{"id": "1", "name": "Product Name", "price": "$99.99", "manufacturer": "Brand", "category": "Category", "last_updated": "2024-01-01", "size": "M", "color": "Blue", "sku": "SKU123"}
```

### Extracted Fields

| Field | Description |
|-------|-------------|
| `id` | Product unique identifier |
| `name` | Product name |
| `price` | Product price |
| `manufacturer` | Manufacturer name |
| `category` | Product category |
| `last_updated` | Last update timestamp |
| `size` | Product size |
| `color` | Product color |
| `sku` | Stock Keeping Unit |

## How It Works

1. **Session Validation**: Checks if existing storage state is still valid by visiting the challenge URL
2. **Login Flow**: If no valid session, performs login with multiple selector fallbacks for email, password, and submit button
3. **Menu Navigation**: Clicks through the menu hierarchy:
   - Launch Challenge → Menu → Data Tools → Inventory Management → Product Catalog → Load Product Data
4. **Data Extraction**:
   - Scrolls through infinite table (up to 250 scrolls)
   - Detects when no new data is loaded (5 consecutive stable scrolls)
   - Extracts product details from table cells

## Error Handling

- Multiple selector fallbacks for login fields to handle UI changes
- Timeout handling for page navigation and element detection
- Session invalidation detection to trigger re-login

## Notes

- The script uses Brave Browser by default. Change `executable_path` in `main()` to use a different browser
- `slow_mo=500` adds a 500ms delay between actions for stability
- Output is appended to the file (use `open(OUTPUT_FILE, "a")`) - delete the file before re-running if needed

- The script extracts the data as long as it generates and we can modify it by extracting the exact value and do that much iterations (ex:3223). currently i used only 250 scrolls


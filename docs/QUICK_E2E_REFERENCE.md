# 🚀 Quick E2E Testing Reference

## Start Testing Now

```bash
cd /workspaces/Go_explorer_clear
./test_everything.sh
```

**That's it!** Everything will run automatically.

---

## Commands Cheat Sheet

### Run All Tests (Recommended)
```bash
./test_everything.sh
```
- Starts Django server
- Runs E2E tests
- Generates screenshots, video, report

### Run Tests Only (Server already running)
```bash
./run_e2e_tests.sh
```

### Run Tests Directly
```bash
python tests/ui_e2e_playwright.py
```

### Start Server Only
```bash
python manage.py runserver 0.0.0.0:8000
```

### Stop Server
```bash
pkill -f "manage.py runserver"
```

---

## View Test Results

### List All Artifacts
```bash
ls -lh tmp/
```

### View Screenshots
```bash
ls -lh tmp/ui-*.png
```

### Watch Video
```bash
ffplay tmp/*.webm        # Using ffmpeg
vlc tmp/*.webm           # Using VLC
```

### Check Report
```bash
cat tmp/test_report.txt
```

### View Latest Results
```bash
cat tmp/LATEST_TEST_RESULTS.md
```

---

## What Gets Generated

| File | Size | What It Is |
|------|------|-----------|
| `ui-home.png` | 864 KB | Home page screenshot |
| `ui-hotels.png` | 1.2 MB | Hotels listing |
| `ui-hotel-detail.png` | 1.2 MB | Hotel detail & form |
| `ui-buses.png` | 580 KB | Buses page |
| `ui-packages.png` | 994 KB | Packages page |
| `[UUID].webm` | 405 KB | Complete video |
| `test_report.txt` | 352 B | Test log |

---

## Troubleshooting

### Server not starting?
```bash
# Check if port 8000 is free
lsof -i :8000

# Check server logs
tail -f /tmp/server.log
```

### Playwright not found?
```bash
pip install playwright
playwright install chromium
```

### Permission denied?
```bash
chmod +x run_e2e_tests.sh test_everything.sh
```

### Need to clean test artifacts?
```bash
rm -rf tmp/
```

---

## Configuration

### Use Different Server URL
```bash
BASE_URL=http://example.com ./run_e2e_tests.sh
```

### Keep Old Test Results
```bash
./run_e2e_tests.sh --no-cleanup
```

### Check Django Server
```bash
curl -I http://localhost:8000/
```

---

## Documentation

- **[E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md)** - Full setup & advanced topics
- **[E2E_SETUP_COMPLETE.md](./E2E_SETUP_COMPLETE.md)** - Complete feature overview
- **[tmp/LATEST_TEST_RESULTS.md](./tmp/LATEST_TEST_RESULTS.md)** - Latest test details

---

## Key Features

✅ Automatic tmp/ cleanup  
✅ No leftover test data  
✅ Screenshots of each flow  
✅ Video recording  
✅ Detailed reports  
✅ Error handling  
✅ Easy to use  

---

## Test Coverage

- ✅ Home page
- ✅ Hotels listing
- ✅ Hotel details
- ✅ Booking form
- ✅ Buses page
- ✅ Packages page

---

## Duration

Total test time: **~30 seconds**

---

## Status

Current: **✅ ALL TESTS PASSING**

Last Run: **2026-01-06**

---

## Questions?

1. Check [E2E_TESTING_GUIDE.md](./E2E_TESTING_GUIDE.md)
2. Review test code: [tests/ui_e2e_playwright.py](./tests/ui_e2e_playwright.py)
3. Check latest results: [tmp/LATEST_TEST_RESULTS.md](./tmp/LATEST_TEST_RESULTS.md)

---

**Ready?** Just run: `./test_everything.sh` 🚀

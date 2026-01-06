# E2E Testing with Playwright

This guide explains how to run end-to-end (E2E) tests for the Go Explorer platform using Playwright.

## 📋 Overview

The E2E test suite automatically:
- ✅ Tests the home page
- ✅ Tests hotels listing and detail pages
- ✅ Attempts hotel booking form interactions
- ✅ Tests buses page
- ✅ Tests packages page
- 📸 Captures full-page screenshots of each flow
- 🎬 Records a video of the entire test session
- 📝 Generates a detailed test report

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Playwright and browser binaries
pip install playwright
playwright install chromium
```

### 2. Start Django Server

```bash
# Make sure you're in the project root
cd /workspaces/Go_explorer_clear

# Start the server (if not already running)
python manage.py runserver 0.0.0.0:8000
```

### 3. Run the E2E Tests

**Option A: Using the convenience script (Recommended)**

```bash
./run_e2e_tests.sh
```

**Option B: Direct Python execution**

```bash
python tests/ui_e2e_playwright.py
```

## 📊 Test Results

After running tests, check the `tmp/` folder for:

### Screenshots
- `ui-home.png` - Home page
- `ui-hotels.png` - Hotels listing page
- `ui-hotel-detail.png` - Hotel detail page
- `ui-buses.png` - Buses page
- `ui-packages.png` - Packages page

### Video Recording
- `*.webm` - Complete test session video (WebM format)

### Test Report
- `test_report.txt` - Detailed test execution log with all actions and results

## 🔧 Configuration

### Custom Server URL

```bash
# Using the script
./run_e2e_tests.sh --url=http://example.com

# Using environment variable
BASE_URL=http://example.com python tests/ui_e2e_playwright.py
```

### Clean Up Before Tests

The test suite automatically cleans up the `tmp/` folder before each run. To keep previous test artifacts:

```bash
./run_e2e_tests.sh --no-cleanup
```

## 🐛 Troubleshooting

### "Server not responding" Error

**Solution:** Make sure Django development server is running:
```bash
python manage.py runserver 0.0.0.0:8000
```

### "Chrome/Chromium not found" Error

**Solution:** Install Playwright browsers:
```bash
playwright install chromium
```

### Connection Timeout Errors

**Solution:** Check your firewall and ensure:
- Django server is bound to `0.0.0.0` (not just localhost)
- Port 8000 is accessible
- No corporate proxy blocking connections

### Database Issues

If you get PostgreSQL connection errors:
1. Comment out `DB_NAME` environment variable in `.env`
2. Django will fallback to SQLite (`db.sqlite3`)

```bash
# In .env, comment out:
# DB_NAME=goexplorer_dev
# DB_USER=...
# DB_PASSWORD=...
```

## 📱 What Gets Tested

### Page Loads
- Each page is tested for successful navigation
- Page loads are verified with "domcontentloaded" state
- Full-page screenshots capture the rendered UI

### User Interactions (Hotels)
- Clicks on first hotel in the list
- Views hotel detail page
- Attempts to fill booking form:
  - Check-in date
  - Check-out date
  - Number of guests
  - Room type selection
  - Booking button click

### Video Recording
- Entire test session is recorded in WebM format
- Useful for debugging and visual verification
- Can be played in modern browsers or VLC

## 📈 Performance Notes

- Each test typically takes 15-30 seconds
- Video recording adds minimal overhead
- Screenshots are high-quality full-page captures
- Total artifacts: ~5-6 MB per test run

## 🔍 Advanced Usage

### Modifying Tests

Edit `tests/ui_e2e_playwright.py` to:
- Add new test flows
- Change timeouts
- Add new pages to test
- Modify screenshot quality/size

### Debugging Failed Tests

1. Check `tmp/test_report.txt` for detailed logs
2. Watch the recorded video in `tmp/*.webm`
3. Review screenshots for visual issues
4. Check browser console (run test with more detailed logging)

### Custom Test Scenarios

```python
# Example: Add a custom test
async def custom_test(page):
    await page.goto("http://localhost:8000/custom-page/")
    await page.wait_for_load_state("domcontentloaded")
    # Add assertions or interactions
```

## ✅ Success Criteria

Test is considered successful when:
- ✅ All pages load without errors
- ✅ Screenshots are captured
- ✅ Video file is created
- ✅ No fatal exceptions occur
- ✅ Test report is generated

## 🎯 Next Steps

1. ✅ Run the test suite
2. 📸 Review generated screenshots
3. 🎬 Watch the recorded video
4. 📋 Check the test report
5. 🐛 Fix any identified UI/UX issues
6. ♻️ Re-run to verify fixes

## 📚 References

- [Playwright Documentation](https://playwright.dev/python/)
- [Playwright API](https://playwright.dev/python/docs/api/class-playwright)
- [Async Playwright Guide](https://playwright.dev/python/docs/async-api/class-asyncplaywright)

## 💡 Tips

- Run tests regularly (CI/CD integration recommended)
- Compare screenshots between versions for visual regressions
- Use video recordings to demonstrate functionality
- Archive test artifacts for future reference
- Update tests as UI changes occur

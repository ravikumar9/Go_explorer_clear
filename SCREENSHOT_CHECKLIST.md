# SCREENSHOT VERIFICATION CHECKLIST

## REQUIRED SCREENSHOTS (5 tests × 2 devices = 10 total)

### DESKTOP TESTS (Full screen browser)

**[ ] TEST 1: Login Success & Redirect**
- URL: http://localhost:8000/users/login/
- Login: `admin@example.com` / `admin`
- Expected: Redirects to home page (/)
- Screenshot needed: Show homepage or confirm redirect in URL bar
- Proof: No error, page loads normally

**[ ] TEST 2: Bus Search - Filter Persistence (Before Refresh)**
- URL: http://localhost:8000/buses/?source_city=BLR&dest_city=HYD&travel_date=2026-01-15
- Expected: Bus results display with "Bangalore to Hyderabad" search
- Screenshot needed: Show search filters in form AND bus results
- Proof: Both cities visible in results or filter form

**[ ] TEST 2B: Bus Search - Filter Persistence (After Refresh)**
- Action: Press F5 to refresh page
- Expected: Same results appear with same URL params
- Screenshot needed: Show same URL bar and results after refresh
- Proof: URL still has `?source_city=BLR&dest_city=HYD&travel_date=...`

**[ ] TEST 3: Desktop Seat Layout**
- URL: http://localhost:8000/buses/1/?route_id=1&travel_date=2026-01-15
- Expected: 48 seats visible in grid layout with 3 colors
- Screenshot needed: Show full seat grid (green/pink/red seats), boarding/dropping dropdowns
- Proof: Seat layout visible, dropdown populated with "Electronic City" or similar, "Ameerpet Station" option visible

**[ ] TEST 4: Desktop Seat Selection with Price Update**
- Action: Click on 2 available seats (green color)
- Expected: Seats highlight (border/blue background), total price updates
- Screenshot needed: Show 2 seats selected (blue highlight) and updated price (1500 × 2 = 3000 + fees)
- Proof: Seats change color/style when clicked, price field updates to 3075 or similar

**[ ] TEST 5: Booking Confirmation (Real Data)**
- URL: http://localhost:8000/bookings/75a1bb3e-bdfe-4c9b-a495-ad756ed5af45/
- Expected: Page shows booking details with real data
- Screenshot needed: Show booking ID, customer name "Rajesh Kumar", email, phone, and total "Rs 3075.00"
- Proof: All fields show actual data (NOT placeholder like [Customer Name] or [Amount])

---

### MOBILE TESTS (Use DevTools F12 → Ctrl+Shift+M → iPhone 12)

**[ ] TEST 1M: Login on Mobile**
- Repeat TEST 1 on mobile viewport (375px width)
- Expected: Form stacks vertically, login works same
- Screenshot needed: Show mobile login page and successful redirect
- Proof: Responsive layout, no horizontal scrolling

**[ ] TEST 2M: Bus Search on Mobile**
- Repeat TEST 2 on mobile viewport
- Expected: Results visible without scroll, filter params persist on refresh
- Screenshot needed: Show bus results on mobile, then after F5 refresh
- Proof: Same functionality as desktop, readable on 375px

**[ ] TEST 3M: Seat Layout on Mobile**
- Repeat TEST 3 on mobile viewport
- Expected: Seat grid responsive, scrollable, boarding/dropping accessible
- Screenshot needed: Show seat grid on mobile (may need scrolling)
- Proof: All 48 seats accessible, dropdowns work

**[ ] TEST 4M: Seat Selection on Mobile**
- Repeat TEST 4 on mobile viewport
- Expected: Seats selectable on touch, price updates
- Screenshot needed: Show 2 seats selected on mobile
- Proof: Touch targets large enough, price updates work

**[ ] TEST 5M: Booking Confirmation on Mobile**
- Repeat TEST 5 on mobile viewport
- Expected: Booking info readable on 375px width
- Screenshot needed: Show all booking details on mobile (no horizontal scroll needed)
- Proof: Customer name, email, phone, total all visible

---

## HOW TO TAKE SCREENSHOTS

### Option A: Built-in Screenshot (Windows + Shift + S)
1. Press `Windows + Shift + S`
2. Select area to capture
3. Paste into editor or save

### Option B: Browser Screenshot (F12)
1. Open DevTools (F12)
2. Press Ctrl+Shift+P
3. Type "screenshot"
4. Select "Capture full page screenshot"

### Option C: Simple - Just describe what you see
If you cannot take screenshots, describe:
- What colors/text you see
- Confirm data is NOT placeholder
- Confirm mobile/desktop look different (responsive)

---

## SUBMIT PROOF

Reply with one of:

**Option 1: Screenshots**
Paste or describe 5 desktop + 5 mobile screenshots above

**Option 2: Video**
Record 10-second video of each flow on desktop & mobile

**Option 3: Detailed Description**
For each test, describe exactly what appears (colors, text, layout, no placeholders)

---

## SUCCESS CRITERIA

- [ ] All 5 flows work on desktop (login, search, seat layout, selection, confirmation)
- [ ] All 5 flows work on mobile (same functionality, responsive layout)
- [ ] Desktop and mobile show same data (parity)
- [ ] No error messages or broken styling
- [ ] Booking confirmation shows real customer name ("Rajesh Kumar"), not placeholder
- [ ] Seat layout shows actual seats (48 total), not placeholder
- [ ] Filter persistence verified (refresh shows same results)

**ONCE ALL 5 TESTS ARE PROVEN ON DESKTOP + MOBILE, I WILL COMMIT.**

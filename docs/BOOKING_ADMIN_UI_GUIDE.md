# 🎨 Booking Admin Panel - UI Guide & Color Reference

## 📍 Navigation Guide

### Accessing the Admin Panel
```
1. Go to: http://localhost:8000/admin/
2. Login with:
   - Username: admin
   - Password: AdminPassw0rd!
3. Look for "Bookings" section in left sidebar
```

### Menu Structure
```
Admin Panel Home
├── Authentication & Authorization
│   ├── Groups
│   └── Users
├── Bookings
│   ├── Bookings ← MAIN SECTION
│   ├── Bus Bookings
│   ├── Package Bookings
│   ├── Booking Audit Logs
│   └── Reviews
├── Buses
├── Core
├── Hotels
├── Notifications
├── Packages
├── Payments
├── Property Owners
└── Users
```

---

## 🎨 Color Guide

### Status Badges
These colors help you identify booking status at a glance:

```
🟡 PENDING (Yellow: #FFC107)
   - Awaiting confirmation
   - Editable
   - Action: Confirm, Edit, or Cancel

🟢 CONFIRMED (Green: #28A745)
   - Confirmed and ready
   - Operational
   - Action: View details, Edit, or Cancel

🔴 CANCELLED (Red: #DC3545)
   - Booking cancelled
   - No operation
   - Action: View reason and refund

🔵 COMPLETED (Blue: #007BFF)
   - Trip/service completed
   - Read-only
   - Action: View only

🟣 DELETED (Purple: #721C24)
   - Soft deleted
   - Hidden from default list
   - Action: Restore or permanent delete
```

### Booking Type Badges
```
🔵 BUS (Light Blue: #0d6efd)
   - Bus bookings

🟦 HOTEL (Cyan: #0dcaf0)
   - Hotel bookings

🟩 PACKAGE (Green: #198754)
   - Travel package bookings
```

### List Display Colors
```
📌 Border Colors on Cards:
   - Left border = 4px colored line indicating status
   - Different colors for pending/confirmed/cancelled/completed/deleted
```

---

## 📋 Booking List View

### What You'll See
```
┌─────────────────────────────────────────────────────────────┐
│ GoExplorer Admin > Bookings > Bookings                       │
├─────────────────────────────────────────────────────────────┤
│ Search: [..................] Filter [↓]  Clear All Filters    │
│                                                              │
│ ✓ ID  Customer      Phone      Type    Status    Amount Date │
├─────────────────────────────────────────────────────────────┤
│ ☐ 08938232 Raj Kumar 9876543210 🔵 BUS 🟡 ₹3000 2026-01-03 │
│ ☐ 1d778a06 Priya Singh 987654... 🔵 BUS 🟢 ₹3000 2026-01-03 │
│ ☐ edb9d178 Vikram P... 987654... 🔵 BUS 🔴 ₹1500 2026-01-03 │
│ ☐ 1c17f972 Neha Desai 987654... 🔵 BUS 🔵 ₹2250 2025-12-31 │
│ ☐ 5a24ac6c Anil Kumar 987654... 🔵 BUS 🟣 ₹1500 2026-01-03 │
└─────────────────────────────────────────────────────────────┘

Legend:
📌 ✓ = Checkbox for bulk actions
🟡 = Status badge (Yellow = Pending)
🟢 = Status badge (Green = Confirmed)
🔴 = Status badge (Red = Cancelled)
🔵 = Status badge (Blue = Completed)
🟣 = Status badge (Purple = Deleted)
```

---

## 🔍 Search Bar

### How to Search
```
Booking ID:     Type: 08938 or full UUID
Customer Name:  Type: "Raj Kumar" or "Priya"
Phone Number:   Type: "9876543210"
Email:          Type: "raj@example.com"
Username:       Type: "customer0"
```

### Search Tips
```
✓ Partial matches work
✓ Case-insensitive
✓ Real-time filtering
✓ Multiple fields indexed
✓ Fast response
```

---

## 🎚️ Filter Options

### Available Filters (Right Sidebar)

```
Booking Type:
  ☐ Hotel
  ☐ Bus
  ☐ Package

Status:
  ☐ Pending
  ☐ Confirmed
  ☐ Cancelled
  ☐ Completed
  ☐ Deleted

Created at:
  [Date Range Selector]

is_deleted:
  ☐ Yes (shows soft-deleted only)
  ☐ No (default, excludes deleted)
```

### Common Filters Combinations
```
To Find: Pending Confirmations
→ Status = Pending, is_deleted = No

To Find: All Cancelled with Refund
→ Status = Cancelled

To Find: Deleted Records
→ is_deleted = Yes

To Find: Today's Confirmed
→ Status = Confirmed, Created at = Today
```

---

## 📖 Booking Detail View

### Layout Overview
```
┌─────────────────────────────────────────────────────────────┐
│ Booking for 08938232 - [Edit] [Save] [Delete]               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ▼ BOOKING INFORMATION                                        │
│   Booking ID:   08938232-b96e-480c-9cce-815c5cb9e09a       │
│   User:         customer0                              [↓]   │
│   Booking Type: Bus                                   [↓]   │
│   Status:       🟡 PENDING                           [↓]   │
│                                                              │
│ ▼ CUSTOMER DETAILS                                          │
│   Customer Name: Raj Kumar                                  │
│   Customer Email: raj@example.com                          │
│   Customer Phone: 9876543210                               │
│   Special Requests: Window seat preferred                  │
│                                                              │
│ ▼ FINANCIAL                                                 │
│   Total Amount: 3000.00                                     │
│   Paid Amount: 0.00                                         │
│                                                              │
│ ▶ CANCELLATION (Collapsed)                                  │
│ ▶ SOFT DELETE (Collapsed)                                   │
│ ▶ AUDIT LOG (Collapsed)                                     │
│ ▶ TIMESTAMPS (Collapsed)                                    │
│                                                              │
│ [Bus Booking Details - Inline]                              │
│ Bus Schedule: [Selection]                                   │
│ Bus Route: [Selection]                                      │
│ Journey Date: [Date Picker]                                 │
│ Boarding Point: [Text Field]                                │
│ Dropping Point: [Text Field]                                │
│                                                              │
│ [Seats - Inline Editable]                                   │
│ Seat | Passenger Name | Age | Gender | [Delete]            │
│                                                              │
│                          [Save Changes]                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Collapsible Sections

### Click to Expand/Collapse
```
▼ BOOKING INFORMATION (Expanded)
▶ CANCELLATION (Collapsed - shows if cancelled)
▶ SOFT DELETE (Collapsed - shows if deleted)
▶ AUDIT LOG (Collapsed - always available)
▶ TIMESTAMPS (Collapsed - created/updated dates)
```

### Why Collapsible?
- Reduces visual clutter
- Focuses on main information
- Quick access to advanced details
- Professional appearance

---

## 📝 Audit Log Expansion

### What You'll See
```
▼ AUDIT LOG

Field    | Old Value        | New Value       | By    | Time
---------|------------------|-----------------|-------|------------------
status   | pending          | confirmed       | admin | 2026-01-03 10:45
boarding | Majestic Stand   | Electric City   | admin | 2026-01-03 11:20
journey  | 2026-01-10       | 2026-01-11      | admin | 2026-01-03 11:21
```

### Each Log Shows:
- Field Name: What was changed
- Old Value: Previous value (first 50 chars)
- New Value: New value (first 50 chars)
- By: Admin username who made change
- Time: Exact timestamp

---

## 🎯 Bulk Actions

### How to Use
```
1. Check checkboxes for multiple bookings
2. Dropdown: "Action" [▼]
3. Select action:
   - Soft delete selected bookings
   - Confirm selected bookings
   - Cancel selected bookings
4. Click [Go]
5. Confirm action
6. Bookings updated with audit logs
```

### Actions Available
```
🗑️ Soft Delete
   - Marks as deleted
   - Hides from default view
   - Reason optional

✅ Confirm Booking
   - Changes pending → confirmed
   - Creates audit log
   - Validates state

❌ Cancel Booking
   - Cancels booking
   - Marks as cancelled
   - Prevents operation
```

---

## 📊 Dashboard

### URL
```
http://localhost:8000/dashboard/
```

### Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Admin Dashboard                                              │
│ Welcome back! Here's your business overview.                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Total Bookings] [Today Bookings] [Pending] [Confirmed]    │
│ [Cancelled]      [Total Revenue]  [Today Rev] [Week Rev]   │
│                                                              │
│ 🚌 BUS OPERATIONS          📈 BOOKING BREAKDOWN            │
│ Bus Bookings: 4            Hotel: 0                         │
│ Active: 10                 Bus: 4                           │
│ Occupancy: 25%             Package: 0                       │
│                                                              │
│ 🎯 BUS OCCUPANCY                                            │
│ BLR-DEL: [████░░░░░░░░░░░░] 25% (10/40)                    │
│ MUM-BLR: [██████░░░░░░░░░░] 30% (12/40)                    │
│                                                              │
│ 📋 RECENT BOOKINGS                                          │
│ Booking ID | Customer | Type | Status | Amount | Date      │
│ 08938232   | Raj      | Bus  | 🟡     | ₹3000  | 2026-01-03│
│ ...        | ...      | ...  | ...    | ...    | ...      │
│                                                              │
│ ⚠️ PENDING ACTIONS                                          │
│ You have 1 booking awaiting confirmation. [Review now →]   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔢 Sample Data Reference

### Test Bookings
```
1. Raj Kumar
   ID: 08938232-b96e-480c-9cce-815c5cb9e09a
   Phone: 9876543210
   Status: 🟡 PENDING
   Amount: ₹3,000
   → Click to test editing

2. Priya Singh
   ID: 1d778a06-fae1-4d2d-9649-6643f048f5b1
   Phone: 9876543211
   Status: 🟢 CONFIRMED
   Seats: 2 booked
   → Click to view seat details

3. Vikram Patel
   ID: edb9d178-bc6a-440b-abc4-c1eb4d32abe1
   Phone: 9876543212
   Status: 🔴 CANCELLED
   Refund: ₹1,500
   → Shows cancellation details

4. Neha Desai
   ID: 1c17f972-eaee-428a-917d-b47b1aa6259b
   Phone: 9876543213
   Status: 🔵 COMPLETED
   → Read-only, trip finished

5. Anil Kumar
   ID: 5a24ac6c-59ad-4db8-85e1-b47b1aa6259b
   Phone: 9876543214
   Status: 🟣 DELETED
   → Filter is_deleted=True to view
```

---

## 🎨 Color Psychology

### Why These Colors?
```
🟡 YELLOW (Pending)
   - Attention needed
   - Action required
   - Warm, urgent feeling

🟢 GREEN (Confirmed)
   - Go/proceed
   - Active/healthy
   - Positive status

🔴 RED (Cancelled)
   - Stop/no action
   - Negative status
   - Warning color

🔵 BLUE (Completed)
   - Cool/calm
   - Done/finished
   - Professional color

🟣 PURPLE (Deleted)
   - Removed from view
   - Archive status
   - Rare occurrence
```

---

## ⌨️ Keyboard Shortcuts

### Admin Panel
```
Ctrl/Cmd + K    : Search
Ctrl/Cmd + S    : Save changes
Tab             : Navigate between fields
Enter           : Submit form
Escape          : Cancel/close
```

### Filtering
```
Type in search  : Real-time filter
Click filter    : Toggle options
Clear All       : Reset filters
```

---

## 💾 Data Persistence

### What Happens When You Save?
```
1. Form validation runs
2. Changes checked against original
3. If changed → Audit log created
4. Data saved to database
5. Page reloads with confirmation
6. Audit trail visible in detail view
```

### What's Immutable?
```
✓ Booking ID (UUID)
✓ Audit logs (read-only)
✓ Created at timestamp
✓ User who created
```

### What Can Be Changed?
```
✓ Status
✓ Customer details (name, phone, email)
✓ Boarding/dropping points
✓ Journey date
✓ Seat assignments
✓ Special requests
✓ Cancellation reason
```

---

## ✅ Common Tasks

### Task 1: View a Booking
```
1. Go to Admin → Bookings → Bookings
2. Click on booking ID or customer name
3. View all details
4. Scroll to see all sections
```

### Task 2: Edit a Booking
```
1. Open booking detail
2. Click [Edit] button (top right)
3. Change desired fields
4. Click [Save]
5. See audit log updated
```

### Task 3: Soft Delete a Booking
```
Option A - Individual:
1. Open booking
2. Click [Delete] button
3. Confirm deletion
4. Provide reason (optional)

Option B - Bulk:
1. Check multiple bookings
2. Select "Soft delete" action
3. Click [Go]
4. Enter reason
```

### Task 4: Search Bookings
```
1. Go to Bookings list
2. Click search bar
3. Type booking ID, name, or phone
4. Results filter automatically
5. Click result to open detail
```

### Task 5: View Audit Log
```
1. Open booking detail
2. Scroll to "AUDIT LOG" section
3. Click ▶ to expand
4. View all changes with timestamps
5. See who made each change
```

---

## 🆘 Troubleshooting

### "Booking not found"
→ Check if it's soft-deleted (filter: is_deleted=True)

### "Can't edit completed booking"
→ Completed bookings are read-only (expected)

### "Audit log not showing"
→ Scroll down to "AUDIT LOG" section and expand

### "Status badge not showing color"
→ Refresh page, status should display with color

### "Search not working"
→ Make sure you typed search term correctly

---

## 📞 UI Support

All UI elements are designed for:
- ✅ Easy navigation
- ✅ Quick actions
- ✅ Clear visual hierarchy
- ✅ Accessibility
- ✅ Mobile responsiveness

**Status:** ✅ UI Complete & Tested

---

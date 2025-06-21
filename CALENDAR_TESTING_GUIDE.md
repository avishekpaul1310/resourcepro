📅 AVAILABILITY CALENDAR - MANUAL TESTING GUIDE
======================================================================
Generated on: June 21, 2025

🎯 TESTING OBJECTIVE
Test all features of the Availability Calendar to ensure it's working properly
with the newly populated test data.

🔐 LOGIN CREDENTIALS
- URL: http://127.0.0.1:8000/accounts/login/
- Username: admin
- Password: admin123

📍 CALENDAR ACCESS
- Direct URL: http://127.0.0.1:8000/resources/availability/
- Navigation: Dashboard → Resources → Availability Calendar

📊 TEST DATA SUMMARY
======================================================================
- Total Records: 46 availability entries
- Resources: 5 team members (Alice Brown, Bob Johnson, Jane Smith, John Doe, Mike Wilson)
- Date Range: June 2025 - September 2025
- Types: Vacation (24%), Training (30%), Personal Leave (17%), Sick Leave (11%), Available (4%), Meeting (4%), Unavailable (9%)

📋 MANUAL TESTING CHECKLIST
======================================================================

🎨 1. VISUAL ELEMENTS
□ Calendar loads with FullCalendar interface
□ Color-coded events display correctly:
  • Vacation: Red (#ff6b6b)
  • Sick Leave: Yellow (#feca57)
  • Training: Blue (#48dbfb)
  • Available: Green (#1dd1a1)
  • Personal Leave: Purple
  • Meeting: Orange
  • Unavailable: Gray
□ Legend shows all availability types
□ Header shows current month/year
□ Navigation arrows (prev/next) visible

🗓️ 2. CALENDAR VIEWS
□ Month view (default) - shows events as colored blocks
□ Week view - detailed weekly schedule
□ List view - chronological list of events
□ Today button returns to current date
□ Navigation between months works smoothly

🔍 3. FILTERING FUNCTIONALITY
□ Resource filter dropdown shows all 5 team members
□ Selecting "Alice Brown" shows only her events
□ Selecting "Bob Johnson" shows only his events
□ Selecting "Jane Smith" shows only her events
□ Selecting "John Doe" shows only his events
□ Selecting "Mike Wilson" shows only his events
□ "All Resources" option shows events for everyone
□ URL updates with ?resource=X parameter when filtering

🖱️ 4. EVENT INTERACTION
□ Clicking on an event shows popup with details
□ Event popup displays:
  • Resource name
  • Availability type
  • Date range
  • Notes/description
□ Events are clickable and responsive

📝 5. ADD AVAILABILITY FORM
□ "Add Availability Entry" button opens modal
□ Modal contains all required fields:
  • Resource dropdown (5 options)
  • Start date picker
  • End date picker
  • Availability type dropdown (7 options)
  • Hours per day field
  • Notes textarea
□ Form validation works:
  • End date must be after start date
  • All required fields must be filled
□ Successful submission creates new event
□ New event appears immediately on calendar

📋 6. UPCOMING EVENTS SIDEBAR
□ "Upcoming Availability Events" section visible
□ Shows next 30 days of events
□ Events listed chronologically
□ Each event shows:
  • Date range
  • Resource name
  • Availability type
  • Notes (if any)

🔍 7. SPECIFIC DATA TO VERIFY

Current Week (June 21-27, 2025):
□ June 21: Alice Brown - Available
□ June 22: Alice Brown, Jane Smith, John Doe - Vacation
□ June 23: Alice Brown - Personal Leave, Mike Wilson - Vacation
□ June 25: Bob Johnson - Available
□ June 26: Alice Brown, Jane Smith, John Doe - Training

Next Week (June 28 - July 4, 2025):
□ June 29 - July 3: Alice Brown, Bob Johnson - Vacation
□ July 4: Jane Smith - Sick Leave

Future Events to Spot Check:
□ July 6-7: Multiple people on sick leave
□ July 13: Several people with personal leave/training
□ July 21: Multiple people unavailable
□ August 10-16: Bob Johnson long vacation
□ August 25-27: Multiple people in training

📱 8. RESPONSIVE DESIGN
□ Calendar displays properly on full screen
□ Mobile view (resize browser window)
□ Tablet view (medium screen size)
□ All buttons and controls remain accessible
□ Text remains readable at different sizes

🔗 9. NAVIGATION & INTEGRATION
□ Breadcrumbs or navigation menu present
□ Link to Time Tracking works
□ Return to Resources page works
□ Dashboard integration works
□ User can logout successfully

⚡ 10. PERFORMANCE & USABILITY
□ Calendar loads quickly (< 3 seconds)
□ No JavaScript errors in browser console
□ Smooth transitions between views
□ Events render without lag
□ Form submissions process quickly
□ Filtering updates calendar instantly

🚨 COMMON ISSUES TO WATCH FOR
======================================================================
❌ Events not displaying (check JavaScript console)
❌ Colors not matching legend
❌ Filtering not working (JavaScript errors)
❌ Form validation not working
❌ Mobile view broken layout
❌ Missing CSRF tokens causing form errors
❌ Authentication redirects

✅ SUCCESS CRITERIA
======================================================================
The calendar is working properly if:
• All 46 test events display correctly
• Color coding matches availability types
• Filtering by resource works for all 5 team members
• Form submission creates new events successfully
• Multiple calendar views (month/week/list) work
• Event clicking shows details
• Upcoming events sidebar shows correct data
• Navigation between months works smoothly
• Mobile/responsive design functions properly

📞 TROUBLESHOOTING
======================================================================
If issues occur:
1. Check browser console for JavaScript errors
2. Verify login credentials (admin/admin123)
3. Ensure Django server is running (http://127.0.0.1:8000)
4. Clear browser cache and reload
5. Check that populate_calendar_data.py ran successfully

🎉 COMPLETION
When all checkboxes are completed successfully, the Availability Calendar
is confirmed to be working properly and ready for production use!

======================================================================
Generated by ResourcePro Availability Calendar Testing Suite
Test data populated: June 21, 2025
Total test events: 46 across 5 resources

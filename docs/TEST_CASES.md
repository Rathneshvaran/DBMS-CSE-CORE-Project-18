# Review 3 Test Cases

| ID | Test | Expected result |
|---|---|---|
| T01 | Search by origin/destination/date | Matching flights displayed |
| T02 | Book an available seat | Booking, ticket and payment created |
| T03 | Select an already occupied seat | Transaction rejected |
| T04 | Book beyond aircraft capacity | Transaction rejected |
| T05 | Enter negative baggage | Validation rejects input |
| T06 | Check in confirmed booking | Check-in record created |
| T07 | Check in cancelled booking | Rejected |
| T08 | Cancel confirmed booking | Booking becomes Cancelled; refund generated |
| T09 | Cancel already cancelled booking | Rejected |
| T10 | View manifest | Passenger, ticket, seat and check-in status shown |
| T11 | View occupancy | Booked count and occupancy percentage shown |
| T12 | View revenue | Paid and refunded amounts reported |
| T13 | Duplicate email | Existing passenger reused/updated |
| T14 | Health endpoint | `{status: ok}` response |

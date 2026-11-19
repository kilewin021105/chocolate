# Integration Test Cases

| # | Action | Expected Result |
|---|---|---|
| 1 | Login with valid account | Dashboard opens |
| 2 | Login with invalid password | Error is displayed |
| 3 | Add product | Product is saved |
| 4 | Edit product | Product information changes |
| 5 | Delete test product | Product is removed |
| 6 | Add customer | Customer appears in list |
| 7 | Add supplier | Supplier appears in list |
| 8 | Create sale | Sale is recorded |
| 9 | Sell a product | Product stock decreases |
| 10 | View report | Transaction and inventory data appear |
| 11 | Open `/api/health` | API reports Supabase or demo fallback |

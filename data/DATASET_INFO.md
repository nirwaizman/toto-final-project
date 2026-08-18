# Dataset — Hotel Booking Demand

**Source:** Hotel Booking Demand Dataset (Antonio, Almeida, Nunes 2019 — widely used on Kaggle)
**File:** `data/raw/hotel_bookings.csv`
**Rows:** 119,390 bookings
**Hotels:** Resort Hotel + City Hotel (Portugal, 2015-2017)

## Why this dataset

Directly relevant to hospitality operations (Nir runs Hotel Eilat + Theodor Hotel Tel Aviv).
The target variable `is_canceled` mirrors a real business problem: predicting booking
cancellations to optimize overbooking and revenue management.

## Key Columns

| Column | Description |
|---|---|
| `hotel` | Resort Hotel / City Hotel |
| `is_canceled` | **Target** — 1 if canceled, 0 if not |
| `lead_time` | Days between booking and arrival |
| `arrival_date_*` | Year/month/week/day of arrival |
| `stays_in_weekend_nights` / `stays_in_week_nights` | Length of stay |
| `adults` / `children` / `babies` | Guest composition |
| `country` | Guest origin country |
| `market_segment` | Booking channel type |
| `distribution_channel` | Direct / TA/TO / Corporate |
| `is_repeated_guest` | Returning guest flag |
| `previous_cancellations` | Guest's cancellation history |
| `reserved_room_type` / `assigned_room_type` | Room details |
| `deposit_type` | No Deposit / Non Refund / Refundable |
| `customer_type` | Transient / Contract / Group / Transient-Party |
| `adr` | Average Daily Rate (price) |
| `total_of_special_requests` | Number of special requests |
| `reservation_status` | Final status |

## Business Question

**Crew 1 (Data Analyst):** What patterns exist in bookings, cancellations, revenue,
and guest behavior across the two hotels?

**Crew 2 (Data Scientist):** Can we predict, at booking time, whether a reservation
will be canceled — to help hotel management with overbooking strategy?

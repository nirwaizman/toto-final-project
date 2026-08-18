# Model Card — Hotel Booking Cancellation Predictor

## Model Purpose
Predicts, at booking time, the probability that a hotel reservation will be
canceled. Intended to support revenue management decisions such as overbooking
buffers and deposit policy — NOT to automatically deny or penalize guests.

## Training Data
- Source: Hotel Booking Demand dataset (Resort Hotel + City Hotel, Portugal, 2015-2017)
- Cleaned via Crew 1 (Data Analyst): missing values imputed, invalid rows removed
- Split: temporal (train 2015-2016, test 2017) to avoid future data leakage; `arrival_date_year` is used only as the split key, never as a feature
- Leakage columns (`reservation_status`, `reservation_status_date`) explicitly excluded; `assigned_room_type` (post-booking) and `agent`/`company` IDs also excluded

## Metrics
# Evaluation Report — Booking Cancellation Prediction

Train set: 77438 bookings (2015-2016) | Test set: 40129 bookings (2017)

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| RandomForestClassifier | 0.7871 | 0.7874 | 0.6216 | 0.6947 | 0.8713 |
| GradientBoostingClassifier ✅ (selected) | 0.7872 | 0.7913 | 0.6166 | 0.6931 | 0.875 |

**Best model:** GradientBoostingClassifier (highest ROC-AUC), saved to `outputs/model.pkl`.

Features used: 16 numeric + 9 categorical (one-hot encoded in-pipeline). Excluded: leakage columns ['reservation_status', 'reservation_status_date'], post-booking/ID columns ['arrival_date', 'assigned_room_type', 'agent', 'company'], and `arrival_date_year` (split key only).


## Limitations
- Trained on Portugal-based hotels (2015-2017); may not generalize to other markets, hotel types, or post-pandemic booking behavior.
- Moderate class imbalance (~37% cancellation rate): recall on the canceled class (~63%) is lower than precision (~79%), so a meaningful share of true cancellations is missed. The decision threshold (0.5) should be tuned to the hotel's cost of a missed cancellation vs. a false alarm.
- No guest-level personal identifiers were used, but `country` and `market_segment` are coarse proxies that could correlate with protected characteristics — model should not be used for individual guest profiling.
- Does not account for external shocks (pandemics, travel bans, macroeconomic shifts).

## Ethical Considerations
- **Do not** use this model to deny bookings, apply discriminatory pricing, or blacklist guests by country/origin.
- Intended use is aggregate risk scoring for **operational planning** (overbooking, staffing), not individual guest judgment.
- Model should be periodically retrained as booking patterns shift over time.
- Predictions are probabilistic, not deterministic — human review is required before any policy action.

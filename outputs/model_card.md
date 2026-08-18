# Model Card — Hotel Booking Cancellation Predictor

## Model Purpose
Predicts, at booking time, the probability that a hotel reservation will be
canceled. Intended to support revenue management decisions such as overbooking
buffers and deposit policy — NOT to automatically deny or penalize guests.

## Training Data
- Source: Hotel Booking Demand dataset (Resort Hotel + City Hotel, Portugal, 2015-2017)
- Cleaned via Crew 1 (Data Analyst): missing values imputed, invalid rows removed
- Split: temporal (train 2015-2016, test 2017) to avoid future data leakage
- Leakage columns (`reservation_status`, `reservation_status_date`) explicitly excluded

## Metrics
# Evaluation Report — Booking Cancellation Prediction

Train set: 77438 bookings (2015-2016) | Test set: 40129 bookings (2017)

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| RandomForestClassifier | 0.7862 | 0.7877 | 0.6179 | 0.6926 | 0.8706 |
| GradientBoostingClassifier ✅ (selected) | 0.7914 | 0.7924 | 0.6298 | 0.7018 | 0.876 |

**Best model:** GradientBoostingClassifier (highest ROC-AUC), saved to `outputs/model.pkl`.


## Limitations
- Trained on Portugal-based hotels (2015-2017); may not generalize to other markets, hotel types, or post-pandemic booking behavior.
- Moderate class imbalance (~37% cancellation rate) may bias predictions toward the majority class despite `class_weight='balanced'`.
- No guest-level personal identifiers were used, but `country` and `market_segment` are coarse proxies that could correlate with protected characteristics — model should not be used for individual guest profiling.
- Does not account for external shocks (pandemics, travel bans, macroeconomic shifts).

## Ethical Considerations
- **Do not** use this model to deny bookings, apply discriminatory pricing, or blacklist guests by country/origin.
- Intended use is aggregate risk scoring for **operational planning** (overbooking, staffing), not individual guest judgment.
- Model should be periodically retrained as booking patterns shift over time.
- Predictions are probabilistic, not deterministic — human review is required before any policy action.

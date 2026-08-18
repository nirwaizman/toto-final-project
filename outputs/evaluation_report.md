# Evaluation Report — Booking Cancellation Prediction

Train set: 77438 bookings (2015-2016) | Test set: 40129 bookings (2017)

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| RandomForestClassifier | 0.7871 | 0.7874 | 0.6216 | 0.6947 | 0.8713 |
| GradientBoostingClassifier ✅ (selected) | 0.7872 | 0.7913 | 0.6166 | 0.6931 | 0.875 |

**Best model:** GradientBoostingClassifier (highest ROC-AUC), saved to `outputs/model.pkl`.

Features used: 16 numeric + 9 categorical (one-hot encoded in-pipeline). Excluded: leakage columns ['reservation_status', 'reservation_status_date'], post-booking/ID columns ['arrival_date', 'assigned_room_type', 'agent', 'company'], and `arrival_date_year` (split key only).

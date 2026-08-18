# Evaluation Report — Booking Cancellation Prediction

Train set: 77438 bookings (2015-2016) | Test set: 40129 bookings (2017)

## Model Comparison

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| RandomForestClassifier | 0.7862 | 0.7877 | 0.6179 | 0.6926 | 0.8706 |
| GradientBoostingClassifier ✅ (selected) | 0.7914 | 0.7924 | 0.6298 | 0.7018 | 0.876 |

**Best model:** GradientBoostingClassifier (highest ROC-AUC), saved to `outputs/model.pkl`.

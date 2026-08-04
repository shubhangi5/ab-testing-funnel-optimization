# Experiment Readout: Affordability Nudge

## 1. Business Context

A food delivery platform tested an affordability nudge designed to improve the session-to-booking funnel. The treatment experience highlighted low delivery fee, discounted meals, and value-for-money options.

## 2. Primary Metric

Primary metric: Session-to-Booking Conversion Rate

## 3. Primary Result

| Metric | Control | Treatment | Absolute Lift | Relative Lift | p-value | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Session-to-Booking Conversion | 14.99% | 16.57% | 1.58 pp | 10.56% | 1e-06 | [0.94, 2.22] pp |

## 4. Interpretation

The treatment changed session-to-booking conversion by 1.58 percentage points.

Statistically significant: True

## 5. Guardrail Metrics

| metric           |   control_value |   treatment_value |   absolute_change |   relative_change |
|:-----------------|----------------:|------------------:|------------------:|------------------:|
| order_value      |     417.883     |       410.762     |      -7.12107     |             -1.7  |
| cancelled        |       0.0503597 |         0.0481025 |      -0.00225722  |             -4.48 |
| refunded         |       0.0210498 |         0.020788  |      -0.000261816 |             -1.24 |
| delayed_delivery |       0.0818012 |         0.0809766 |      -0.000824673 |             -1.01 |

## 6. Top Segment-Level Results

| segment_type   | segment_value   |   control_sessions |   treatment_sessions |   control_rate_pct |   treatment_rate_pct |   absolute_lift_pp |   relative_lift_pct |   p_value | statistically_significant   |
|:---------------|:----------------|-------------------:|---------------------:|-------------------:|---------------------:|-------------------:|--------------------:|----------:|:----------------------------|
| user_segment   | high_value_user |               3823 |                 3751 |              21.45 |                25.03 |               3.58 |               16.71 |  0.000221 | True                        |
| city           | Mumbai          |               5117 |                 4928 |              15.2  |                17.55 |               2.35 |               15.45 |  0.001466 | True                        |
| device_type    | Web             |               2491 |                 2601 |              14.33 |                16.53 |               2.2  |               15.35 |  0.029897 | True                        |
| city           | Delhi           |               5343 |                 5474 |              14.22 |                16.08 |               1.85 |               13.02 |  0.007257 | True                        |
| device_type    | iOS             |               7015 |                 6864 |              15.28 |                16.97 |               1.69 |               11.07 |  0.00675  | True                        |

## 7. Recommendation

Recommend rollout, subject to guardrail review.

## 8. Next Steps

- Review whether the lift is consistent across key user segments.
- Check whether the treatment reduces average order value or worsens cancellations, refunds, or delivery delays.
- If guardrails are stable, consider phased rollout.
- If segment-level effects vary, consider targeted rollout to the strongest-performing segments.

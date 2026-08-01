# A/B Testing Funnel Optimization

# A/B Testing and Funnel Optimization Case Study

## 1. Business Context

A food delivery platform wants to improve session-to-booking conversion. The product team launches an affordability nudge that highlights low delivery fee, discounted meals, and value-for-money options during restaurant discovery and checkout.

The goal of this analysis is to evaluate whether the intervention improved conversion without negatively impacting guardrail metrics such as average order value, cancellation rate, or refund rate.

## 2. Objective

Evaluate the impact of an A/B experiment on the user funnel and recommend whether the product change should be rolled out.

## 3. Experiment Design

### Hypothesis

Users exposed to affordability nudges will have a higher probability of completing a booking compared to users in the control group.

### Control Group

Users experience the existing food discovery and checkout journey.

### Treatment Group

Users see affordability nudges during restaurant discovery and checkout.

### Primary Metric

Session-to-Booking Conversion Rate

### Funnel Metrics

- Session to Restaurant View
- Restaurant View to Add-to-Cart
- Add-to-Cart to Checkout
- Checkout to Booking
- Overall Session-to-Booking Conversion

### Guardrail Metrics

- Average Order Value
- Cancellation Rate
- Refund Rate
- Delivery Delay Rate

## 4. Dataset

This project uses a synthetic event-level dataset simulating food delivery sessions.

The dataset contains:

- user_id
- session_id
- experiment_group
- city
- device_type
- user_segment
- session_start_time
- restaurant_viewed
- item_added_to_cart
- checkout_started
- booking_confirmed
- order_value
- cancelled
- refunded
- delayed_delivery

## 5. Methodology

The analysis includes:

1. Funnel construction using SQL
2. Conversion rate comparison between control and treatment
3. Statistical significance testing
4. Confidence interval estimation
5. Segment-level analysis
6. Guardrail metric review
7. Rollout recommendation

## 6. Key Questions

- Did the treatment improve session-to-booking conversion?
- Which funnel step improved the most?
- Did the impact vary by city, device, or user segment?
- Were there any negative guardrail movements?
- Should the product be rolled out fully, partially, or not at all?

## 7. Tools Used

- SQL
- Python
- pandas
- scipy/statsmodels
- matplotlib
- Jupyter Notebook

## 8. Business Recommendation

The final recommendation will be based on statistical significance, practical lift, segment-level consistency, and guardrail metric stability.
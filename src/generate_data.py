import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

N_SESSIONS = 50_000

OUTPUT_PATH = Path("data/raw/food_delivery_ab_experiment.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


# -----------------------------
# 1. User/session level fields
# -----------------------------

session_id = np.arange(1, N_SESSIONS + 1)
user_id  = np.random.randint(10000,25000, size=N_SESSIONS)

experiment_group = np.random.choice(['control', 'treatment'], size=N_SESSIONS, p=[0.5, 0.5])
city_group = np.random.choice(["Bangalore", "Delhi", "Mumbai", "Hyderabad", "Pune"],
    size=N_SESSIONS,
    p=[0.28, 0.22, 0.20, 0.17, 0.13]
)

device_type = np.random.choice(["iOS", "Android", "Web"],size = N_SESSIONS, p=[0.28, 0.62, 0.1])
user_segment = np.random.choice(["new_user", "returning_user", "high_value_user"],
    size=N_SESSIONS,
    p=[0.35, 0.50, 0.15])
session_start_time = pd.date_range(start="2026-01-01", periods=N_SESSIONS, freq="min")

# -----------------------------
# 2. Segment adjustment factors
# -----------------------------

segment_factor = np.select(
   [
        user_segment == "new_user",
        user_segment == "returning_user",
        user_segment == "high_value_user"
    ],
    [
        -0.04,
        0.00,
        0.06
    ],
    default=0)
device_factor = np.select(
    [
        device_type == "Android",
        device_type == "iOS",
        device_type == "Web"
    ],
    [
        0.00,
        0.02,
        -0.03
    ],
    default=0
)

treatment_flag = experiment_group == "treatment"

# -----------------------------
# 3. Funnel probabilities
# -----------------------------

p_restaurant_viewed = 0.72 + segment_factor + device_factor + np.where(treatment_flag, 0.025, 0)
p_added_to_cart = 0.48 + segment_factor + np.where(treatment_flag, 0.020, 0)
p_checkout_started = 0.62 + segment_factor + np.where(treatment_flag, 0.015, 0)
p_booking_confirmed = 0.70 + segment_factor + np.where(treatment_flag, 0.020, 0)

# Keep probabilities between 0 and 1
p_restaurant_viewed = np.clip(p_restaurant_viewed, 0.01, 0.99)
p_added_to_cart = np.clip(p_added_to_cart, 0.01, 0.99)
p_checkout_started = np.clip(p_checkout_started, 0.01, 0.99)
p_booking_confirmed = np.clip(p_booking_confirmed, 0.01, 0.99)

restaurant_viewed = np.random.binomial(1, p_restaurant_viewed)
item_added_to_cart = np.where(
    restaurant_viewed == 1,
    np.random.binomial(1, p_added_to_cart),
    0
)

checkout_started = np.where(
    item_added_to_cart == 1,
    np.random.binomial(1, p_checkout_started),
    0
)

booking_confirmed = np.where(
    checkout_started == 1,
    np.random.binomial(1, p_booking_confirmed),
    0
)

# -----------------------------
# 4. Order and guardrail metrics
# -----------------------------


base_order_value = np.random.normal(loc=420, scale=120, size=N_SESSIONS)

# Treatment users may have slightly lower AOV because affordability nudges push value options.
order_value = np.where(
    booking_confirmed == 1,
    base_order_value - np.where(treatment_flag, 10, 0),
    np.nan
)

order_value = np.where(order_value < 100, 100, order_value)

cancelled = np.where(
    booking_confirmed == 1,
    np.random.binomial(1, np.where(treatment_flag, 0.052, 0.050)),
    0
)

refunded = np.where(
    booking_confirmed == 1,
    np.random.binomial(1, np.where(treatment_flag, 0.022, 0.020)),
    0
)

delayed_delivery = np.where(
    booking_confirmed == 1,
    np.random.binomial(1, np.where(treatment_flag, 0.083, 0.080)),
    0
)


# -----------------------------
# 5. Final dataframe
# -----------------------------
df = pd.DataFrame({
    "session_id": session_id,
    "user_id": user_id,
    "experiment_group": experiment_group,
    "city": city_group,
    "device_type": device_type,
    "user_segment": user_segment,
    "session_start_time": session_start_time,
    "restaurant_viewed": restaurant_viewed,
    "item_added_to_cart": item_added_to_cart,
    "checkout_started": checkout_started,
    "booking_confirmed": booking_confirmed,
    "order_value": np.round(order_value, 2),
    "cancelled": cancelled,
    "refunded": refunded,
    "delayed_delivery": delayed_delivery
})

df.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset created successfully: {OUTPUT_PATH}")
print(f"Rows: {len(df):,}")
print("\nExperiment split:")
print(df["experiment_group"].value_counts(normalize=True).round(3))

print("\nBooking conversion by group:")
print(
    df.groupby("experiment_group")["booking_confirmed"]
    .mean()
    .rename("session_to_booking_conversion")
    .round(4)
)
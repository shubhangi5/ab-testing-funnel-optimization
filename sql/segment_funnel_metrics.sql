WITH base AS (
    SELECT *
    FROM read_csv_auto('data/raw/food_delivery_ab_experiment.csv')
)

SELECT
    experiment_group,
    city,
    device_type,
    user_segment,

    COUNT(*) AS sessions,
    SUM(booking_confirmed) AS bookings,

    ROUND(100.0 * SUM(restaurant_viewed) / COUNT(*), 2) AS session_to_restaurant_view_rate,

    ROUND(
        100.0 * SUM(item_added_to_cart) / NULLIF(SUM(restaurant_viewed), 0),
        2
    ) AS restaurant_view_to_cart_rate,

    ROUND(
        100.0 * SUM(checkout_started) / NULLIF(SUM(item_added_to_cart), 0),
        2
    ) AS cart_to_checkout_rate,

    ROUND(
        100.0 * SUM(booking_confirmed) / NULLIF(SUM(checkout_started), 0),
        2
    ) AS checkout_to_booking_rate,

    ROUND(100.0 * SUM(booking_confirmed) / COUNT(*), 2) AS session_to_booking_rate,

    ROUND(
        AVG(CASE WHEN booking_confirmed = 1 THEN order_value END),
        2
    ) AS avg_order_value

FROM base
GROUP BY
    experiment_group,
    city,
    device_type,
    user_segment
ORDER BY
    city,
    device_type,
    user_segment,
    experiment_group;
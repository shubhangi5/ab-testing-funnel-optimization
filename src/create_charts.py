from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("data/raw/food_delivery_ab_experiment.csv")
CHARTS_PATH = Path("reports/charts")
CHARTS_PATH.mkdir(parents=True, exist_ok=True)


def save_funnel_conversion_chart(df):
    funnel_summary = (
        df.groupby("experiment_group")
        .agg(
            sessions=("session_id", "count"),
            restaurant_views=("restaurant_viewed", "sum"),
            add_to_cart=("item_added_to_cart", "sum"),
            checkout_started=("checkout_started", "sum"),
            bookings=("booking_confirmed", "sum"),
        )
        .reset_index()
    )

    funnel_steps = [
        "restaurant_views",
        "add_to_cart",
        "checkout_started",
        "bookings",
    ]

    for step in funnel_steps:
        funnel_summary[f"{step}_rate"] = (
            funnel_summary[step] / funnel_summary["sessions"] * 100
        )

    chart_df = funnel_summary[
        [
            "experiment_group",
            "restaurant_views_rate",
            "add_to_cart_rate",
            "checkout_started_rate",
            "bookings_rate",
        ]
    ].copy()

    chart_df = chart_df.set_index("experiment_group").T
    chart_df.index = [
        "Restaurant View",
        "Add to Cart",
        "Checkout Started",
        "Booking Confirmed",
    ]

    ax = chart_df.plot(kind="bar", figsize=(10, 6))
    ax.set_title("Funnel Conversion by Experiment Group")
    ax.set_xlabel("Funnel Step")
    ax.set_ylabel("Conversion Rate from Session (%)")
    ax.legend(title="Experiment Group")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(CHARTS_PATH / "funnel_conversion_by_group.png", dpi=200)
    plt.close()


def save_primary_metric_chart():
    primary = pd.read_csv("reports/primary_metric_analysis.csv")

    control_rate = primary.loc[0, "control_rate_pct"]
    treatment_rate = primary.loc[0, "treatment_rate_pct"]

    chart_df = pd.DataFrame({
        "experiment_group": ["control", "treatment"],
        "conversion_rate": [control_rate, treatment_rate],
    })

    ax = chart_df.plot(
        x="experiment_group",
        y="conversion_rate",
        kind="bar",
        legend=False,
        figsize=(7, 5),
    )

    ax.set_title("Primary Metric: Session-to-Booking Conversion")
    ax.set_xlabel("Experiment Group")
    ax.set_ylabel("Conversion Rate (%)")
    plt.xticks(rotation=0)

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f%%")

    plt.tight_layout()
    plt.savefig(CHARTS_PATH / "primary_metric_conversion.png", dpi=200)
    plt.close()


def save_guardrail_chart():
    guardrails = pd.read_csv("reports/guardrail_analysis.csv")

    # Exclude order value because it is on a different scale.
    rate_guardrails = guardrails[
        guardrails["metric"].isin(["cancelled", "refunded", "delayed_delivery"])
    ].copy()

    rate_guardrails["control_pct"] = rate_guardrails["control_value"] * 100
    rate_guardrails["treatment_pct"] = rate_guardrails["treatment_value"] * 100

    chart_df = rate_guardrails[
        ["metric", "control_pct", "treatment_pct"]
    ].set_index("metric")

    ax = chart_df.plot(kind="bar", figsize=(9, 5))
    ax.set_title("Guardrail Metrics by Experiment Group")
    ax.set_xlabel("Guardrail Metric")
    ax.set_ylabel("Rate (%)")
    ax.legend(["Control", "Treatment"])
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    plt.savefig(CHARTS_PATH / "guardrail_metrics.png", dpi=200)
    plt.close()


def save_segment_lift_chart():
    segments = pd.read_csv("reports/segment_ab_test_summary.csv")

    top_segments = (
        segments.sort_values("absolute_lift_pp", ascending=False)
        .head(10)
        .copy()
    )

    top_segments["segment"] = (
        top_segments["segment_type"] + ": " + top_segments["segment_value"]
    )

    ax = top_segments.plot(
        x="segment",
        y="absolute_lift_pp",
        kind="bar",
        legend=False,
        figsize=(11, 6),
    )

    ax.set_title("Top Segments by Absolute Conversion Lift")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Absolute Lift in Conversion Rate (pp)")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()

    plt.savefig(CHARTS_PATH / "top_segment_lift.png", dpi=200)
    plt.close()


def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. "
            "Run `python src/generate_data.py` first."
        )

    df = pd.read_csv(DATA_PATH)

    save_funnel_conversion_chart(df)
    save_primary_metric_chart()
    save_guardrail_chart()
    save_segment_lift_chart()

    print("Charts created successfully in reports/charts/")


if __name__ == "__main__":
    main()
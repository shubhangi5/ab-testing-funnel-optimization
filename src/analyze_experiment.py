from pathlib import Path
from math import sqrt,erfc
import pandas as pd

data_path = Path("data/raw/food_delivery_ab_experiment.csv")
reports_path = Path("reports")
reports_path.mkdir(parents=True, exist_ok=True)

def two_proportion_test(control_success, control_total, treatment_success, treatment_total):
    """
    Perform a two-proportion z-test to compare the success rates of two groups.

    Parameters:
    control_success (int): Number of successes in the control group.
    control_total (int): Total number of observations in the control group.
    treatment_success (int): Number of successes in the treatment group.
    treatment_total (int): Total number of observations in the treatment group.

    Returns:
    float: z-score for the test.
    float: p-value for the test.
    """
    # Calculate proportions
    p_control = control_success / control_total
    p_treatment = treatment_success / treatment_total

    diff = p_treatment - p_control
    relative_lift = diff / p_control if p_control != 0 else None

    # Pooled proportion
    p_pool = (control_success + treatment_success) / (control_total + treatment_total)

    # Standard error
    se = sqrt(p_pool * (1 - p_pool) * (1/control_total + 1/treatment_total))

    # Z-score
    z_score = diff/se if se != 0 else None

     # Two-tailed p-value using complementary error function
    p_value = erfc(abs(z_score) / sqrt(2))

     # Unpooled standard error for confidence interval
    ci_se = sqrt((p_control * (1 - p_control) / control_total) +
                  (p_treatment * (1 - p_treatment) / treatment_total))
    ci_low = diff - 1.96 * ci_se
    ci_high = diff + 1.96 * ci_se

    return {
        "control_rate": p_control,
        "treatment_rate": p_treatment,
        "absolute_lift": diff,
        "relative_lift": relative_lift,
        "z_score": z_score,
        "p_value": p_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
    }


def run_primary_metric_analysis(df):
    """
    Run the primary metric analysis on the provided DataFrame.
    """
    # Group by variant and calculate successes and totals
    summary = (df.groupby('experiment_group').agg(
        sessions = ("session_id","count"),
        bookings = ("booking_confirmed","sum")
    ).reset_index()
    )

    control = summary[summary['experiment_group'] == 'control'].iloc[0]
    treatment = summary[summary['experiment_group'] == 'treatment'].iloc[0]

    # Perform two-proportion test
    result = two_proportion_test(
        control_success=control['bookings'],
        control_total=control['sessions'],
        treatment_success=treatment['bookings'],
        treatment_total=treatment['sessions']
    )

   
    output = pd.DataFrame([{
        "metric":  "session_to_booking_conversion",
        "control_sessions": control['sessions'],
        "treatment_sessions": treatment['sessions'],
        "control_bookings": control['bookings'],
        "treatment_bookings": treatment['bookings'],
        "control_rate_pct" : round(result['control_rate'] * 100, 2),
        "treatment_rate_pct" : round(result['treatment_rate'] * 100, 2),
        "absolute_lift_pp" : round(result['absolute_lift'] * 100,2),
        "relative_lift_pct" : round(result['relative_lift'] * 100,2), 
        "ci_low_pp" : round(result['ci_low'] * 100,2),
        "ci_high_pp" : round(result['ci_high'] * 100,2),    
        "z_score": round(result['z_score'], 3),
        "p_value": round(result['p_value'], 6),
        "statistically_significant": (result['p_value'] < 0.05) and not (result['ci_low'] <= 0 <= result['ci_high'])

    }])

    output.to_csv(reports_path / "primary_metric_analysis.csv", index=False)
    return output



def run_guardrail_analysis(df):
    booked = df[df["booking_confirmed"] == 1].copy()
    guardrails = []
    for metric in ["order_value", "cancelled", "refunded", "delayed_delivery"]:
         metric_summary = (
            booked.groupby("experiment_group")
            .agg(
                sample_size=(metric, "count"),
                metric_value=(metric, "mean")
            )
            .reset_index()
        )

         control_value = metric_summary.loc[metric_summary["experiment_group"] == "control",
                                             "metric_value"].iloc[0]
         
         treatment_value = metric_summary.loc[metric_summary["experiment_group"] == "treatment",
                                             "metric_value"].iloc[0]
         absolute_change = treatment_value - control_value
         relative_change = absolute_change / control_value if control_value != 0 else None

         guardrails.append({
            "metric": metric,
            "control_value": control_value,
            "treatment_value": treatment_value,
            "absolute_change": absolute_change,
            "relative_change": round(relative_change * 100, 2) if relative_change is not None else None
        })

    output = pd.DataFrame(guardrails)
    output.to_csv(reports_path / "guardrail_analysis.csv", index=False)
    return output

def segment_lift(df, segment_column):
    rows = []

    for segment_value in sorted(df[segment_column].dropna().unique()):
        segment_df = df[df[segment_column] == segment_value]

        summary = (
            segment_df.groupby("experiment_group")
            .agg(
                sessions=("session_id", "count"),
                bookings=("booking_confirmed", "sum")
            )
            .reset_index()
        )

        groups_present = set(summary["experiment_group"].unique())

        if "control" not in groups_present or "treatment" not in groups_present:
            continue

        control = summary[summary["experiment_group"] == "control"].iloc[0]
        treatment = summary[summary["experiment_group"] == "treatment"].iloc[0]

        result = two_proportion_test(
            control_success=control["bookings"],
            control_total=control["sessions"],
            treatment_success=treatment["bookings"],
            treatment_total=treatment["sessions"],
        )

        rows.append({
            "segment_type": segment_column,
            "segment_value": segment_value,
            "control_sessions": int(control["sessions"]),
            "treatment_sessions": int(treatment["sessions"]),
            "control_rate_pct": round(result["control_rate"] * 100, 2),
            "treatment_rate_pct": round(result["treatment_rate"] * 100, 2),
            "absolute_lift_pp": round(result["absolute_lift"] * 100, 2),
            "relative_lift_pct": round(result["relative_lift"] * 100, 2),
            "p_value": round(result["p_value"], 6),
            "statistically_significant": result["p_value"] < 0.05
        })

    return pd.DataFrame(rows)


def run_segment_analysis(df):
    segment_outputs = []

    for segment_column in ["city", "device_type", "user_segment"]:
        segment_result = segment_lift(df, segment_column)

        if not segment_result.empty:
            segment_outputs.append(segment_result)

    if not segment_outputs:
        raise ValueError("No valid segment-level A/B test results were created.")

    output = pd.concat(segment_outputs, ignore_index=True)

    print("\nSegment output columns:")
    print(output.columns.tolist())

    output = output.sort_values(
        by=["statistically_significant", "absolute_lift_pp"],
        ascending=[False, False]
    )

    output.to_csv(reports_path / "segment_ab_test_summary.csv", index=False)

    return output

def write_executive_summary(primary,guardrails,segments):
     primary_row = primary.iloc[0]
     if (
        primary_row["statistically_significant"]
        and primary_row["absolute_lift_pp"] > 0
    ):
        recommendation = "Recommend rollout, subject to guardrail review."
     elif primary_row["absolute_lift_pp"] > 0:
        recommendation = "Do not fully rollout yet. Continue testing or increase sample size."
     else:
        recommendation = "Do not rollout. Treatment did not improve the primary metric."

     top_segments = segments.head(5)

     summary = f"""# Experiment Readout: Affordability Nudge

## 1. Business Context

A food delivery platform tested an affordability nudge designed to improve the session-to-booking funnel. The treatment experience highlighted low delivery fee, discounted meals, and value-for-money options.

## 2. Primary Metric

Primary metric: Session-to-Booking Conversion Rate

## 3. Primary Result

| Metric | Control | Treatment | Absolute Lift | Relative Lift | p-value | 95% CI |
|---|---:|---:|---:|---:|---:|---:|
| Session-to-Booking Conversion | {primary_row["control_rate_pct"]}% | {primary_row["treatment_rate_pct"]}% | {primary_row["absolute_lift_pp"]} pp | {primary_row["relative_lift_pct"]}% | {primary_row["p_value"]} | [{primary_row["ci_low_pp"]}, {primary_row["ci_high_pp"]}] pp |

## 4. Interpretation

The treatment changed session-to-booking conversion by {primary_row["absolute_lift_pp"]} percentage points.

Statistically significant: {primary_row["statistically_significant"]}

## 5. Guardrail Metrics

{guardrails.to_markdown(index=False)}

## 6. Top Segment-Level Results

{top_segments.to_markdown(index=False)}

## 7. Recommendation

{recommendation}

## 8. Next Steps

- Review whether the lift is consistent across key user segments.
- Check whether the treatment reduces average order value or worsens cancellations, refunds, or delivery delays.
- If guardrails are stable, consider phased rollout.
- If segment-level effects vary, consider targeted rollout to the strongest-performing segments.
"""

     output_path = reports_path / "experiment_readout.md"
     output_path.write_text(summary, encoding="utf-8")

     print(f"\nCreated: {output_path}")


def main():
    if not data_path.exists():
        raise FileNotFoundError( f"Dataset not found at {data_path}. "
            "Run `python src/generate_data.py` first.")
    df = pd.read_csv(data_path)

    primary = run_primary_metric_analysis(df)
    guardrails = run_guardrail_analysis(df)
    segments = run_segment_analysis(df)

    write_executive_summary(primary, guardrails, segments)
    print("\nPrimary metric result:")
    print(primary.to_string(index=False))

    print("\nGuardrail metrics:")
    print(guardrails.to_string(index=False))

    print("\nTop segment results:")
    print(segments.head(10).to_string(index=False))    

if __name__ == "__main__":
    main()                        

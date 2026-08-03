from pathlib import Path
import duckdb

data_path = Path('data/raw/food_delivery_ab_experiment.csv')
reports_path = Path('reports')

reports_path.mkdir(parents=True, exist_ok=True)

def run_query(sql_file : str,output_file : str) -> None:
    query_path = Path(sql_file)

    if not data_path.exists():
         raise FileNotFoundError(
            f"Dataset not found at {data_path}. "
            "Run `python src/generate_data.py` first."
        )

    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_path}")
    query = query_path.read_text()

    with duckdb.connect() as conn:
        result = conn.execute(query).df()
    output_path = reports_path / output_file
    result.to_csv(output_path, index=False)

    print(f"\nCreated: {output_path}")
    print(result.head(10).to_string(index=False))

if __name__ == "__main__":
    run_query(
        sql_file="sql/funnel_metrics.sql",
        output_file="funnel_metrics_by_group.csv")
    run_query(
        sql_file="sql/segment_funnel_metrics.sql",
        output_file="funnel_metrics_by_segment.csv"
    )



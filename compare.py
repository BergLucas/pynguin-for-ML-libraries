import argparse
import json
from collections import Counter
from pprint import pprint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_summary")
    parser.add_argument("second_summary")

    args = parser.parse_args()

    with open(args.first_summary, "r") as f:
        first_summary = json.load(f)

    with open(args.second_summary, "r") as f:
        second_summary = json.load(f)

    keys = [
        "experiment_name",
        "nb_experiments",
        "mean_coverage",
        "mean_iterations",
        "mean_total_time",
        "mean_search_time",
        "mean_mutation_score",
        "return_code_counter",
    ]

    for key in keys:
        first_summary_value = str(first_summary[key])
        second_summary_value = str(second_summary[key])
        print(f"{key:<25}: {first_summary_value:<35} {second_summary_value:<35}")


if __name__ == "__main__":
    main()

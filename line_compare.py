from scipy.stats import mannwhitneyu
import argparse
import json
import os


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_experiment")
    parser.add_argument("second_experiment")

    args = parser.parse_args()

    first_summary_path = os.path.join(args.first_experiment, "summary.json")
    second_summary_path = os.path.join(args.second_experiment, "summary.json")

    with open(first_summary_path, "r") as f:
        first_summary = json.load(f)

    with open(second_summary_path, "r") as f:
        second_summary = json.load(f)

    first_executed_lines_counter: dict = first_summary["executed_lines_counter"]
    second_executed_lines_counter: dict = second_summary["executed_lines_counter"]

    lines = sorted(
        first_executed_lines_counter.keys() | second_executed_lines_counter.keys(),
        key=lambda line: int(line),
    )

    for line in lines:
        first_count = first_executed_lines_counter[line]
        second_count = second_executed_lines_counter[line]

        first_distribution = [True] * first_count + [False] * (
            first_summary["nb_runs"] - first_count
        )
        second_distribution = [True] * second_count + [False] * (
            second_summary["nb_runs"] - second_count
        )

        t_statistic, p_value = mannwhitneyu(
            first_distribution, second_distribution, alternative="two-sided"
        )

        print(f"Line {line} Mann–Whitney U-test: {t_statistic} (pvalue: {p_value})")


if __name__ == "__main__":
    main()

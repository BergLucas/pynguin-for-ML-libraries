from scipy.stats import mannwhitneyu
from utils import load_summary
import argparse
import csv
import os


def get_coverages(experiment_path: str, nb_runs: int) -> list[float]:
    coverages = []
    for i in range(nb_runs):
        run_path = os.path.join(experiment_path, str(i))

        statistics_path = os.path.join(run_path, "statistics.csv")

        try:
            with open(statistics_path, "r") as f:
                (statistics,) = csv.DictReader(f)
            coverage = float(statistics["Coverage"])
        except FileNotFoundError:
            coverage = 0.0

        coverages.append(coverage)

    return coverages


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_experiment")
    parser.add_argument("second_experiment")

    args = parser.parse_args()

    first_summary = load_summary(args.first_experiment)
    second_summary = load_summary(args.second_experiment)

    keys = [
        "experiment_name",
        "nb_runs",
        "mean_coverage",
        "mean_iterations",
        "mean_total_time",
        "mean_search_time",
        "mean_mutation_score",
        "crash_test_count",
        "return_code_counter",
    ]

    for key in keys:
        first_summary_value = str(first_summary[key])
        second_summary_value = str(second_summary[key])
        print(f"{key:<30}: {first_summary_value:<35} {second_summary_value:<35}")

    first_coverages = get_coverages(args.first_experiment, first_summary["nb_runs"])
    second_coverages = get_coverages(args.second_experiment, second_summary["nb_runs"])

    u_statistic, p_value = mannwhitneyu(
        first_coverages, second_coverages, alternative="two-sided"
    )

    n1 = len(first_coverages)
    n2 = len(second_coverages)
    a12 = u_statistic / (n1 * n2)

    distance = abs(a12 - 0.5)

    if distance < 0.06:
        difference = "Negligible"
    elif distance < 0.14:
        difference = "Small"
    elif distance < 0.21:
        difference = "Medium"
    else:
        difference = "Large"

    print(f"Mann–Whitney U-test           : {u_statistic} (pvalue: {p_value})")
    print(f"Vargha-Delaney A statistic    : {a12} ({difference})")


if __name__ == "__main__":
    main()

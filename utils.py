from scipy.stats import mannwhitneyu
import json
import csv
import os


def load_summary(experiment_path: str) -> dict:
    summary_path = os.path.join(experiment_path, "summary.json")

    with open(summary_path, "r") as f:
        return json.load(f)


def compare_distributions(
    first_distribution: list[float],
    second_distribution: list[float],
) -> tuple[float, float, float, str]:
    u_statistic, p_value = mannwhitneyu(
        first_distribution, second_distribution, alternative="two-sided"
    )

    n1 = len(first_distribution)
    n2 = len(second_distribution)
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

    return u_statistic, p_value, a12, difference


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

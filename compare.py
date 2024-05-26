from utils import load_summary, get_coverages, compare_distributions
import argparse


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

    u_statistic, p_value, a12, difference = compare_distributions(
        first_coverages, second_coverages
    )

    print(f"Mann–Whitney U-test           : {u_statistic:.2f} (pvalue: {p_value:.2f})")
    print(f"Vargha-Delaney A statistic    : {a12:.2f} ({difference:.2f})")


if __name__ == "__main__":
    main()

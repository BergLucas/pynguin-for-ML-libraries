from utils import load_summary, get_coverages, compare_distributions
from pylatex import NoEscape
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_experiment")
    parser.add_argument("second_experiment")

    args = parser.parse_args()

    first_summary = load_summary(args.first_experiment)
    second_summary = load_summary(args.second_experiment)

    first_mean_coverage = first_summary["mean_coverage"]
    second_mean_coverage = second_summary["mean_coverage"]

    first_coverages = get_coverages(args.first_experiment, first_summary["nb_runs"])
    second_coverages = get_coverages(args.second_experiment, second_summary["nb_runs"])

    _, p_value, a12, difference = compare_distributions(
        first_coverages, second_coverages
    )

    if p_value < 0.05:
        color = "\\cellcolor{gray!25}"
    else:
        color = ""

    if p_value < 0.01:
        p_value_str = "<0.01"
    else:
        p_value_str = f"{p_value:.2f}"

    print(
        NoEscape(
            f"{first_mean_coverage:.2f} & {second_mean_coverage:.2f} & {color}{p_value_str} & {difference} ({a12:.2f}) \\\\"
        )
    )


if __name__ == "__main__":
    main()

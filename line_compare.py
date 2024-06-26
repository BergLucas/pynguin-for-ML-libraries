from utils import load_summary, compare_distributions
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_experiment")
    parser.add_argument("second_experiment")

    args = parser.parse_args()

    first_summary = load_summary(args.first_experiment)
    second_summary = load_summary(args.second_experiment)

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

        u_statistic, p_value, a12, difference = compare_distributions(
            first_distribution, second_distribution
        )

        print(
            f"Line {line:<4} Mann–Whitney U-test: {u_statistic:.2f} (pvalue: {p_value:.2f}) / Vargha-Delaney A statistic: {a12:.2f} ({difference})"
        )


if __name__ == "__main__":
    main()

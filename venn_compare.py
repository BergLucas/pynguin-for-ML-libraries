from matplotlib_venn import venn2_unweighted
from utils import load_summary
import matplotlib.pyplot as plt
import argparse


def executed_lines_set(executed_lines_counter: dict[str, int]) -> set[str]:
    return set(key for key, value in executed_lines_counter.items() if value > 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_experiment")
    parser.add_argument("second_experiment")

    args = parser.parse_args()

    summaries = [
        load_summary(args.first_experiment),
        load_summary(args.second_experiment),
    ]

    experiment_names = " and ".join(summary["experiment_name"] for summary in summaries)
    executed_lines_names = [summary["experiment_name"] for summary in summaries]
    executed_lines_sets = [
        executed_lines_set(summary["executed_lines_counter"]) for summary in summaries
    ]

    fig, ax = plt.subplots()

    venn2_unweighted(
        subsets=executed_lines_sets,
        set_labels=executed_lines_names,
        ax=ax,
    )

    fig.canvas.manager.set_window_title(f"Comparison of {experiment_names}")

    plt.show()


if __name__ == "__main__":
    main()

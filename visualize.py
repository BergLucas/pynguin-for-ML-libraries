import matplotlib.pyplot as plt
from utils import load_summary
from functools import reduce
import operator
import argparse


def load_experiment(experiment_path: str) -> tuple[str, int, dict]:
    summary = load_summary(experiment_path)
    return (
        summary["experiment_name"],
        summary["nb_runs"],
        summary["executed_lines_counter"],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiments", nargs="+")

    args = parser.parse_args()

    all_experiment_name, all_nb_runs, all_executed_lines_counter = zip(
        *(load_experiment(experiment_path) for experiment_path in args.experiments)
    )

    total_nb_runs = sum(all_nb_runs)

    lines = sorted(
        reduce(
            operator.or_,
            (
                executed_lines_counter.keys()
                for executed_lines_counter in all_executed_lines_counter
            ),
        ),
        key=lambda line: int(line),
    )

    fig, ax = plt.subplots()

    bottom = [0] * len(lines)
    for experiment_name, executed_lines_counter in zip(
        all_experiment_name, all_executed_lines_counter
    ):
        sorted_executed_lines_counter = [executed_lines_counter[line] for line in lines]
        ax.bar(
            lines,
            sorted_executed_lines_counter,
            label=experiment_name,
            bottom=bottom,
        )
        bottom = [sum(x) for x in zip(bottom, sorted_executed_lines_counter)]

    ax.set_ylim([0, total_nb_runs * 1.1])
    ax.set_xlabel("Line number")
    ax.set_ylabel(f"Number of times the line was executed by a test suite")

    experiment_names = " and ".join(all_experiment_name)

    fig.canvas.manager.set_window_title(f"Visualization of {experiment_names}")

    plt.xticks(rotation=90, fontsize=6)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()

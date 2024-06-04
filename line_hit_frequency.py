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
    parser.add_argument("--no-interactive", action="store_true")
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

    fig, ax = plt.subplots(figsize=(5, 10))

    left = [0] * len(lines)
    for experiment_name, executed_lines_counter in zip(
        all_experiment_name, all_executed_lines_counter
    ):
        sorted_line_hit_frequencies = [
            executed_lines_counter[line] / total_nb_runs for line in lines
        ]
        ax.barh(
            lines,
            sorted_line_hit_frequencies,
            label=experiment_name,
            left=left,
        )
        left = [sum(x) for x in zip(left, sorted_line_hit_frequencies)]

    ax.set_ylabel("Line number")
    ax.set_xlabel("Line hit frequency")
    ax.set_ylim((len(lines) * len(all_experiment_name)) / -20, len(lines) + 5)
    ax.invert_yaxis()

    experiment_names = " and ".join(all_experiment_name)

    title = f"Line hit frequency of {experiment_names}"

    fig.canvas.manager.set_window_title(title)

    plt.xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    plt.yticks(range(0, len(lines), len(lines) // 25))
    plt.legend(loc="upper right")

    if args.no_interactive:
        plt.savefig(
            title.replace(" ", "_") + ".png",
            dpi=300,
            bbox_inches="tight",
        )
    else:
        plt.show()


if __name__ == "__main__":
    main()

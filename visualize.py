import matplotlib.pyplot as plt
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

    first_experiment_name = first_summary["experiment_name"]
    second_experiment_name = second_summary["experiment_name"]
    total_nb_runs = first_summary["nb_runs"] + second_summary["nb_runs"]

    first_executed_lines_counter: dict = first_summary["executed_lines_counter"]
    second_executed_lines_counter: dict = second_summary["executed_lines_counter"]

    lines = sorted(
        first_executed_lines_counter.keys() | second_executed_lines_counter.keys(),
        key=lambda line: int(line),
    )

    first_count = [first_executed_lines_counter[line] for line in lines]
    second_count = [second_executed_lines_counter[line] for line in lines]

    fig, ax = plt.subplots()

    ax.bar(lines, first_count, label=first_experiment_name)
    ax.bar(lines, second_count, label=second_experiment_name, bottom=first_count)

    ax.set_ylim([0, total_nb_runs * 1.1])
    ax.set_xlabel("Line number")
    ax.set_ylabel(f"Number of times the line was executed by a test suite")

    fig.canvas.manager.set_window_title(
        f"Comparison between {first_experiment_name} and {second_experiment_name}"
    )

    plt.xticks(rotation=90, fontsize=6)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()

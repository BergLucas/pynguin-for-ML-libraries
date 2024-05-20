import argparse
import json
import matplotlib.pyplot as plt
from collections import Counter
from pprint import pprint


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_summary")
    parser.add_argument("second_summary")

    args = parser.parse_args()

    with open(args.first_summary, "r") as f:
        first_summary = json.load(f)

    with open(args.second_summary, "r") as f:
        second_summary = json.load(f)

    first_executed_lines_counter: dict = first_summary["executed_lines_counter"]
    second_executed_lines_counter: dict = second_summary["executed_lines_counter"]

    lines = sorted(
        first_executed_lines_counter.keys() | second_executed_lines_counter.keys(),
        key=lambda line: int(line),
    )

    first_count = [first_executed_lines_counter[line] for line in lines]
    second_count = [second_executed_lines_counter[line] for line in lines]

    _, ax = plt.subplots()

    ax.bar(lines, first_count, label=first_summary["experiment_name"])
    ax.bar(
        lines, second_count, label=second_summary["experiment_name"], bottom=first_count
    )

    plt.xticks(rotation=90, fontsize=6)
    plt.legend()

    plt.show()


if __name__ == "__main__":
    main()

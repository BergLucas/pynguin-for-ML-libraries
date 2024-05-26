from utils import load_summary
from pylatex import Tabular
import argparse


def create_table(summaries: list[dict]) -> tuple[tuple, list[tuple]]:
    header = (
        "Experiment",
        "Coverage",
        "Iterations",
        "Total time",
        "Search time",
        "Mutation score",
        "Success",
        "Failure",
        "Timeout",
        "Segmentation fault",
        "Out of memory",
        "Floating point exception",
        "Other crashes",
    )

    data: list[tuple] = []
    for summary in summaries:
        return_code_counter = summary["return_code_counter"]
        success_count = return_code_counter.pop("0", 0)
        failure_count = return_code_counter.pop("1", 0)
        timeout_count = return_code_counter.pop("null", 0)
        segmentation_fault_count = return_code_counter.pop("-11", 0)
        out_of_memory_count = return_code_counter.pop("-9", 0)
        floating_point_exception_count = return_code_counter.pop("-8", 0)
        other_crashes_count = sum(return_code_counter.values())

        data.append(
            (
                summary["experiment_name"],
                f'{summary["mean_coverage"]:.2f}',
                f'{summary["mean_iterations"]:.2f}',
                f'{summary["mean_total_time"]:.2f}',
                f'{summary["mean_search_time"]:.2f}',
                f'{summary["mean_mutation_score"]:.2f}',
                str(success_count),
                str(failure_count),
                str(timeout_count),
                str(segmentation_fault_count),
                str(out_of_memory_count),
                str(floating_point_exception_count),
                str(other_crashes_count),
            )
        )

    return header, data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("experiments", nargs="+")

    args = parser.parse_args()

    header, data = create_table(list(map(load_summary, args.experiments)))

    latex_table = Tabular(f'|{" c |" * len(header)}')
    latex_table.add_hline()
    latex_table.add_row(header)
    latex_table.add_hline()
    for row in data:
        latex_table.add_row(row)
        latex_table.add_hline()

    print(latex_table.dumps())


if __name__ == "__main__":
    main()

from utils import load_summary
from pylatex import Tabular
import argparse


HEADER = (
    "Experiment",
    "Coverage",
    "Iterations",
    "Total time",
    "Search time",
    "Mutation score",
    "Crash test count",
    "Success",
    "Failure",
    "Timeout",
    "Segmentation fault",
    "Out of memory",
    "Floating point exception",
    "Other crashes",
)


def create_table(summaries: list[dict]) -> list[tuple]:
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
                str(summary["crash_test_count"]),
                str(success_count),
                str(failure_count),
                str(timeout_count),
                str(segmentation_fault_count),
                str(out_of_memory_count),
                str(floating_point_exception_count),
                str(other_crashes_count),
            )
        )

    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--except_columns")
    parser.add_argument("experiments", nargs="+")

    args = parser.parse_args()

    data = create_table(list(map(load_summary, args.experiments)))

    if args.except_columns is not None:
        except_columns_names = args.except_columns.split(",")
    else:
        except_columns_names = []

    column_indexes = tuple(
        i for i in range(len(HEADER)) if HEADER[i] not in except_columns_names
    )

    header = tuple(HEADER[i] for i in column_indexes)

    latex_table = Tabular(f'|{" c |" * len(header)}')
    latex_table.add_hline()
    latex_table.add_row(header)
    latex_table.add_hline()
    for row in data:
        latex_table.add_row(tuple(row[i] for i in column_indexes))
        latex_table.add_hline()

    print(latex_table.dumps())


if __name__ == "__main__":
    main()

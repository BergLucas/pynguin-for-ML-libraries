import subprocess
import os
import random
import argparse
import time
import csv


def run_pynguin(
    module_name: str,
    project_path: str,
    report_path: str,
    maximum_search_time: int,
    seed: int,
    create_coverage_report: bool,
    timeout: int,
    *pynguin_args: str,
):
    os.makedirs(report_path, exist_ok=True)

    formatted_pynguin_args = (
        arg.format(report_path=report_path)
        for arg in pynguin_args
    )

    with open(f"{report_path}/seed", "w") as seed_file:
        seed_file.write(f"{seed}")

    with (
        open(f"{report_path}/stdout.log", "w") as stdout_file,
        open(f"{report_path}/stderr.log", "w") as stderr_file,
    ):
        try:
            return_code = subprocess.run(
                [
                    "pynguin",
                    "--module-name", module_name,
                    "--project-path", project_path,
                    "--output-path", report_path,
                    "--report-dir", report_path,
                    "--maximum-search-time", str(maximum_search_time),
                    "--seed", str(seed),
                    "--create-coverage-report", str(create_coverage_report),
                    "--output-variables", "TargetModule", "AlgorithmIterations", "Coverage", "TotalTime", "SearchTime", "LineNos", "MutationScore",
                    "-v",
                    *formatted_pynguin_args,
                ],
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=timeout,
            ).returncode
        except subprocess.TimeoutExpired:
            return_code = None

    with open(f"{report_path}/return_code", "w") as info_file:
        info_file.write(f"{return_code}")


def change_pynguin_branch(pynguin_path: str, branch_name: str):
    subprocess.run(
        ["git", "checkout", branch_name],
        cwd=pynguin_path,
        stdout=subprocess.DEVNULL,
    )


def install_pynguin_dependencies(pynguin_path: str):
    subprocess.run(
        ["pip", "install", "-e", pynguin_path],
        stdout=subprocess.DEVNULL,
    )


def split_args(args: str) -> list[str]:
    return [arg for arg in args.split(" ") if arg]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules-csv-path", default="modules.csv")
    parser.add_argument("--modules-csv-start", default=None)
    parser.add_argument("--modules-csv-end", default=None)
    parser.add_argument("--project-path", default=".")
    parser.add_argument("--pynguin-path", default="pynguin")
    parser.add_argument("--results-path", default="results")
    parser.add_argument("--nb-experiments", type=int, default=30)
    parser.add_argument("--type-tracing", action="store_true")
    parser.add_argument("--maximum-search-time", type=int, default=600)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--create-coverage-report", action="store_true")
    parser.add_argument("--base-seed", type=int, default=time.time_ns())

    args = parser.parse_args()

    modules_csv_path = args.modules_csv_path
    pynguin_path = args.pynguin_path
    project_path = args.project_path
    results_path = args.results_path
    nb_experiments = args.nb_experiments
    maximum_search_time = args.maximum_search_time
    timeout = args.timeout
    create_coverage_report = args.create_coverage_report
    base_seed = args.base_seed

    random.seed(base_seed)

    with open(modules_csv_path, "r") as modules_csv_file:
        modules = [
            (module_name, experiment_name, branch_name, split_args(pynguin_args))
            for module_name, experiment_name, branch_name, pynguin_args in csv.reader(modules_csv_file)
        ]

    modules_start_string = args.modules_csv_start

    if modules_start_string is None:
        modules_start = 0
    else:
        modules_start = int(modules_start_string)

    modules_end_string = args.modules_csv_end

    if modules_end_string is None:
        modules_end = len(modules)
    else:
        modules_end = int(modules_end_string)

    for module_name, experiment_name, branch_name, pynguin_args in modules[modules_start:modules_end]:
            print(f'{experiment_name} : Running {nb_experiments} experiments with "{module_name}" on branch "{branch_name}"')

            change_pynguin_branch(pynguin_path, branch_name)

            install_pynguin_dependencies(pynguin_path)

            for i in range(nb_experiments):
                print(f"Experiment {i}")
                report_path = os.path.join(results_path, experiment_name, str(i))

                seed = random.randrange(0, 2 << 64)

                if os.path.exists(report_path):
                    print("Skipping because the report folder already exists")
                    continue

                run_pynguin(
                    module_name,
                    project_path,
                    report_path,
                    maximum_search_time,
                    seed,
                    create_coverage_report,
                    timeout,
                    *pynguin_args,
                )


if __name__ == "__main__":
    main()

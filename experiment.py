import subprocess
import os
import random
import argparse
import time
import csv
import json
from collections import Counter


def run_pynguin(
    module_name: str,
    project_path: str,
    experiment_path: str,
    maximum_search_time: int,
    timeout: int,
    seed: int,
    *pynguin_args: str,
) -> int | None:
    os.makedirs(experiment_path, exist_ok=True)

    formatted_pynguin_args = (
        arg.format(experiment_path=experiment_path) for arg in pynguin_args
    )

    with open(f"{experiment_path}/seed", "w") as seed_file:
        seed_file.write(f"{seed}")

    with (
        open(f"{experiment_path}/stdout.log", "w") as stdout_file,
        open(f"{experiment_path}/stderr.log", "w") as stderr_file,
    ):
        try:
            return_code = subprocess.run(
                [
                    "pynguin",
                    "--module-name",
                    module_name,
                    "--project-path",
                    project_path,
                    "--output-path",
                    experiment_path,
                    "--report-dir",
                    experiment_path,
                    "--maximum-search-time",
                    str(maximum_search_time),
                    "--seed",
                    str(seed),
                    "--output-variables",
                    "TargetModule",
                    "AlgorithmIterations",
                    "Coverage",
                    "TotalTime",
                    "SearchTime",
                    "LineNos",
                    "MutationScore",
                    "-v",
                    *formatted_pynguin_args,
                ],
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=timeout,
            ).returncode
        except subprocess.TimeoutExpired:
            return_code = None

    with open(f"{experiment_path}/return_code", "w") as info_file:
        info_file.write(f"{return_code}")

    return return_code


def run_coverage(experiment_path: str, module_name: str) -> None:
    (test_file,) = filter(
        lambda name: name.startswith("test_"), os.listdir(experiment_path)
    )

    subprocess.run(
        [
            "coverage",
            "run",
            "--branch",
            "--source",
            module_name,
            "-m",
            "pytest",
            test_file,
        ],
        cwd=experiment_path,
        stdout=subprocess.DEVNULL,
    )

    subprocess.run(
        ["coverage", "json"],
        cwd=experiment_path,
        stdout=subprocess.DEVNULL,
    )


def change_pynguin_branch(pynguin_path: str, branch_name: str) -> None:
    subprocess.run(
        ["git", "checkout", branch_name],
        cwd=pynguin_path,
        stdout=subprocess.DEVNULL,
    )


def install_pynguin_dependencies(pynguin_path: str) -> None:
    subprocess.run(
        ["pip", "install", "-e", pynguin_path],
        stdout=subprocess.DEVNULL,
    )


def split_args(args: str) -> list[str]:
    return [arg for arg in args.split(" ") if arg]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules-csv-path", default="modules.csv")
    parser.add_argument("--modules-csv-start", default=None)
    parser.add_argument("--modules-csv-end", default=None)
    parser.add_argument("--project-path", default=".")
    parser.add_argument("--pynguin-path", default="pynguin")
    parser.add_argument("--results-path", default="results")
    parser.add_argument("--nb-experiments", type=int, default=30)
    parser.add_argument("--base-seed", type=int, default=time.time_ns())

    args = parser.parse_args()

    modules_csv_path = args.modules_csv_path
    pynguin_path = args.pynguin_path
    project_path = args.project_path
    results_path = args.results_path
    nb_experiments = args.nb_experiments
    base_seed = args.base_seed

    random.seed(base_seed)

    with open(modules_csv_path, "r") as modules_csv_file:
        modules = [
            (
                module_name,
                experiment_name,
                branch_name,
                int(maximum_search_time),
                int(timeout),
                split_args(pynguin_args),
            )
            for module_name, experiment_name, branch_name, maximum_search_time, timeout, pynguin_args in csv.reader(
                modules_csv_file
            )
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

    for (
        module_name,
        experiment_name,
        branch_name,
        maximum_search_time,
        timeout,
        pynguin_args,
    ) in modules[modules_start:modules_end]:
        print(
            f'{experiment_name} : Running {nb_experiments} experiments with "{module_name}" on branch "{branch_name}"'
        )

        change_pynguin_branch(pynguin_path, branch_name)

        install_pynguin_dependencies(pynguin_path)

        experiments_path = os.path.join(results_path, experiment_name)

        for i in range(nb_experiments):
            print(f"Experiment {i}")
            experiment_path = os.path.join(experiments_path, str(i))

            seed = random.randrange(0, 2 << 64)

            if os.path.exists(experiment_path):
                print("Skipping because the experiment path already exists")
                continue

            return_code = run_pynguin(
                module_name,
                project_path,
                experiment_path,
                maximum_search_time,
                timeout,
                seed,
                *pynguin_args,
            )

            if return_code == 0:
                run_coverage(experiment_path, module_name)

        print(f"{experiment_name} : Getting statistics")

        all_iterations = []
        all_coverage = []
        all_total_time = []
        all_search_time = []
        all_mutation_score = []
        executed_lines_counter = Counter()
        return_code_counter = Counter()
        for i in range(nb_experiments):
            experiment_path = os.path.join(experiments_path, str(i))

            statistics_path = os.path.join(experiment_path, "statistics.csv")

            coverage_path = os.path.join(experiment_path, "coverage.json")

            return_code_path = os.path.join(experiment_path, "return_code")

            try:
                with open(statistics_path, "r") as f:
                    (statistics,) = csv.DictReader(f)
                    iterations = int(statistics["AlgorithmIterations"])
                    coverage = float(statistics["Coverage"])
                    total_time = int(statistics["TotalTime"])
                    search_time = int(statistics["SearchTime"])
                    mutation_score = float(statistics["MutationScore"])
            except FileNotFoundError:
                iterations = 0
                coverage = 0.0
                total_time = timeout
                search_time = maximum_search_time
                mutation_score = 0.0

            try:
                with open(coverage_path, "r") as f:
                    coverage_data = json.load(f)

                    (file_data,) = coverage_data["files"].values()

                    executed_lines = file_data["executed_lines"]
            except FileNotFoundError:
                executed_lines = []

            with open(return_code_path, "r") as f:
                return_data = f.read()

                if return_data.isdigit():
                    return_code = int(return_data)
                else:
                    return_code = None

            all_iterations.append(iterations)
            all_coverage.append(coverage)
            all_total_time.append(total_time)
            all_search_time.append(search_time)
            all_mutation_score.append(mutation_score)
            executed_lines_counter.update(executed_lines)
            return_code_counter[return_code] += 1

        summary = {
            "nb_experiments": nb_experiments,
            "mean_iterations": sum(all_iterations) / nb_experiments,
            "mean_coverage": sum(all_coverage) / nb_experiments,
            "mean_total_time": sum(all_total_time) / nb_experiments,
            "mean_search_time": sum(all_search_time) / nb_experiments,
            "mean_mutation_score": sum(all_mutation_score) / nb_experiments,
            "executed_lines_counter": executed_lines_counter,
            "return_code_counter": return_code_counter,
        }

        summary_path = os.path.join(experiments_path, "summary.json")

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=4)


if __name__ == "__main__":
    main()

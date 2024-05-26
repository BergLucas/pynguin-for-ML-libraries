import subprocess
import os
import random
import argparse
import time
import csv
import json
import inspect
import importlib
import ast
from collections import Counter


NANOSECONDS_IN_SECOND = 1_000_000_000


def run_pynguin(
    module_name: str,
    project_path: str,
    run_path: str,
    maximum_search_time: int,
    timeout: int,
    seed: int,
    *pynguin_args: str,
) -> int | None:
    os.makedirs(run_path, exist_ok=True)

    formatted_pynguin_args = (arg.format(run_path=run_path) for arg in pynguin_args)

    with open(f"{run_path}/seed", "w") as seed_file:
        seed_file.write(f"{seed}")

    with (
        open(f"{run_path}/stdout.log", "w") as stdout_file,
        open(f"{run_path}/stderr.log", "w") as stderr_file,
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
                    run_path,
                    "--report-dir",
                    run_path,
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

    with open(f"{run_path}/return_code", "w") as info_file:
        info_file.write(f"{return_code}")

    return return_code


def run_coverage(run_path: str, module_path: str) -> None:
    try:
        (test_file,) = filter(
            lambda name: name.startswith("test_"), os.listdir(run_path)
        )
    except ValueError:
        return

    subprocess.run(
        [
            "coverage",
            "run",
            "--branch",
            "--include",
            module_path,
            "-m",
            "pytest",
            test_file,
        ],
        cwd=run_path,
        stdout=subprocess.DEVNULL,
    )

    subprocess.run(
        ["coverage", "json", "--pretty-print"],
        cwd=run_path,
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


def get_lines(node: ast.AST) -> set[int]:
    lines: set[int] = set()

    if hasattr(node, "lineno"):
        lines.add(node.lineno)

    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.mod, ast.stmt, ast.excepthandler, ast.match_case)):
            lines.update(get_lines(child))

    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
        for decorator in node.decorator_list:
            lines.update(get_lines(decorator))

    return lines


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules-csv-path", default="modules.csv")
    parser.add_argument("--modules-csv-start", default=None)
    parser.add_argument("--modules-csv-end", default=None)
    parser.add_argument("--project-path", default=".")
    parser.add_argument("--pynguin-path", default="pynguin")
    parser.add_argument("--results-path", default="results")
    parser.add_argument("--nb-runs", type=int, default=30)
    parser.add_argument("--base-seed", type=int, default=time.time_ns())

    args = parser.parse_args()

    modules_csv_path = args.modules_csv_path
    pynguin_path = args.pynguin_path
    project_path = args.project_path
    results_path = args.results_path
    nb_runs = args.nb_runs
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
            f'{experiment_name} : Doing {nb_runs} runs with "{module_name}" on branch "{branch_name}"'
        )

        change_pynguin_branch(pynguin_path, branch_name)

        install_pynguin_dependencies(pynguin_path)

        experiment_path = os.path.join(results_path, experiment_name)

        module = importlib.import_module(module_name)

        module_path = inspect.getfile(module)

        for i in range(nb_runs):
            print(f"Run {i}")
            run_path = os.path.join(experiment_path, str(i))

            seed = random.randrange(0, 2 << 64)

            if os.path.exists(run_path):
                print("Skipping because the run path already exists")
                continue

            return_code = run_pynguin(
                module_name,
                project_path,
                run_path,
                maximum_search_time,
                timeout,
                seed,
                *pynguin_args,
            )

            if return_code == 0:
                run_coverage(run_path, module_path)

        print(f"{experiment_name} : Getting statistics")

        module_source_code = inspect.getsource(module)

        module_tree = ast.parse(module_source_code)

        lines = get_lines(module_tree)

        all_iterations = []
        all_coverage = []
        all_total_time = []
        all_search_time = []
        all_mutation_score = []
        crash_test_count = 0
        executed_lines_counter = Counter({line: 0 for line in lines})
        return_code_counter = Counter()
        for i in range(nb_runs):
            run_path = os.path.join(experiment_path, str(i))

            statistics_path = os.path.join(run_path, "statistics.csv")

            coverage_path = os.path.join(run_path, "coverage.json")

            return_code_path = os.path.join(run_path, "return_code")

            crash_test_count += len(
                tuple(
                    filter(
                        lambda filename: filename.startswith("crash_test_"),
                        os.listdir(run_path),
                    )
                )
            )

            try:
                with open(statistics_path, "r") as f:
                    (statistics,) = csv.DictReader(f)

                iterations = int(statistics["AlgorithmIterations"])
                coverage = float(statistics["Coverage"])
                total_time = int(statistics["TotalTime"])
                search_time = int(statistics["SearchTime"])
                try:
                    mutation_score = float(statistics["MutationScore"])
                except ValueError:
                    mutation_score = 0.0

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
                try:
                    return_code = int(f.read())
                except ValueError:
                    return_code = None

            all_iterations.append(iterations)
            all_coverage.append(coverage)
            all_total_time.append(total_time)
            all_search_time.append(search_time)
            all_mutation_score.append(mutation_score)
            executed_lines_counter.update(executed_lines)
            return_code_counter[return_code] += 1

        summary = {
            "experiment_name": experiment_name,
            "nb_runs": nb_runs,
            "mean_iterations": sum(all_iterations) / nb_runs,
            "mean_coverage": sum(all_coverage) / nb_runs,
            "mean_total_time": sum(all_total_time) / (nb_runs * NANOSECONDS_IN_SECOND),
            "mean_search_time": sum(all_search_time)
            / (nb_runs * NANOSECONDS_IN_SECOND),
            "mean_mutation_score": sum(all_mutation_score) / nb_runs,
            "crash_test_count": crash_test_count,
            "executed_lines_counter": executed_lines_counter,
            "return_code_counter": return_code_counter,
        }

        summary_path = os.path.join(experiment_path, "summary.json")

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=4)


if __name__ == "__main__":
    main()

#!/bin/sh

requirement_path=$1
modules_csv_path=$2
experiment_name=$3
shift 3 # discard the first 3 arguments
experiment_args=$@

results_folder="./results/$experiment_name"

mkdir -p "$results_folder"

docker build --build-arg REQUIREMENTS_PATH="$requirement_path" --build-arg MODULES_CSV_PATH="$modules_csv_path" -t "$experiment_name" .

docker run -v $results_folder:/app/results "$experiment_name" $@

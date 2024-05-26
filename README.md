# Pynguin for ML libraries

"Pynguin for ML libraries" is a Master Thesis made by [Lucas Berg](https://github.com/BergLucas) with the aim of improving Pynguin for generating tests for machine learning libraries.

## Download

The project can be downloaded using the following command:

```bash
git clone --recurse-submodules https://github.com/BergLucas/pynguin-for-ML-libraries.git
```

## Setting up a development environment

### Requirements

The project requires:

- [Python](https://www.python.org/) == 3.10.4
- [pip](https://pip.pypa.io/en/stable/) == 23.3.1

### Python environment setup

You can setup a Python development environment by running the following commands in the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install matplotlib==3.8.4 matplotlib-venn==0.11.10 PyLaTeX==1.4.2 scipy==1.13.0 coverage==7.5.1 -e ./pynguin
```

## Setting up a Conda development environment

### Requirements

The project requires:

- [Conda](https://conda.io/projects/conda/en/latest/index.html)

### Conda environment setup

You can setup a Conda development environment by running the following commands in the project root:

```bash
conda env create -f environment.yml

conda activate pynguin-for-ML-libraries
```

## Example

This example allows you to carry out an experiment to obtain statistics on an improvement of Pynguin.

### Requirements

This example requires a development environment to be set up.

### Execution

You can execute the example by running the following commands:

```bash
pip install -r requirements/requirements.polars.txt

python experiment.py --modules-csv-path modules/polars.csv --results-path results/polars
```

## Example using Docker

This example allows you to carry out an experiment to obtain statistics on an improvement of Pynguin using Docker.

### Requirements

This example requires:

- [Docker](https://www.docker.com/)

### Execution

You can execute the example by running the following command:

```bash
sh docker_experiment.sh requirements/requirements.polars.txt modules/polars.csv polars
```

## License

All code is licensed for others under a MIT license (see [LICENSE](https://github.com/BergLucas/pynguin-for-ML-libraries/blob/main/LICENSE)).

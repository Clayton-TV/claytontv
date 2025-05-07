## 1. Clone the repository
Start by cloning the repository and navigating to the project directory:
```bash
git clone git@github.com:clayton-tv/claytontv.git
cd claytontv
```

## 2. Create a virtual environment
The project uses Python 3.12. You can either install Python 3.12 on your system or use a version manager like `pyenv` to manage multiple Python versions.

### A. Using `pyenv` (recommended)
Install pyenv if you haven't already.
```bash
curl https://pyenv.run | bash
```

You can check if `pyenv` is installed by running:
```bash
pyenv --version
```

Then, install Python 3.12 using `pyenv`:
```bash
pyenv install 3.12.8
```

Verify the installation shows the correct version, which should be `3.12.8`:
```bash
python --version 
# Should output: Python 3.12.8
```

> Note: The project contains a `.python-version` file, which specifies the Python version to use. If you have `pyenv` installed, it will automatically switch to the specified version when you navigate to the project directory.

You can now skip to Step 3 to install the dependencies.

### B. Using a global Python installation (Not recommended)
First, you will need to install Python 3.12 on your system. You can download it from the official Python website or use a package manager like `apt`, `brew`, or `choco` depending on your operating system.
You can check if Python 3.12 is installed by running:
```bash
python --version
# or
python3 --version
```
If Python 3.12 is installed, you can create a virtual environment using the following command:
```bash
python3.12 -m venv venv
source venv/bin/activate
```

You can now continue to Step 3 to install the dependencies.

## 3. Install dependencies
> Make sure you have activated your virtual environment from Step 2 before running the following commands.

This project uses Poetry for dependency management. Verify that Poetry is installed by running:
```bash
poetry --version # Should show Poetry version 1.8.3 or later
```

### Install Poetry
If you don't have Poetry installed, you can install it as follows.
#### Linux, macOS, or WSL
```bash
curl -sSL https://install.python-poetry.org | python -
```

#### Windows (PowerShell)
> Note: If you have installed Python through the Microsoft Store, replace `py` with `python` in the following command.
```bash
# Windows PowerShell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
 ### Use Poetry to install dependencies
Set up the project environment and install the dependencies:
```bash
poetry env use 3.12
poetry install
poetry run pre-commit install
```

This will:
- Configure poetry to use Python 3.12.
- Install all the dependencies listed in `pyproject.toml`.
- Set up pre-commit hooks for code quality checks.

## 4. Activate the Poetry environment
We use Poe the Poet as a task manager, which helps self-document useful commands.

Start a Poetry shell
```bash
poetry shell
```

List the project commands
```bash
poe
```

## 5. Run the application

## 6. Troubleshooting

## 7. More
By way of documentation, this section details a few key aspects of the repository.

### A. Pre-Commit Hooks
The repository uses pre-commit hooks to enforce code quality checks. 
These run automatically before each commit.
You can find the configuration in the `.pre-commit-config.yaml` file.

If you want to manually check the status of the hooks, you can run:
```bash
pre-commit run --all-files --show-diff-on-failure
```

### Code Formatting and Linting
Ruff is a fast Python linter and code formatter. It is used to enforce code style and catch common errors.

You can run the ruff formatter and linter with:
```bash
poe format
poe lint
```

### Testing
The repository uses pytest for testing. 

You can run the tests using:
```bash
poe test
```
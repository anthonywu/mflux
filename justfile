# justfile for mflux Python 3.10+ project, using 3.13 as recommended maintainer Python as of Jan 2026

set shell := ["bash", "-euc"]

python_version := "3.13"
venv_dir := ".venv"
# Ruff version derives from the pinned dev dependency in pyproject.toml (single source of truth)
ruff_version := `sed -n 's/^    "ruff==\([0-9.]*\)",$/\1/p' pyproject.toml`

# Show all recipes
default:
    @just --list

# Set up the project and run the default tests
all: install test

# Create the virtual environment, install dependencies and pre-commit hooks
install: venv-init ensure-pre-commit
    @echo "🏗️ Installing dependencies and pre-commit hooks..."
    uv sync --python {{ python_version }}
    @echo "✅ Dependencies installed."
    pre-commit install
    @echo "✅ Pre-commit hooks installed."

# Create the Python virtual environment with uv
venv-init: expect-arm64 expect-uv
    @echo "🏗️ Creating virtual environment with recommended uv tool:"
    uv python install --quiet {{ python_version }}
    uv venv --clear --python {{ python_version }}
    @echo "✅ Python {{ python_version }} virtual environment created at {{ venv_dir }}"

# Run ruff linter (read-only; use 'just check' to auto-apply fixes)
lint:
    @echo "🏗️ Running linters (ruff {{ ruff_version }}, pinned via pyproject.toml), your files will not be mutated."
    uvx ruff@{{ ruff_version }} check
    @echo "✅ Linting complete."

# Lint the justfile itself (fails if 'just --fmt' would reformat it)
lint-justfile:
    just --fmt --check

# Run ruff code formatter (mutates files; review your git diffs after)
format:
    @echo "🏗️ Running formatter (ruff {{ ruff_version }}, pinned via pyproject.toml), your files will be changed to comply to formatting configs."
    uvx ruff@{{ ruff_version }} format
    git diff --stat
    @echo "✅ Formatting complete. Please review your git diffs, if any."

# Run pre-commit auto-fixes and formatters on all files
check:
    @echo "🏗️ Running pre-commit linter and formatters on files..."
    pre-commit run --all-files

# Run the default test selection (excludes slow model tests, see addopts in pyproject.toml)
test: _test-run

# Run the suite incl. slow tests, excluding high-memory ones (downloads model weights)
test-all: (_test-run '-m "not high_memory_requirement"')

# Run fast tests only (no image generation)
test-fast: (_test-run "-m fast")

# Run slow tests only (image generation)
test-slow: (_test-run "-m slow")

# Build distribution packages and check sizes
build:
    rm -rf dist/mflux-*
    uv build
    @echo "📦 Artifact sizes (expect < 1MB):"
    du -sh dist/*
    @echo "📦 Largest files in the sdist (should not contain image artifacts):"
    TEMP_DIR=$(mktemp -d -t mflux-dist) && \
    mkdir -p "$TEMP_DIR/this-build" && \
    tar -xzf dist/mflux-*.tar.gz -C "$TEMP_DIR/this-build" && \
    find "$TEMP_DIR/this-build" -type f -exec du -h {} \; | sort -rh | head -n 5

# Remove the virtual environment
clean:
    @echo "🧼 Cleaning up venv."
    rm -rf {{ venv_dir }}
    @echo "✅ Cleaned up venv. Run 'just install' to re-generate."

# --- private helpers ----------------------------------------------------------

# 🖥️ mflux and MLX are known to be compatible with aarch64 Mac and Linux only
[private]
expect-arm64:
    @if [ "{{ arch() }}" != "aarch64" ]; then \
        echo "mflux and MLX is known to be compatible with aarch64 Mac and Linux only. This justfile does not support your machine."; \
        exit 1; \
    fi

# we "expect" uv but should not install it for the user, let user *choose* to trust a third party installer
[private]
expect-uv:
    @if ! command -v uv > /dev/null; then \
        echo "You can use classic python -m venv to setup this project,"; \
        echo "but we officially support using uv for managing this project's environment."; \
        echo ""; \
        echo "Please install uv to continue:"; \
        echo "    https://github.com/astral-sh/uv?tab=readme-ov-file#installation"; \
        exit 1; \
    fi

# assume reasonably pre-commit is a safe dependency given its wide support (e.g. GitHub Actions integration)
[private]
ensure-pre-commit:
    @if ! command -v pre-commit > /dev/null; then \
        echo "pre-commit required for submitting commits before pull requests. Using uv tool to install pre-commit."; \
        uv tool install pre-commit; \
    fi

# shared test runner: locked env incl. dev extras (pinned mlx) for testing
[private]
_test-run args="":
    @echo "🏗️ Syncing locked environment with dev extras..."
    uv sync --all-extras
    @echo "🏗️ Running pytest {{ args }} ..."
    MFLUX_PRESERVE_TEST_OUTPUT=1 uv run --no-sync python -m pytest {{ args }}
    @echo "✅ Tests completed"

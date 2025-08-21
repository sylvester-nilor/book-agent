set -e

if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
fi

echo "Installing dependencies with uv..."
cd src
uv sync

echo "Installing development dependencies..."
uv sync --extra dev

echo "Regenerating requirements.txt from pyproject.toml..."
uv pip compile pyproject.toml --output-file requirements.txt

cd ..

echo "Setting up PYTHONPATH..."
export PYTHONPATH=src

echo "Setting up application-default credentials..."
if ! gcloud auth application-default print-access-token &> /dev/null; then
    echo "Application-default credentials not set up. Please run:"
    echo "gcloud auth application-default login"
    echo ""
    echo "This is needed for local development to access BigQuery/Firestore."
else
    echo "Application-default credentials are set up."
fi

echo "Development environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "source src/.venv/bin/activate"
echo ""
echo "Or use uv run to run commands directly:"
echo "cd src && uv run python main.py"
echo "cd src && uv run pytest"
echo ""
echo "Or run from root with PYTHONPATH=src:"
echo "PYTHONPATH=src python src/main.py"
echo "PYTHONPATH=src pytest"
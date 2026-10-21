# Contributing to Phantom

Thank you for your interest in contributing to Phantom! We welcome contributions ranging from bug fixes and documentation enhancements to parser optimizations and new language proposals.

Please review this guide to get started. All participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Development Environment Setup

Phantom requires **Python ≥ 3.10**.

### 1. Get the source
Clone the repository from wherever you obtained it and `cd` into it.

### 2. Create and Activate a Virtual Environment
```bash
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install in Editable Mode
Install Phantom with development and testing dependencies:
```bash
pip install -e ".[dev]"
```

If you plan to work on or test the LLM generator capabilities (requires Google Gemini), install all optional dependencies:
```bash
pip install -e ".[all]"
```

---

## Running Tests

Phantom uses `pytest` for unit, integration, and round-trip encoding tests.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=phantom --cov-report=term-missing

# Run a specific test module
pytest tests/test_parser.py
```

Ensure all tests pass before submitting a pull request.

---

## Code Quality and Style Guidelines

We enforce consistent formatting and static analysis with `ruff`.

### Code Style Rules
- **Python Version:** Python 3.10+ compatibility.
- **Future Imports:** Every module must begin with `from __future__ import annotations`.
- **Type Annotations:** All functions, methods, and class attributes must be fully type-annotated.
- **Line Length:** Target line length is 100 characters (soft limit).
- **Safe Execution:** **Never** use `eval()`, `exec()`, or dynamic code execution on Phantom instruction data or arguments.
- **Docstrings:** All public modules, classes, and functions must have descriptive Google- or PEP 257-style docstrings.

### Running Linters
```bash
# Run ruff linter
ruff check .

# Automatically apply safe fixes
ruff check --fix .

# Check code formatting
ruff format --check .

# Auto-format code
ruff format .
```

---

## Language Feature Proposals

Phantom maintains a disciplined, specification-first development philosophy. The instruction registry and encoding rules form an authoritative contract for parsers, validators, runtimes, and generators.

If you wish to propose a new instruction, encoding mode, or runtime capability:
1. **Open an Issue First:** Discuss the motivation and use case on GitHub Discussions or Issues.
2. **Draft a Formal Specification:** Write a formal update in accordance with [SPECIFICATION.md](SPECIFICATION.md). Specify the instruction identifier, argument signatures, validation constraints, runtime lifecycle behavior, and error conditions.
3. **Submit the Spec for Review:** Language additions must achieve consensus on grammar design and backward compatibility before implementation code is accepted.
4. **Implement Full Toolchain Support:** Any new instruction requires updates to:
   - `phantom.ir` (AST/IR models)
   - `phantom.grammar` (Instruction registry and argument specs)
   - Parser and serializer
   - Static validator
   - Runtime dispatcher
   - CLI inspect/check outputs
   - Documentation and test suites

---

## Pull Request Process

1. **Create a Topic Branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. **Write Unit Tests:** Ensure every code modification is covered by corresponding unit tests in `tests/`.
3. **Verify Documentation:** If your change modifies or expands functionality, update the relevant documentation in `docs/` and root specifications.
4. **Run Verification:**
   ```bash
   ruff check .
   ruff format --check .
   pytest
   ```
5. **Submit PR:** Provide a clear summary of changes, motivation, and link any related issues.

---

## Security Vulnerabilities

Please **do not** open public GitHub issues for security vulnerabilities. Review our [Security Policy](SECURITY.md) and report concerns privately to `security@phantom-lang.dev`.

---

## Quality gates

Before opening a pull request run:

```bash
ruff check src tests scripts
pytest
python scripts/verify_release.py
```

Documentation that shows command output is checked by `tests/test_examples.py`; if you change CLI output, update the docs and that test together. Do not weaken a test to make it pass.

## Research proposals (including Phantom C)

Proposals touching visibility, detection or observers must follow [docs/research/EXPERIMENTAL_METHOD.md](docs/research/EXPERIMENTAL_METHOD.md). Contributions that provide operational techniques for evading security products or concealing execution from authorized system owners will not be accepted. See [docs/research/PHANTOM_C.md](docs/research/PHANTOM_C.md).

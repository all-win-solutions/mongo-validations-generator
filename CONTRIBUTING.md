# Contributing to mongo_validations_generator

First off, thanks for taking the time to contribute to _mongo_validations_generator_! Your help is welcome and appreciated 🙌

This document outlines the guidelines for contributing to the project.

---

## 🧠 Project Style Guide

This project uses:

- [PEP 8](https://peps.python.org/pep-0008/) for Python style
- [`ruff`](https://docs.astral.sh/ruff/) for linting and formatting
- [`pytest`](https://docs.pytest.org/) for testing

Please ensure that your contributions are formatted and pass type checks before submitting a PR.

---

## ✅ Submitting a Pull Request

Before opening a pull request:

- **Update the version** in `pyproject.toml` and `CHANGELOG.md`. We follow [Semantic Versioning (SemVer)](https://semver.org/):

  - Increment the **patch** version for bug fixes.
  - Increment the **minor** version for new features.
  - Increment the **major** version for breaking changes.

- **Update the changelog** in `CHANGELOG.md`:

  - Add a new `## x.y.z` heading at the top.
  - Clearly list what was added, changed, or fixed.

- **Write tests** for any new behavior or bug fix, ideally in `tests/test_*.py`.

## 🙋 Questions?

Open an issue or start a discussion if you're unsure how to contribute. We're happy to help you get started!

Thanks again for your contributions 💙

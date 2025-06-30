# Contributing to DeepCoderX

We welcome contributions to the DeepCoderX project! This document provides some basic guidelines for developers who want to contribute.

## Development Setup

To get started with development, you will need to clone the repository and set up a virtual environment as described in the [Getting Started](getting_started.md) guide.

## Coding Conventions

Please follow these conventions when writing code for DeepCoderX:

*   **Style:** Follow the PEP 8 style guide for Python code.
*   **Typing:** Use type hints for all function and method signatures.
*   **Docstrings:** Add clear and concise docstrings to all public functions, classes, and methods.
*   **Testing:** When adding new features, please also add corresponding unit tests (see below).

## Submitting Pull Requests

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes.
4.  Add or update tests as needed.
5.  Ensure all tests pass.
6.  Submit a pull request with a clear description of your changes.

## Testing

While the project does not yet have a comprehensive test suite, we are working on adding one. We will be using the `pytest` framework for testing. When you contribute new code, please consider adding unit tests for it in the `tests/` directory.
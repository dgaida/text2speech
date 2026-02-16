# Docstring Style Guide

This project follows the **Google Python Style Guide** for docstrings. This ensures that the documentation is consistent and can be correctly processed by tools like `mkdocstrings`.

## Basic Format

A docstring should contain a short summary, followed by a more detailed description (if necessary), arguments, return values, and raised exceptions.

```python
def function(name: str, age: int = 0) -> bool:
    """Short summary in one sentence.

    A more detailed description explaining what the function does
    and why you should use it.

    Args:
        name (str): The name of the person.
        age (int): The age of the person (default is 0).

    Returns:
        bool: True if the operation was successful, otherwise False.

    Raises:
        ValueError: If the name is empty.
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return True
```

## Classes

Classes should have a docstring immediately below the class definition. The `__init__` method should also be documented.

```python
class Example:
    """Short summary of the class.

    Longer description of the class.
    """

    def __init__(self, value: int):
        """Initializes the class.

        Args:
            value (int): The initialization value.
        """
        self.value = value
```

## Automation

We use `interrogate` to measure docstring coverage. Every public API must be documented.

```bash
# Check docstring coverage
interrogate text2speech/
```

#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    """Run administrative tasks."""

    load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?",
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

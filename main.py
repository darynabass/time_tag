"""Main entry point for the TimeTag application."""

from database.database import create_database


def main():
    """Initialize the application database."""
    create_database()


if __name__ == "__main__":
    main()
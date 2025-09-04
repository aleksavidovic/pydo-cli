import argparse
import sys

def run():
    """
    This is the main entry point for the command-line tool.
    It parses arguments and calls the main logic.
    """
    parser = argparse.ArgumentParser(
        description="A simple command-line tool."
    )
    parser.add_argument(
        "--name",
        default="User",
        help="The name to greet."
    )
    
    # The `sys.argv[1:]` slices off the program name itself.
    args = parser.parse_args(sys.argv[1:])
    
    # Call the main application logic
    main(args.name)

def main(name: str):
    """
    The core logic of the application.
    """
    print(f"Hello, {name}!")

if __name__ == "__main__":
    # This allows running the script directly for testing,
    # e.g., `python src/pydo/main.py --name Test`
    run()


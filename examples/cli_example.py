"""
Claude Code API Wrapper - CLI Example

Usage:
    python cli_example.py "your question"
    python cli_example.py "Hello, Claude!"
"""

import argparse
import requests
import sys

API_URL = "http://localhost:5000"


def ask_claude(prompt: str) -> str:
    """Ask Claude and return the response."""
    response = requests.post(
        f"{API_URL}/ask",
        json={"prompt": prompt}
    )

    if response.status_code != 200:
        return f"Error: {response.text}"

    data = response.json()

    if data["success"]:
        return data["response"]
    else:
        return f"Error: {data['error']}"


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code API CLI Client"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Question to ask Claude"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )

    args = parser.parse_args()

    if args.interactive:
        print("Claude Code API CLI (quit: type 'quit' or 'exit')")
        print("-" * 50)

        while True:
            try:
                prompt = input("\nQuestion> ").strip()

                if prompt.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if not prompt:
                    continue

                print("\nResponse:")
                print(ask_claude(prompt))

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

    elif args.prompt:
        print(ask_claude(args.prompt))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

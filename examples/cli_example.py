"""
Claude Code API Wrapper - CLI 예시

사용법:
    python cli_example.py "질문 내용"
    python cli_example.py "Hello, Claude!"
"""

import argparse
import requests
import sys

API_URL = "http://localhost:5000"


def ask_claude(prompt: str) -> str:
    """Claude에 질문하고 응답을 반환합니다."""
    response = requests.post(
        f"{API_URL}/ask",
        json={"prompt": prompt}
    )

    if response.status_code != 200:
        return f"오류: {response.text}"

    data = response.json()

    if data["success"]:
        return data["response"]
    else:
        return f"오류: {data['error']}"


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code API CLI 클라이언트"
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Claude에게 물어볼 질문"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="대화형 모드로 실행"
    )

    args = parser.parse_args()

    if args.interactive:
        print("Claude Code API CLI (종료: quit 또는 exit)")
        print("-" * 50)

        while True:
            try:
                prompt = input("\n질문> ").strip()

                if prompt.lower() in ["quit", "exit", "q"]:
                    print("종료합니다.")
                    break

                if not prompt:
                    continue

                print("\n응답:")
                print(ask_claude(prompt))

            except KeyboardInterrupt:
                print("\n종료합니다.")
                break

    elif args.prompt:
        print(ask_claude(args.prompt))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

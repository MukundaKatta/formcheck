"""CLI for formcheck."""
import sys, json, argparse
from .core import Formcheck

def main():
    parser = argparse.ArgumentParser(description="FormCheck — AI Personal Trainer. Real-time exercise form correction using pose estimation.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Formcheck()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.learn(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"formcheck v0.1.0 — FormCheck — AI Personal Trainer. Real-time exercise form correction using pose estimation.")

if __name__ == "__main__":
    main()

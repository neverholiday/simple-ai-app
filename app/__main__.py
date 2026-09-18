"""Start the app: `uv run python -m app --use solution` or `--use starter`."""

import argparse

import uvicorn

from app.gaps import CHOICES, load_gaps
from app.main import create_app


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app", description=__doc__)
    parser.add_argument(
        "--use",
        choices=CHOICES,
        required=True,
        help="Which Gaps to run: solution (finished) or starter (the ones you write).",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    app = create_app(load_gaps(args.use))
    print(f"Open http://{args.host}:{args.port}  (Gaps: {args.use})")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

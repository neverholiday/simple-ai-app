from app.gaps import CHOICES


def pytest_addoption(parser):
    parser.addoption(
        "--use",
        choices=CHOICES,
        default="starter",
        help="Which Gaps the Gap tests check: starter (yours, the default) or solution.",
    )

"""pytest options for this test suite."""


def pytest_addoption(parser):
    parser.addoption(
        "--update-golden", action="store_true", default=False,
        help="Rewrite the golden snapshots in tests/golden/ from the tool's current output, instead of "
             "comparing against them. A deliberate act: a snapshot change is a printed-calc change and "
             "needs Micah's review (tests/test_golden.py).",
    )

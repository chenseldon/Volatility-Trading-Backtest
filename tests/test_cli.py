from volbacktest.cli import build_parser


def test_cli_exposes_required_commands() -> None:
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices

    assert set(choices) == {"validate-data", "run", "sweep", "report"}

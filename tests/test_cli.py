"""Light CLI surface tests."""

from etsy_drafter.__main__ import build_parser


def test_parser_has_subcommands():
    parser = build_parser()
    for command in ("draft", "list", "export"):
        try:
            parser.parse_args([command, "--help"])
        except SystemExit:
            pass
        args = parser.parse_args([command] + (["--out", "x"] if command == "export" else []))
        assert args.command == command

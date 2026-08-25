from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "runtime-probe":
        from video_editing_agent.adapters.bootstrap.runtime_probe import main as probe_main

        return probe_main(sys.argv[2:])
    if len(sys.argv) > 1:
        from video_editing_agent.adapters.cli.entrypoint import main as cli_main

        return cli_main(sys.argv[1:])
    from video_editing_agent.adapters.product.tkinter_app import launch

    return launch()


if __name__ == "__main__":
    raise SystemExit(main())

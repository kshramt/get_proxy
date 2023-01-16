#!/usr/bin/python3

import argparse
import collections
import logging
import logging.config
import os
import pathlib
import time
from typing import Any

import pythonjsonlogger.jsonlogger
import uvicorn

import src

from .. import apps

logger = logging.getLogger(__name__)


# class _UtcFormatter(logging.Formatter):
#     converter = time.gmtime
#     default_time_format = "%Y-%m-%dT%H:%M:%S"
#     default_msec_format = "%s.%03dZ"


class _UtcJsonFormatter(pythonjsonlogger.jsonlogger.JsonFormatter):  # type: ignore
    converter = time.gmtime
    default_time_format = "%Y-%m-%dT%H:%M:%S"
    default_msec_format = "%s.%03dZ"


def main(argv: list[str]) -> None:
    args = _parse_argv(argv[1:])
    run(args)


def run(args: argparse.Namespace) -> None:
    log_config = _log_config_of([], level_stderr=args.log_level)
    uvicorn.run(
        apps.app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_config=log_config,
    )


def _parse_argv(argv: list[str]) -> argparse.Namespace:
    logger.debug(dict(argv=argv))
    doc = f"""
    {__file__}
    """

    parser = argparse.ArgumentParser(
        doc, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {src.__version__}"
    )
    parser.add_argument(
        "--log_level",
        default="warning",
        type=lambda x: getattr(logging, x.upper()),  # type: ignore
        help="Set log level.",
    )
    args = parser.parse_args(argv)
    return args


def _log_config_of(
    paths: collections.abc.Sequence[str],
    level_stderr: int = logging.INFO,
    level_path: int = logging.DEBUG,
    version: int = 1,
    disable_existing_loggers: bool = False,
) -> dict[str, Any]:
    for path in paths:
        pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    # fmt = "%(levelname)s\t%(process)d\t%(asctime)s.%(msecs)03d\t%(pathname)s\t%(funcName)s\t%(lineno)d\t%(message)s"
    fmt = "%(levelname)s\t%(process)d\t%(asctime)s\t%(name)s\t%(funcName)s\t%(lineno)d\t%(message)s"
    formatters = dict(
        # tab={
        #     "()": _UtcFormatter,
        #     "format": fmt,
        # },
        json={
            "()": _UtcJsonFormatter,
            "format": fmt,
            "json_ensure_ascii": False,
            "rename_fields": dict(asctime="timestamp", levelname="severity"),
        },
    )
    handlers = dict(
        stderr={
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": level_stderr,
            "stream": "ext://sys.stderr",
        },
        **{
            str(i): {
                "class": "logging.FileHandler",
                "formatter": "json",
                "level": level_path,
                "filename": path,
            }
            for i, path in enumerate(paths)
        },
    )
    log_config = dict(
        version=version,
        disable_existing_loggers=disable_existing_loggers,
        formatters=formatters,
        handlers=handlers,
        root=dict(level=logging.DEBUG, handlers=list(handlers.keys())),
    )
    return log_config

#!/usr/bin/python3

import argparse
import dataclasses
import json
import logging
import sys

__version__ = "1.0.0"
logger = logging.getLogger()


@dataclasses.dataclass
class Platform:
    os: str
    arch: str


def main(argv):
    args = _parse_argv(argv[1:])
    _add_handlers(logger, level_stderr=args.log_level)
    logger.debug(dict(args=args))
    run(args)


def run(args):
    spec = dict(group=dict(), target=dict())
    for platform in (
        Platform(os="linux", arch="amd64"),
        Platform(os="linux", arch="arm64"),
    ):
        ks = []
        for target, image_name in (
            ("test_api", "/test_api"),
            ("prod", ""),
        ):
            k = f"{target}-{platform.os}-{platform.arch}"
            v = {
                "dockerfile": f"Dockerfile",
                "target": target,
                "output": [f"type=docker"],
                "tags": [
                    f"{args.base}{image_name}:{args.sha}-{platform.os}-{platform.arch}"
                ],
                "platforms": [f"{platform.os}/{platform.arch}"],
                "args": dict(arch=platform.arch),
                "cache-from": [
                    f"type=registry,ref={args.base}{image_name}:{args.ref_b64}-{platform.os}-{platform.arch}-cache"
                ],
                "cache-to": [
                    f"type=registry,ref={args.base}{image_name}:{args.ref_b64}-{platform.os}-{platform.arch}-cache,mode=max"
                ],
            }
            spec["target"][k] = v
            ks.append(k)
        spec["group"][f"{platform.os}-{platform.arch}"] = dict(targets=ks)
    json.dump(
        spec,
        sys.stdout,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )


def _parse_argv(argv):
    logger.debug(dict(argv=argv))
    doc = f"""
    {__file__}
    """

    parser = argparse.ArgumentParser(
        doc, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--log_level",
        default="warning",
        type=lambda x: getattr(logging, x.upper()),
        help="Set log level.",
    )
    parser.add_argument("--sha", required=True)
    parser.add_argument("--ref_b64", required=True)
    parser.add_argument("--base", default="ghcr.io/kshramt/get_proxy")
    args = parser.parse_args(argv)
    logger.debug(dict(args=args))
    return args


def _add_handlers(logger, level_stderr=logging.INFO, level_path=logging.DEBUG):
    fmt = logging.Formatter(
        "%(levelname)s\t%(process)d\t%(asctime)s\t%(name)s\t%(funcName)s\t%(lineno)d\t%(message)s"
    )
    import time

    fmt.converter = time.gmtime
    fmt.default_time_format = "%Y-%m-%dT%H:%M:%S"
    fmt.default_msec_format = "%s.%03dZ"

    hdl = logging.StreamHandler(sys.stderr)
    hdl.setFormatter(fmt)
    hdl.setLevel(level_stderr)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(hdl)

    return logger


if __name__ == "__main__":
    main(sys.argv)

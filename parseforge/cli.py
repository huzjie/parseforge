"""Command-line interface for parseforge."""
import argparse
import json

from .config import load_config
from .engine import OmniParser
from .oracle import synthesize_document


def _parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", default=None, help="path to a YAML config")
    ap = argparse.ArgumentParser(prog="parseforge",
                                 description="Omni-modal document parsing engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", parents=[common], help="self-check all backends")
    sub.add_parser("bench", parents=[common], help="run OmniDocBench evaluation")
    p_train = sub.add_parser("train", parents=[common], help="train the mock backend")
    p_train.add_argument("--steps", type=int, default=20)
    p_train.add_argument("--lr", type=float, default=0.025)
    p_parse = sub.add_parser("parse", parents=[common], help="parse a synthetic doc")
    p_parse.add_argument("--doc-id", default="cli-0")
    p_parse.add_argument("--regions", type=int, default=8)
    p_serve = sub.add_parser("serve", parents=[common], help="start the HTTP server")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)
    return ap


def cmd_doctor(args):
    from .doctor import run_doctor
    run_doctor(args.config)


def cmd_bench(args):
    from .bench.omnidocbench import run_bench
    run_bench(args.config)


def cmd_train(args):
    from .train import train
    train(args.config, steps=args.steps, lr=args.lr)


def cmd_parse(args):
    cfg = load_config(args.config)
    parser = OmniParser(cfg)
    doc = synthesize_document(args.doc_id, n_regions=args.regions)
    result = parser.parse(doc)
    print(result.to_json())


def cmd_serve(args):
    from .server import run_server
    cfg = load_config(args.config)
    host = args.host or cfg.serving.host
    port = args.port or cfg.serving.port
    run_server(host, port, cfg)


def main(argv=None):
    args = _parser().parse_args(argv)
    handlers = {
        "doctor": cmd_doctor,
        "bench": cmd_bench,
        "train": cmd_train,
        "parse": cmd_parse,
        "serve": cmd_serve,
    }
    handlers[args.cmd](args)


if __name__ == "__main__":
    main()

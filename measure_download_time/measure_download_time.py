#!/usr/bin/env python3
import asyncio
import base64
import pathlib
import sys

from yapapi import Golem
from yapapi.services import Service
from yapapi.log import enable_default_logger
from yapapi.payload import vm
from yapapi.rest.activity import CommandExecutionError

examples_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))

from utils import build_parser, run_golem_example, TEXT_COLOR_CYAN, TEXT_COLOR_DEFAULT

task_finished_event = asyncio.Event()


class ApiCallService(Service):
    def __init__(self, *args, url: str, outfile: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._url = url
        self._outfile = outfile

    @staticmethod
    async def get_payload():
        return await vm.manifest(
            manifest = open("manifest.json.base64", "r").read(),
            manifest_sig = open("manifest.json.base64.sign.sha256.base64", "r").read(),
            manifest_sig_algorithm = "sha256",
            manifest_cert = open("author.crt.pem.base64", "r").read(),
            min_mem_gib=0.5,
            min_storage_gib=5,
            min_cpu_threads=1,
            capabilities=["inet", "manifest-support"],
        )

    async def run(self):
        script = self._ctx.new_script()

        script.run("/golem/entrypoints/request.sh", self._url)
        script.download_file("/golem/output/output.txt", self._outfile)

        yield script

        result = open(self._outfile, "r").read().strip()
        print(
            f"{TEXT_COLOR_CYAN}"
            f"Golem Network took: {result} seconds to download a file from {self._url}"
            f"{TEXT_COLOR_DEFAULT}"
        )
        task_finished_event.set()


async def main(subnet_tag, url, outfile):
    async with Golem(budget=1.0, subnet_tag=subnet_tag) as golem:
        instance_params = [{"url": url, "outfile": outfile}]
        await golem.run_service(ApiCallService, instance_params=instance_params, num_instances=1)

        await task_finished_event.wait()


if __name__ == "__main__":
    parser = build_parser(
        "Measure time which takes Golem Network to download a file from provided url"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Url with file to download",
    )
    parser.add_argument(
        "--outfile",
        type=str,
        default="output.txt",
        help="Output file with measured time",
    )

    args = parser.parse_args()
    enable_default_logger(log_file="measure_download_time.log")

    run_golem_example(main(subnet_tag=args.subnet_tag, url=args.url, outfile=args.outfile))

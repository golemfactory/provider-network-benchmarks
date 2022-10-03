#!/usr/bin/env python3
import asyncio
from datetime import datetime
import pathlib
import sys

from yapapi import Golem
from yapapi.services import Service
from yapapi.payload import vm

examples_dir = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(examples_dir))

CALLS_PER_SECOND = 10_000
ITERATIONS = 10

from utils import (
    build_parser,
    run_golem_example,
    print_env_info,
)

class ChainlinkExample(Service):
    @staticmethod
    async def get_payload():
        return await vm.manifest(
            manifest = open("manifest.json.base64", "rb").read(),
            manifest_sig = open("manifest.json.base64.sign.sha256.base64", "rb").read(),
            manifest_sig_algorithm = "sha256",
            manifest_cert = open("requestor.crt.pem.base64", "rb").read(),
            min_mem_gib=0.5,
            min_cpu_threads=0.5,
            capabilities=["inet", "manifest-support"],
        )

    async def run(self):
        script = self._ctx.new_script()
        future_result = script.run(
            "/bin/sh",
            "-c",
            f"python /golem/run/chainlink_request.py \
                --batch {CALLS_PER_SECOND} \
                --iterations {ITERATIONS}",
        )
        yield script

        result = (await future_result).stdout
        print(result.strip() if result else "")


async def main(subnet_tag, payment_driver, payment_network):
    async with Golem(
        budget=1.0,
        subnet_tag=subnet_tag,
        payment_driver=payment_driver,
        payment_network=payment_network,
    ) as golem:
        print_env_info(golem)

        cluster = await golem.run_service(ChainlinkExample, num_instances=1)

        while True:
            print(cluster.instances)
            try:
                await asyncio.sleep(10)
            except (KeyboardInterrupt, asyncio.CancelledError):
                break


if __name__ == "__main__":
    parser = build_parser("Chainlink example")
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    parser.set_defaults(log_file=f"chainlink-example-{now}.log")
    args = parser.parse_args()

    run_golem_example(
        main(
            subnet_tag=args.subnet_tag,
            payment_driver=args.payment_driver,
            payment_network=args.payment_network,
        ),
        log_file=args.log_file,
    )

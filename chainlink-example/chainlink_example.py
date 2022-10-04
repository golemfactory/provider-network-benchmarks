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

from utils import (
    build_parser,
    run_golem_example,
    print_env_info,
)

CALLS_PER_SECOND = 100
ITERATIONS = 5

class ChainlinkExample(Service):
    @staticmethod
    async def get_payload():
        return await vm.manifest(
            manifest = open("manifest.json.base64", "r").read(),
            manifest_sig = open("manifest.json.base64.sign.sha256.base64", "r").read(),
            manifest_sig_algorithm = "sha256",
            manifest_cert = open("author.crt.pem.base64", "r").read(),
            min_mem_gib=0.5,
            min_cpu_threads=1,
            capabilities=["inet", "manifest-support"],
        )

    async def run(self):
        script = self._ctx.new_script()
        future_result = script.run(
            "/bin/sh",
            "-c",
            f"python /golem/run/chainlink_request.py \
                --batch {CALLS_PER_SECOND} \
                --iterations {ITERATIONS} \
                --threads 100",
        )
        yield script

        result = (await future_result)
        print("Stdout:")
        result_out = result.stdout
        print(result_out.strip() if result_out else "")
        print("Stderr:")
        result_err = result.stderr
        print(result_err.strip() if result_err else "")

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
    parser = build_parser("Chainlink requests example")
    now = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
    parser.set_defaults(log_file=f"chainlink-requests-yapapi-{now}.log")
    args = parser.parse_args()

    run_golem_example(
        main(
            subnet_tag="testnet",
            payment_driver=args.payment_driver,
            payment_network=args.payment_network,
        ),
        log_file=args.log_file,
    )

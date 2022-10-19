#!/usr/bin/env python3
# chainlink_request.py

import asyncio
import concurrent.futures
from multiprocessing import cpu_count
import argparse
from web3 import Web3
import time
import sys

NUM_CORES = cpu_count()

# AggregatorV3Interface ABI
ABI = '\
    [{\
        "inputs":[],\
        "name":"decimals",\
        "outputs":[{"internalType":"uint8","name":"","type":"uint8"}],\
        "stateMutability":"view",\
        "type":"function"\
    },{\
        "inputs":[],\
        "name":"description",\
        "outputs":[{"internalType":"string","name":"","type":"string"}],\
        "stateMutability":"view",\
        "type":"function"\
    },{\
        "inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],\
        "name":"getRoundData",\
        "outputs":[\
            {"internalType":"uint80","name":"roundId","type":"uint80"},\
            {"internalType":"int256","name":"answer","type":"int256"},\
            {"internalType":"uint256","name":"startedAt","type":"uint256"},\
            {"internalType":"uint256","name":"updatedAt","type":"uint256"},\
            {"internalType":"uint80","name":"answeredInRound","type":"uint80"}\
        ],\
        "stateMutability":"view",\
        "type":"function"\
    },{\
        "inputs":[],\
        "name":"latestRoundData",\
        "outputs":[\
            {"internalType":"uint80","name":"roundId","type":"uint80"},\
            {"internalType":"int256","name":"answer","type":"int256"},\
            {"internalType":"uint256","name":"startedAt","type":"uint256"},\
            {"internalType":"uint256","name":"updatedAt","type":"uint256"},\
            {"internalType":"uint80","name":"answeredInRound","type":"uint80"}\
        ],\
        "stateMutability":"view",\
        "type":"function"\
    },{\
        "inputs":[],\
        "name":"version",\
        "outputs":[{"internalType":"uint256","name":"","type":"uint256"}],\
        "stateMutability":"view",\
        "type":"function"\
    }]'


class Requests:
    def __init__(self, threads, batch_size, iterations, rpc_urls, contract):
        self.threads_size = threads
        self.batch_size = batch_size
        self.iterations = iterations
        self.rpc_urls = rpc_urls
        self.contract = contract

    def chainlink_request(self, iteration: int, batch_iteration: int, rpc_index: int):
        request_time = time.time_ns()

        rpc = self.rpc_urls[rpc_index]

        # Change this to use your own infura ID
        web3 = Web3(Web3.HTTPProvider(rpc))

        # Set up contract instance
        contract = web3.eth.contract(address=self.contract, abi=ABI)
        # Make call to latestRoundData()
        try:
            latestData = contract.functions.latestRoundData().call()
        except Exception as e:
            print(f"{iteration}.{batch_iteration}:\tRPC: {rpc}\tError: {e}")
            return
        
        # accessing 'answer' field
        usd_price = latestData[1] / 100_000_000

        request_time = (time.time_ns() - request_time) / 1_000_000
        print(
            f"{iteration}.{batch_iteration}:\t{request_time}ms\t{usd_price} USD\tRPC: {rpc}"
        )

    async def batch(
        self, executor: concurrent.futures.ThreadPoolExecutor, iteration: int
    ):
        for i in range(self.batch_size):
            rpc_index = i % len(self.rpc_urls)
            executor.submit(
                self.chainlink_request,
                iteration=iteration,
                batch_iteration=i,
                rpc_index=rpc_index,
            )

    async def run(self):
        run_time = time.time_ns()

        with concurrent.futures.ThreadPoolExecutor(self.threads_size) as executor:
            for i in range(self.iterations):
                print(f"{i}:")
                await self.batch(executor, i)
                await asyncio.sleep(1)
            executor.shutdown(wait=True, cancel_futures=False)

        run_time = (time.time_ns() - run_time) / 1_000_000_000
        print(
            f"Run took {run_time}s"
        )

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--batch", default=100, type=int, help="Batch size")
    parser.add_argument(
        "-i", "--iterations", default=5, type=int, help="Number of iterations"
    )
    parser.add_argument(
        "-t", "--threads", default=NUM_CORES, type=int, help="Number of threads"
    )
    # RPC URLs from here https://chainlist.org/chain/1
    parser.add_argument(
        "-r",
        "--rpc",
        default=\
"https://rpc.ankr.com/eth,\
https://cloudflare-eth.com,\
https://eth-mainnet.public.blastapi.io,\
https://eth-rpc.gateway.pokt.network,\
https://api.securerpc.com/v1,\
https://1rpc.io/eth",
        nargs="+",
        type=str,
        help="RPC URLs",
    )
    # Contract address from here https://docs.chain.link/docs/data-feeds/price-feeds/addresses/
    parser.add_argument(
        "-c",
        "--contract",
        default="0x83441C3A10F4D05de6e0f2E849A850Ccf27E6fa7",
        type=str,
        help="Contract address (with 0x prefix)",
    )
    args = parser.parse_args()

    rpc_urls = args.rpc.split(",")

    await Requests(
        args.threads, args.batch, args.iterations, rpc_urls, args.contract
    ).run()


if __name__ == "__main__":
    asyncio.run(main())

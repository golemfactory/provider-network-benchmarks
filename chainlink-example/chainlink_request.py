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
    def __init__(self, threads, batch_size, iterations, rpc, contract):
        self.threads_size = threads
        self.batch_size = batch_size
        self.iterations = iterations
        self.rpc = rpc
        self.contract = contract

    def chainlink_request(self, iteration: int, batch_iteration: int):
        request_time = time.time_ns()

        # Change this to use your own infura ID
        web3 = Web3(Web3.HTTPProvider(self.rpc))

        # Set up contract instance
        contract = web3.eth.contract(address=self.contract, abi=ABI)
        # Make call to latestRoundData()
        latestData = contract.functions.latestRoundData().call()
        # accessing 'answer' field
        usd_price = latestData[1] / 100_000_000

        request_time = (time.time_ns() - request_time) / 1_000_000
        print(
            f"{iteration}.{batch_iteration}:\t{request_time}ms\t USD {usd_price}"
        )

    async def batch(
        self, executor: concurrent.futures.ThreadPoolExecutor, iteration: int
    ):
        for i in range(self.batch_size):
            new_future = executor.submit(
                self.chainlink_request, iteration=iteration, batch_iteration=i
            )

    async def run(self):
        with concurrent.futures.ThreadPoolExecutor(self.threads_size) as executor:
            for i in range(self.iterations):
                print(f"{i}:")
                await self.batch(executor, i)
                await asyncio.sleep(1)
            executor.shutdown(wait=True, cancel_futures=False)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--batch", default=100, type=int, help="Batch size")
    parser.add_argument(
        "-i", "--iterations", default=5, type=int, help="Number of iterations"
    )
    parser.add_argument(
        "-t", "--threads", default=-1, type=int, help="Number of threads"
    )
    # RPC URL from here https://chainlist.org/chain/1
    parser.add_argument(
        "-r", "--rpc", default="https://rpc.ankr.com/eth", type=str, help="RPC URL"
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

    threads_size = NUM_CORES
    if args.threads > 0:
        threads_size = args.threads

    await Requests(
        threads_size, args.batch, args.iterations, args.rpc, args.contract
    ).run()


if __name__ == "__main__":
    asyncio.run(main())

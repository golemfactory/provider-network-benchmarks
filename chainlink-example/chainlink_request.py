#!/usr/bin/env python3
# countasync.py

import asyncio
import argparse
from web3 import Web3
import time
import sys

async def chainlink_request(iteration: int, batch_iteration: int):
    # Change this to use your own infura ID
    web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    # AggregatorV3Interface ABI
    abi = '[{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"description","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint80","name":"_roundId","type":"uint80"}],"name":"getRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"latestRoundData","outputs":[{"internalType":"uint80","name":"roundId","type":"uint80"},{"internalType":"int256","name":"answer","type":"int256"},{"internalType":"uint256","name":"startedAt","type":"uint256"},{"internalType":"uint256","name":"updatedAt","type":"uint256"},{"internalType":"uint80","name":"answeredInRound","type":"uint80"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]'
    # Price Feed address
    addr = '0x83441C3A10F4D05de6e0f2E849A850Ccf27E6fa7'

    # Set up contract instance
    contract = web3.eth.contract(address=addr, abi=abi)
    # Make call to latestRoundData()
    latestData = contract.functions.latestRoundData().call()
    f"{iteration}.{batch_iteration}:\t{latestData}"


async def requests(batch: int, iteration: int):
    # loop = asyncio.get_event_loop()
    tasks = []
    for i in range(batch):
        task = asyncio.create_task(chainlink_request(iteration, i))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    print(results)
    # group = asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    # await loop.run_until_complete(group)

async def request_batches(batch: int, iterations: int):
    global_time = time.time_ns()

    for i in range(iterations):
        batch_time = time.time_ns()
        print(f"Iteration #{i}.")

        results = asyncio.gather(requests(batch, i))
        await asyncio.sleep(1)
        print(results)
        batch_time = time.time_ns() - batch_time
        print(f"Iteration #{i} took: {batch_time} ns.")
    
    global_time = time.time_ns() - global_time
    print(f"All took: {global_time} ns.")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--batch", default=100, type=int, help="Batch size")
    parser.add_argument("-i", "--iterations", default=5, type=int, help="Number of iterations")
    args = parser.parse_args()
    
    batch = args.batch
    iterations = args.iterations
    
    await request_batches(batch, iterations)

if __name__ == "__main__":
    asyncio.run(main())

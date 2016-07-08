#!/usr/bin/env python3


import asyncio
import random
import argparse
import traceback
from contextlib import closing
from pulsar.apps import rpc


async def get_random_integer_online(api_key, range_min, range_max):
    proxy = rpc.JsonProxy("https://api.random.org/json-rpc/1/invoke",
                          data={"apiKey": api_key})

    response = await proxy.generateIntegers(n=1,
                                            min=range_min,
                                            max=range_max)

    return response["random"]["data"][0]


async def get_random_integer_offline(range_min, range_max):
    return random.randint(range_min, range_max)


async def get_random_integer(api_key, range_min, range_max):
    if api_key:
        try:
            number = await get_random_integer_online(api_key,
                                                     range_min,
                                                     range_max)
        except:
            traceback.print_exc()
            number = await get_random_integer_offline(range_min, range_max)
    else:
        number = await get_random_integer_offline(range_min, range_max)

    return number


async def beat(args):
    while True:
        print(await get_random_integer(args.api_key,
                                       args.min,
                                       args.max),
              flush=True)

        await asyncio.sleep(args.interval)


def parse_command_line():
    def check_negative(argument):
        value = int(argument)
        if value < 0:
            raise argparse.ArgumentTypeError("'%s' is not a positive integer"
                                             % (argument,))
        return value

    parser = argparse.ArgumentParser(description="Generates a steady stream "
                                                 "of random integers to the "
                                                 "standard output.")
    parser.add_argument("--api-key",
                        help="RANDOM.ORG API key, for fetching truly random "
                             "numbers")
    parser.add_argument("--min",
                        type=int,
                        help="Lower boundary (defaults to %(default)s)",
                        default=0)
    parser.add_argument("--max",
                        type=int,
                        help="Upper boundary, inclusive (defaults to "
                             "%(default)s)",
                        default=int(1e9))
    parser.add_argument("--interval",
                        type=check_negative,
                        help="Heartbeat interval, in seconds (defaults "
                             "to %(default)s)",
                        default=60*60)

    return parser.parse_args()


def main():
    args = parse_command_line()

    with closing(asyncio.get_event_loop()) as loop:
        loop.run_until_complete(beat(args))


if __name__ == "__main__":
    main()

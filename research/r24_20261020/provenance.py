"""Run identity helpers. Seed allocation is injective over declared bounds.

A project, replicate, random stream and draw index have disjoint mixed-radix
coordinates. This prevents the arithmetic train/evaluation seed collision in the
first development draft. It does not itself prove statistical independence of
pseudorandom generators, nor can it prevent leakage from preprocessing.
"""
from __future__ import annotations


def split_seed(project: int, replicate: int, stream: int, index: int = 0) -> int:
    """Return a unique nonnegative seed smaller than 2**63.

    Bounds: project < 100; replicate < 1_000_000; stream < 16; index < 100_000.
    Streams: 0 initialization, 1 training, 2 validation, 3 evaluation,
    4 process-noise training, 5 process-noise validation, 6 process-noise evaluation,
    7 optimization directions, 8 optimization minibatches, 9 synthetic teacher.
    """
    fields = ((project, 100), (replicate, 1_000_000), (stream, 16), (index, 100_000))
    for value, bound in fields:
        if type(value) is not int or not 0 <= value < bound:
            raise ValueError(f"Seed coordinate must be an integer in [0,{bound})")
    return ((project * 1_000_000 + replicate) * 16 + stream) * 100_000 + index

# Percy Projects

Scientific state, evidence, and reproducible project outputs. The repository's
[project-state contract](PERCY_PROJECTS_README.md) defines how completed,
negative, mixed, and unresolved results are recorded.

## Reproducible project package

| Project | Completed output | Scientific state | Reproduce |
| --- | --- | --- | --- |
| [Math 11](projects/math11/README.md) | Original paper, exact verifier, all candidate data, figures, archive, integrity runner, tests and CI workflow | October 2 computational certificate reproduced. Independent proof/novelty review remains open. | `python -B projects/math11/tools/reproduce.py` |

The [Math 11 state record](projects/math11/state.json) separates its completed
reproduction question from unresolved density and literature questions. Its
original release files remain byte-preserved.

Product and research implementations that already have a canonical repository
continue there. Conference routing does not create duplicate experiments or
replace a submitted scientific result. Execution receipts are coordinated through
[Percy Work](https://github.com/build-the-future-11/Percy-Work).

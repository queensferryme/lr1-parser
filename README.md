# LR1-Parser

This python package implements an LR(1) parser, as a part of the *Compiler Principal* course.
To run the code, you will need [Python](https://www.python.org/) >= 3.8 and [Poetry](https://github.com/python-poetry/poetry).
```shell script
peotry install
python -m lr1-parser
```
The results will be stored in the `./static` directory:
```
static
├── automaton.png --> deterministic finite automaton (DFA)
├── records.txt   --> parsing records
└── tables.txt    --> parsing tables (action & goto)
```
If you'd like to change the grammar or testcases, go to `./lr1-parser/__main__.py`. 
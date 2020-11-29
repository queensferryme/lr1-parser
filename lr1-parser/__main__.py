from .parser import Parser
from .visualization import Visualization

# define an lr(1) grammar
grammar = {
    "non-terminals": ["E", "F", "T"],
    "productions": {
        "E": [("E", "+", "T"), ("E", "-", "T"), ("T",)],
        "F": [("(", "E", ")"), ("num",)],
        "T": [("T", "*", "F"), ("T", "/", "F"), ("F",)],
    },
    "terminals": ["+", "-", "*", "/", "(", ")", "num"],
}

if __name__ == "__main__":
    # construct the extended grammar
    if start_symbol := grammar["non-terminals"][0]:
        new_start_symbol = start_symbol + "'"
        grammar["productions"][new_start_symbol] = [(start_symbol,)]
        grammar["non-terminals"] = [new_start_symbol, *grammar["non-terminals"]]
    # construct the lr(1) parser
    parser = Parser(grammar)
    # visualize results
    Visualization.print_automaton(parser.automaton)
    Visualization.print_parsing_tables(grammar, parser)
    Visualization.print_parsing_records(
        parser.parse(["(", "num", "+", "num", ")", "/", "num"])
    )

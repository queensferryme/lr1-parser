import contextlib
from typing import Any, Dict, List

from graphviz import Digraph

from .automaton import Automaton
from .parser import Parser


class Visualization:
    @classmethod
    def print_automaton(cls, automaton: Automaton) -> None:
        dot = Digraph(graph_attr={"rankdir": "LR"}, node_attr={"shape": "square"})
        for state in range(0, len(automaton.item_sets)):
            dot.node(
                name=str(state),
                label=f"{str(state)}\n"
                + "\l".join(
                    [
                        "".join([item[0], "→", *item[1:]])
                        for item in automaton.item_sets[state]
                    ]
                )
                + "\l",
            )
        for state in automaton.transition:
            for symbol, to in automaton.transition[state].items():
                if to != -1:
                    dot.edge(str(state), str(to), symbol)
        dot.render("static/automaton", format="png", cleanup=True)

    @classmethod
    def print_parsing_records(cls, records: List[tuple]):
        with open("static/records.txt", "wt") as fout:
            with contextlib.redirect_stdout(fout):
                print(f"{'No':10}{'State':20}{'Symbols':30}{'Action'}")
                for index, (states, symbols, string, action) in enumerate(records):
                    print(f"{index:<10d}", end="")
                    print(f"{str(states):20}", end="")
                    print(f"{str(symbols):30}", end="")
                    if action["type"] == "accept":
                        print("ACC")
                    elif action["type"] == "reduction":
                        print(
                            f"{'R ' + ''.join([action['production'][0], '->', *action['production'][1:]]):15}"
                        )
                    else:
                        print(f"{'S' + str(action['state']):15}")

    @classmethod
    def print_parsing_tables(cls, grammar: Dict[str, Any], parser: Parser) -> None:
        with open("static/tables.txt", "wt") as fout:
            with contextlib.redirect_stdout(fout):
                # header
                print(" " * 10, end="")
                print("action", end="")
                print(
                    " " * ((len(grammar["terminals"]) + 1) * 15 - len("action")), end=""
                )
                print("goto")
                print(f"{'No':10}", end="")
                for symbol in [*grammar["terminals"], "$"]:
                    print(f"{symbol:15}", end="")
                for symbol in grammar["non-terminals"][1:]:
                    print(f"{symbol:10}", end="")
                print()
                # body
                for state in range(parser.automaton.n_states):
                    print(f"{state:<10}", end="")
                    for symbol in [*grammar["terminals"], "$"]:
                        if symbol not in parser.action[state]:
                            print(" " * 15, end="")
                        else:
                            action_type = parser.action[state][symbol]["type"]
                            if action_type == "accept":
                                print(f"{'ACC'}", end="")
                            elif action_type == "reduction":
                                production = parser.action[state][symbol]["production"]
                                print(
                                    f"{'R ' + ''.join([production[0], '->', *production[1:]]):15}",
                                    end="",
                                )
                            else:
                                print(
                                    f"{'S' + str(parser.action[state][symbol]['state']):15}",
                                    end="",
                                )
                    for symbol in grammar["non-terminals"][1:]:
                        if parser.goto[state][symbol] == -1:
                            print(" " * 10, end="")
                        else:
                            print(f"{parser.goto[state][symbol]:<10}", end="")
                    print()

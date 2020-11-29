from collections import defaultdict
from typing import Any, Dict, List, Sequence, Union

from .automaton import Automaton


class Parser:
    def __init__(self, grammar: Dict[str, Any]):
        self._dot = "·"
        self._grammar = grammar
        self.action = defaultdict(dict)
        self.automaton = Automaton(grammar)
        self.goto = self.automaton.transition
        self._construct()

    def parse(self, string: Sequence) -> List[tuple]:
        records, states, string, symbols = [], [0], [*string, "$"], [0]
        while True:
            action = self.action[states[-1]][string[0]]
            records.append((states, symbols, string, action))
            if action["type"] == "accept":
                break
            elif action["type"] == "reduction":
                production = action["production"]
                states = states[: 1 - len(production)]
                states.append(self.goto[states[-1]][production[0]])
                symbols = symbols[: 1 - len(production)]
                symbols.append(production[0])
            elif action["type"] == "shift":
                states.append(action["state"])
                symbols.append(string[0])
                string = string[1:]
            else:
                raise ValueError()
        return records

    def _construct(self) -> None:
        """construct the action & goto table of the slr(1) parser"""

        self._first = self._first_set()
        self._follow = self._follow_set()
        for state in range(self.automaton.n_states):
            for item in self.automaton.item_sets[state]:
                # acceptance item
                if (
                    item[0] == self._grammar["non-terminals"][0]
                    and item[-1] == self._dot
                ):
                    self.action[state]["$"] = {"type": "accept"}
                # reduction item
                elif (index := item.index(self._dot)) + 1 == len(item):
                    for symbol in self._follow[item[0]]:
                        self.action[state][symbol] = {
                            "type": "reduction",
                            "production": [*item[:index], *item[index + 1 :]],
                        }
                # shift item
                elif (symbol := item[index + 1]) in self._grammar["terminals"]:
                    self.action[state][symbol] = {
                        "type": "shift",
                        "state": self.automaton.transition[state][symbol],
                    }

    def _first_set(self) -> Dict[Union[str, tuple], set]:
        """construct the first sets of non-terminals & sequences in a given grammar"""

        first = defaultdict(set)
        productions = [
            (key, *value)
            for key in self._grammar["productions"]
            for value in self._grammar["productions"][key]
        ]
        # non-terminals
        while flag := True:
            for production in productions:
                # X -> y..., y \in T
                if (
                    production[1] in self._grammar["terminals"]
                    and production[1] not in first[production[0]]
                ):
                    flag = False
                    first[production[0]].add(production[1])
                # X -> 𝜺
                elif production[1] == "" and production[1] not in first[production[0]]:
                    flag = False
                    first[production[0]].add(production[1])
                elif production[1] in self._grammar["non-terminals"]:
                    # X -> Y..., Y \in NT
                    if new_first := (
                        first[production[1]] - {""} - first[production[0]]
                    ):
                        flag = False
                        first[production[0]].update(new_first)
                    # X -> Y1Y2..., Y1 \in NT, 𝜺 \in FIRST(Y1), Y2 \in NT, 𝜺 \in FIRST(Y2), ...
                    for i in range(1, len(production)):
                        if "" not in first[production[i]]:
                            break
                        elif i + 1 == len(production):
                            flag = False
                            first[production[0]].add("")
                        elif new_first := (
                            first[production[i + 1]] - {""} - first[production[0]]
                        ):
                            flag = False
                            first[production[0]].update(new_first)

            if flag:
                break
        # sequences
        for production in productions:
            for i in range(1, len(production)):
                sequence = production[i:]
                # sequence = y..., y \in T
                if sequence[0] in self._grammar["terminals"]:
                    first[sequence] = {sequence[0]}
                # sequence = Y..., Y \in NT
                else:
                    first[sequence] = first[sequence[0]] - {""}
                    for j in range(len(sequence)):
                        if "" not in first[sequence[j]]:
                            break
                        elif j + 1 == len(sequence):
                            first[sequence].add("")
                        else:
                            first[sequence].update(first[sequence[j + 1]] - {""})
        return first

    def _follow_set(self) -> Dict[str, set]:
        """construct the follow sets of non-terminals in a given grammar"""

        follow = defaultdict(set)
        follow[self._grammar["non-terminals"][0]].add("$")
        while flag := True:
            for production in [
                (key, *value)
                for key in self._grammar["productions"]
                for value in self._grammar["productions"][key]
            ]:
                for i in range(1, len(production)):
                    if production[i] in self._grammar["terminals"]:
                        continue
                    # X -> 𝛼Y
                    elif i + 1 == len(production):
                        if new_follow := (
                            follow[production[0]] - follow[production[i]]
                        ):
                            flag = False
                            follow[production[i]].update(new_follow)
                    # X -> 𝛼Y𝛽
                    elif new_follow := (
                        self._first[production[i + 1 :]] - {""} - follow[production[i]]
                    ):
                        flag = False
                        follow[production[i]].update(new_follow)
                    # X -> 𝛼Y𝛽, 𝜺 \in FIRST(𝛽)
                    elif "" in self._first[production[i + 1 :]] and (
                        new_follow := follow[production[0]] - follow[production[i]]
                    ):
                        flag = False
                        follow[production[i]].update(new_follow)
            if flag:
                return follow

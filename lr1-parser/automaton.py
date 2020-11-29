import itertools
from collections import defaultdict
from typing import Any, Dict, Set


class Automaton:
    """construct an deterministic finite automaton (DFA) for slr(1) grammar parsing"""

    def __init__(self, grammar: Dict[str, Any]):
        self._dot = "·"
        self._grammar = grammar
        self.item_sets = []  # read only
        self.n_states = 0  # read only
        self.transition = defaultdict(dict)  # read only
        self._construct()

    def _closure(self, item_set: Set[tuple]) -> Set[tuple]:
        """construct a closure on a given item set, each closure shall be a node of the automaton"""

        while True:
            new_item_set = set()
            for item in item_set:
                # exclude reduction items
                if (index := item.index(self._dot)) + 1 == len(item):
                    continue
                # exclude terminals
                if (symbol := item[index + 1]) not in self._grammar["non-terminals"]:
                    continue
                # add new items if not present
                for production in self._grammar["productions"][symbol]:
                    if (new_item := (symbol, self._dot, *production)) not in item_set:
                        new_item_set.add(new_item)
            # return if no new items are added in this iteration
            if new_item_set:
                item_set.update(new_item_set)
            else:
                return item_set

    def _construct(self) -> None:
        """construct the automaton for recognizing viable prefixes"""

        # initialize item sets with closure({S'->·S})
        self.item_sets.append(
            self._closure(
                {
                    (
                        start_symbol := self._grammar["non-terminals"][0],
                        self._dot,
                        *self._grammar["productions"][start_symbol][0],
                    )
                }
            )
        )
        # add new item sets and state transitions between them
        while True:
            for state in range(n_states := len(self.item_sets)):
                for symbol in itertools.chain(
                    self._grammar["non-terminals"], self._grammar["terminals"]
                ):
                    self._go(state, symbol)
            if len(self.item_sets) == n_states:
                break
        self.n_states = n_states

    def _go(self, state: int, symbol: str) -> None:
        """construct a state transition, given the current state and input symbol"""

        if symbol in self.transition[state]:
            return
        # create a new item set of the next state
        new_item_set = set()
        for item in self.item_sets[state]:
            # exclude reduction item
            if (index := item.index(self._dot)) + 1 == len(item):
                continue
            # add new items if not present
            if item[index + 1] == symbol:
                new_item_set.add(
                    (*item[:index], item[index + 1], item[index], *item[index + 2 :])
                )
        # check if the item set of next state is empty
        if len(new_item_set := self._closure(new_item_set)) == 0:
            self.transition[state][symbol] = -1
        # add only a new state transition if the node is present
        elif new_item_set in self.item_sets:
            self.transition[state][symbol] = self.item_sets.index(new_item_set)
        # add a new node and state transition in between if not present
        else:
            self.item_sets.append(new_item_set)
            self.transition[state][symbol] = len(self.item_sets) - 1

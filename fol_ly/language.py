from __future__ import annotations

import re


"""This module provides an implementation of first-order languages (which
will be referred to as simply "languages").

Languages are collections of "symbols". In our implementation, a "symbol"
will be a finite, non-empty string that contains no whitespace. For example,
"+", "0", "v1" would be considered valid symbols. 

In our implementation, a "string" of a language is a space-delimited sequence
of symbols. Combining this with the requirement that symbols contain no 
whitespace allows for strings to be properly parsed. For example, 
"( AA v1 ) ( = v1 v2 )" would be a string of 9 symbols.

The symbols of a language can be divided into "logical symbols" and 
"non-logical symbols":
    - Logical symbols are common to all languages. 
    - Non-logical symbols are the constant symbols, functions symbols, and 
    relation symbols that are defined for each particular language.
"""


# The set of logical symbols common to all first order languages.
#   To limit our character set to ASCII, we use:
#       "||" to represent the disjunction symbol (U+2228)
#       "!!" to represent the negation symbol (U+00AC)
#       "AA" to represent the universal quantification symbol (U+2200)
COMMON_SYMBOLS = {"(", ")", "||", "!!", "AA", "="}
# We also use "v1, v2, ..." to represent the variable symbols of all languages
VAR_SYMBOL_RE = r"^v[1-9]\d*$"
# We also define additional logical symbols for shorthand when constructing formulas.
#   To limit our chatacter set to ASCII, we use:
#       "&&" to represent the conjunction symbol (U+2227)
#       "->" to represent the right arrow (U+2192)
#       "<->" to represent the left-right arrow (U+2194)
#       "EE" to represent the existential quantification symbol (U+2203)
SHORTHAND_SYMBOLS = {"&&", "->", "<->", "EE"}


def is_disjoint_sets(*sets: set) -> bool:
    """Return whether the given sets are pairwise disjoint."""
    all_elements = set()
    for s in sets:
        for element in s:
            if element in all_elements:
                return False
        all_elements.update(s)
    return True


class Language:
    """A language of first order logic."""

    # The constant symbols of this language
    _constants: set[str]
    # The function symbols of this language
    _functions: dict[int, set[str]]
    # The relation symbols of this language
    _relations: dict[int, set[str]]

    def __init__(
        self, constants: set, functions: dict[int:set], relations: dict[int:set]
    ):
        """Initialize this language with the given constant, function, and
        relation symbols.

        Each set of symbols must be pairwise disjoint, and also cannot
        include any of the COMMON_SYMBOLS.

        Args:
            constants: A set of strings representing the constant symbols of
                this language.
            functions: A dictionary mapping positive integers to sets
                of function symbols. The key represents the arity of
                the function symbols in the set.
            relations: A dictionary mapping positive integers to sets
                of relation symbols. The key represents the arity of
                the relation symbols in the set.

        Raises:
            ValueError: If any of the dictionaries are ill-formed, or
                any strings in the sets cannot be used as a constant,
                function, or relation symbol.
        """
        if not is_disjoint_sets(constants, *functions.values(), *relations.values()):
            raise ValueError("A symbol appears in more than one set.")

        if not all(
            {Language.is_valid_nonlogical_symbol(symbol) for symbol in constants}
        ):
            raise ValueError("Invalid constant symbol.")

        if not all({isinstance(key, int) and key > 0 for key in functions}):
            raise ValueError("Invalid key in functions.")
        for symbol_set in functions.values():
            if not all(
                {Language.is_valid_nonlogical_symbol(symbol) for symbol in symbol_set}
            ):
                raise ValueError("Invalid function symbol.")

        if not all({isinstance(key, int) and key > 0 for key in relations}):
            raise ValueError("Invalid key in relations.")
        for symbol_set in relations.values():
            if not all(
                {Language.is_valid_nonlogical_symbol(symbol) for symbol in symbol_set}
            ):
                raise ValueError("Invalid relation symbol.")

        self._constants = constants.copy()
        self._functions = {n: functions[n].copy() for n in functions}
        self._relations = {n: relations[n].copy() for n in relations}

    def __repr__(self):
        return "Language(constants=%r,functions=%r,relations=%r)" % (
            self._constants,
            self._functions,
            self._relations,
        )

    def __str__(self):
        function_symbols = [
            f"\t{n}-ary: {self._functions[n]}\n" for n in sorted(self._functions.keys())
        ]
        relation_symbols = [
            f"\t{n}-ary: {self._relations[n]}\n" for n in sorted(self._relations.keys())
        ]
        return (
            f"-Language-\n"
            f"Constants: {self._constants}\n"
            f"Functions:\n"
            f"{''.join(function_symbols)}"
            f"Relations:\n"
            f"{''.join(relation_symbols)}"
        )

    def __eq__(self, other: Language):
        return (
            self._constants == other._constants
            and set(self._functions.keys()) == set(other._functions.keys())
            and set(self._relations.keys()) == set(other._relations.keys())
            and all(
                {self._functions[n] == other._functions[n] for n in self._functions}
            )
            and all(
                {self._relations[n] == other._relations[n] for n in self._relations}
            )
        )

    def is_valid_nonlogical_symbol(symbol: str) -> bool:
        """Return whether the given string can be used as a constant, function,
        or relation symbol of a first order language.
        """
        return (
            isinstance(symbol, str)
            and symbol not in COMMON_SYMBOLS
            and re.search(r"\s", symbol) is None
            and not Language.is_variable_symbol(symbol)
            and symbol not in SHORTHAND_SYMBOLS
        )

    def is_common_symbol(symbol: str) -> bool:
        """Return whether the given symbol is one of the symbols common
        to all first order languages.
        """
        return symbol in COMMON_SYMBOLS

    def is_variable_symbol(symbol: str) -> bool:
        """Return whether the given symbol is a variable symbol."""
        return re.match(VAR_SYMBOL_RE, symbol)

    def is_constant_symbol(self, symbol: str) -> bool:
        """Return whether the given symbol is a constant symbol
        of this language.
        """
        return symbol in self._constants

    def get_function_arity(self, symbol: str) -> int | None:
        """Return the arity of the given function symbol, or None if the given
        symbol is not a function symbol of this language.
        """
        for n in self._functions:
            if symbol in self._functions[n]:
                return n

    def get_relation_arity(self, symbol: str) -> int | None:
        """Return the arity of the given relation symbol, or None if the given
        symbol is not a relation symbol of this language.
        """
        for n in self._relations:
            if symbol in self._relations[n]:
                return n

    def get_variable_index(variable: str) -> int:
        """Given a variable (i.e., a string of the form "vn"), return the int n."""
        if not Language.is_variable_symbol(variable):
            raise ValueError(f"Not a variable: {variable}")
        return int(variable[1:])

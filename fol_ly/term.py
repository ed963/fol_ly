from __future__ import annotations

import abc
import itertools
from typing import override

from fol_ly.language import Language


"""This module provides an implementation of terms in a first order language.

Given a language L, a term of L is a non-empty finite string t of symbols from 
L such that:
    1. t is a variable, or
    2. t is a constant symbol, or
    3. t is the string "f t1 t2 ... tn" where f is an n-ary function symbol of L 
        and each of the ti is a term of L
"""


class Term(abc.ABC):
    """A term of a first order language."""

    language: Language

    def __init__(self, language: Language):
        """Initialize this term of the given language."""
        self.language = language

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        """Return the representation of this term as a string of
        one or more space-delimited symbols.
        """
        pass

    @abc.abstractmethod
    def __eq__(self, other: Term):
        pass

    @abc.abstractmethod
    def get_variable_symbols(self) -> set[str]:
        """Return the set of variable symbols in this term."""
        pass

    @abc.abstractmethod
    def substitute(self, x: str, t: Term) -> Term:
        """Return a new Term instance that is this Term, but with term t substituted
        for variable x (often denoted u[t/x] or u^x_t).

        Args:
            x: A variable of this Term's language
            t: A Term of this Term's language

        Returns:
            A new Term instance obtained by substituting t for x

        Raises:
            ValueError: If given args are invalid
        """
        pass

    @abc.abstractmethod
    def find_substituted_term(self, t: Term, x: str) -> Term | None:
        """If there is some unique term s such that: t is this term with s substituted
        for x, then return s.

        Otherwise, if all terms s satisfy the above, return None.

        Raises:
            ValueError: If there is no term s such that t is this term with s
                substituted for x.
        """
        pass


class VariableTerm(Term):
    """A term consisting of a single variable symbol."""

    variable: str

    def __init__(self, language: Language, variable: str):
        """Initialize this term of the given language.

        Args:
            language: A language.
            variable: A variable symbol of the language.

        Raises:
            ValueError: If given variable is not a variable symbol of the language.
        """
        if not Language.is_variable_symbol(variable):
            raise ValueError(f"Not a variable symbol: {variable}")
        super().__init__(language)
        self.variable = variable

    def __repr__(self):
        return "VariableTerm(language=%r,variable=%r)" % (
            self.language,
            self.variable,
        )

    def __str__(self):
        return self.variable

    def __eq__(self, other: Term):
        return (
            isinstance(other, VariableTerm)
            and self.language == other.language
            and self.variable == other.variable
        )

    @override
    def get_variable_symbols(self) -> set[str]:
        return set([self.variable])

    @override
    def substitute(self, x: str, t: Term) -> Term:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return t if x == self.variable else VariableTerm(self.language, self.variable)

    @override
    def find_substituted_term(self, t: Term, x: str) -> Term | None:
        if self.language != t.language:
            raise ValueError("t must be a term of the same language.")
        if self.variable == x:
            return t
        if self == t:
            return None
        raise ValueError("The given substitution cannot be satisfied by any term.")


class ConstantTerm(Term):
    """A term consisting of a single constant symbol."""

    constant: str

    def __init__(self, language: Language, constant: str):
        """Initialize this term of the given language.

        Args:
            language: A language.
            constant: A constant symbol of the language.

        Raises:
            ValueError: If given constant is not a constant symbol of the
                language.
        """
        if not language.is_constant_symbol(constant):
            raise ValueError(f"Not a constant symbol: {constant}")
        super().__init__(language)
        self.constant = constant

    def __repr__(self):
        return "ConstantTerm(language=%r,constant=%r)" % (
            self.language,
            self.constant,
        )

    def __str__(self):
        return self.constant

    def __eq__(self, other: Term):
        return (
            isinstance(other, ConstantTerm)
            and self.language == other.language
            and self.constant == other.constant
        )

    @override
    def get_variable_symbols(self) -> set[str]:
        return set()

    @override
    def substitute(self, x: str, t: Term) -> Term:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return ConstantTerm(self.language, self.constant)

    @override
    def find_substituted_term(self, t: Term, x: str) -> Term | None:
        if self.language != t.language:
            raise ValueError("t must be a term of the same language.")
        if self == t:
            return None
        raise ValueError("The given substitution cannot be satisfied by any term.")


class FunctionTerm(Term):
    """A term consisting of an n-ary function symbol f, followed by n terms."""

    f: str
    arguments: list[Term]

    def __init__(self, language: Language, f: str, arguments: list[Term]):
        """Initialize this term of the given language.

        Args:
            language: A language.
            f: A function symbol of the language.
            arguments: A list of n terms of the languaga, where n is the arity
                of f.

        Raises:
            ValueError: If invalid arguments are given.
        """
        arity = language.get_function_arity(f)
        if arity is None:
            raise ValueError(f"Not a function symbol: {f}")
        if len(arguments) != arity:
            raise ValueError(
                f"Length of arguments does not match arity of f: "
                f"{len(arguments)} args given for {arity}-ary symbol."
            )
        if any({term.language != language for term in arguments}):
            raise ValueError("Language of term does not match given language.")

        super().__init__(language)
        self.f = f
        self.arguments = arguments.copy()

    def __repr__(self):
        return "FunctionTerm(language=%r,f=%r,arguments=%r)" % (
            self.language,
            self.f,
            self.arguments,
        )

    def __str__(self):
        return f"{self.f} " f"{' '.join([str(arg) for arg in self.arguments])}"

    def __eq__(self, other: Term):
        return (
            isinstance(other, FunctionTerm)
            and self.language == other.language
            and self.f == other.f
            and self.arguments == other.arguments
        )

    @override
    def get_variable_symbols(self) -> set[str]:
        variable_symbols = set()
        variable_symbols.update(
            *[term.get_variable_symbols() for term in self.arguments]
        )
        return variable_symbols

    @override
    def substitute(self, x: str, t: Term) -> Term:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if t.language != self.language:
            raise ValueError(f"t must be a term of the same language.")

        return FunctionTerm(
            self.language, self.f, [term.substitute(x, t) for term in self.arguments]
        )

    @override
    def find_substituted_term(self, t: Term, x: str) -> Term | None:
        if self.language != t.language:
            raise ValueError("t must be a term of the same language.")
        if not isinstance(t, FunctionTerm) or self.f != t.f:
            raise ValueError("The given substitution cannot be satisfied by any term.")
        candidates = [
            self.arguments[i].find_substituted_term(t.arguments[i], x)
            for i in range(len(self.arguments))
        ]
        if all({c is None for c in candidates}):
            return None
        term_candidates = [c for c in candidates if c is not None]
        if len(term_candidates) == 1:
            return term_candidates.pop()
        else:
            raise ValueError("The given substitution cannot be satisfied by any term.")


def string_to_term(language: Language, string: str) -> Term:
    """Given the string representation of a term in the specified language,
    return a Term instance corresponding to the term.

    Args:
        language: A language.
        string: A string containing a space-delimited sequence of
            symbols representing a term in the given language.

    Returns:
        A Term instance corresponding to the given string.

    Raises:
        ValueError: If the given string cannot be parsed into a term.
    """
    if Language.is_variable_symbol(string):
        return VariableTerm(language, string)

    if language.is_constant_symbol(string):
        return ConstantTerm(language, string)

    symbols = string.split()
    if len(symbols) < 2:
        raise ValueError("Cannot parse string into a term.")

    arity = language.get_function_arity(symbols[0])
    if arity is None or len(symbols) < arity + 1:
        raise ValueError("Cannot parse string into a term.")

    if arity == 1:
        return FunctionTerm(
            language, symbols[0], [string_to_term(language, " ".join(symbols[1:]))]
        )

    # split_indices iterates through the possible start indices of t2,...,tn
    for split_indices in itertools.combinations(range(2, len(symbols)), arity - 1):
        try:
            arguments = []
            for i in range(len(split_indices)):
                start = 1 if i == 0 else split_indices[i - 1]
                end = split_indices[i]
                arguments.append(string_to_term(language, " ".join(symbols[start:end])))

            arguments.append(
                string_to_term(language, " ".join(symbols[split_indices[-1] :]))
            )

            return FunctionTerm(language, symbols[0], arguments)

        except ValueError:
            pass

    raise ValueError("Cannot parse string into a term.")

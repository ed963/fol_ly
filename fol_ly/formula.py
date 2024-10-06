from __future__ import annotations

import abc
import itertools
from typing import override

from fol_ly.language import Language
from fol_ly.term import Term, string_to_term


"""This module provides an implementation of formulas in a first order language.

Given a language L, a formula of L is a non-empty finite string P of symbols from 
L such that:
	1. P is the string "= t1 t2", where t1 and t2 are terms of L, or
	2. P is the string "R t1 t2 ... tn", where R is an n-ary relation symbol of L 
        and each of the ti is a term of L, or
	3. P is the string "( !! Q )", where Q is a formula of L, or
	4. P is the string "( Q || R )", where Q and R are formulas of L, or
	5. P is the string "( AA vi ) ( Q )", where vi is a variable and Q is a formula of L

Additionally, define the following shorthands:
    1. "( Q && R )" will mean "( !! ( ( !! Q ) || ( !! R ) ) )"
    2. "( Q -> R )" will mean "( ( !! Q ) || R )"
    3. "( Q <-> R )" will mean "( ( Q -> R ) && ( R -> Q ) )"
    4. "( EE vi ) ( Q )" will mean "( !! ( AA vi ) ( !! Q ) )"
"""


class Formula(abc.ABC):
    """A (well-formed) formula of a first order language."""

    language: Language

    def __init__(self, language: Language):
        """Initialize this formula of the given language."""
        self.language = language

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __str__(self):
        """Return the representation of this formula as a string of
        space-delimited symbols.
        """
        pass

    @abc.abstractmethod
    def __eq__(self, other: Formula):
        pass

    @abc.abstractmethod
    def get_free_variables(self) -> set[str]:
        """Return the set of free variables in this formula."""
        pass

    def variable_free_in_formula(self, variable: str) -> bool:
        """Return whether the given variable is free in this formula."""
        return variable in self.get_free_variables()

    def is_sentence(self) -> bool:
        """Return whether this formula is a sentence.

        A sentence is a formula that has no free variables.
        """
        return len(self.get_free_variables()) == 0

    @abc.abstractmethod
    def substitute(self, x: str, t: Term) -> Formula:
        """Return a new Formula instance that is this Formula, but with term t
        substituted for variable x (often denoted P[t/x] or P^x_t).

        Args:
            x: A variable of this Formula's language
            t: A Term of this Formula's language

        Returns:
            A new Formula instance obtained by substituting t for x

        Raises:
            ValueError: If given args are invalid
        """
        pass

    @abc.abstractmethod
    def is_substitutable(self, x: str, t: Term) -> bool:
        """Given a variable x and term t, return whether t is substitutable
        for x in this formula.

        Args:
            x: A variable of this Formula's language
            t: A Term of this Formula's language

        Returns:
            Whether t is substitutable for x in this formula

        Raises:
            ValueError: If given args are invalid
        """
        pass

    @abc.abstractmethod
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        """If there is some unique term s such that: f is this formula with s substituted
        for x, then return s.

        Otherwise, if all terms s satisfy the above, return None.

        Raises:
            ValueError: If there is no term s such that f is this formula with s
                substituted for x.
        """
        pass


class EqualityFormula(Formula):
    """A formula of the form "= t1 t2", where t1 and t2 are terms."""

    t1: Term
    t2: Term

    def __init__(self, language: Language, t1: Term, t2: Term):
        """Initialize this formula of the given language.

        Args:
            language: A language.
            t1: A term of the language.
            t2: A term of the language.

        Raises:
            ValueError: If invalid arguments are given.
        """
        if t1.language != language or t2.language != language:
            raise ValueError("Language of term does not match given language.")
        super().__init__(language)
        self.t1 = t1
        self.t2 = t2

    def __repr__(self):
        return "EqualityFormula(t1=%r,t2=%r)" % (self.t1, self.t2)

    def __str__(self):
        return f"= {self.t1} {self.t2}"

    def __eq__(self, other: Formula):
        return (
            isinstance(other, EqualityFormula)
            and self.language == other.language
            and self.t1 == other.t1
            and self.t2 == other.t2
        )

    @override
    def get_free_variables(self) -> set[str]:
        return set.union(self.t1.get_variable_symbols(), self.t2.get_variable_symbols())

    @override
    def substitute(self, x: str, t: Term) -> Formula:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return EqualityFormula(
            self.language, self.t1.substitute(x, t), self.t2.substitute(x, t)
        )

    @override
    def is_substitutable(self, x: str, t: Term) -> bool:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return True

    @override
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        if f.language != self.language:
            raise ValueError(f"f must be a formula of the same language.")
        if not isinstance(f, EqualityFormula):
            raise ValueError("The given substitution cannot be satisfied by any term.")
        candidate_one = self.t1.find_substituted_term(f.t1, x)
        candidate_two = self.t2.find_substituted_term(f.t2, x)
        if candidate_one is None:
            return candidate_two
        if candidate_two is None:
            return candidate_one
        if candidate_one == candidate_two:
            return candidate_one
        else:
            raise ValueError("The given substitution cannot be satisfied by any term.")


class RelationFormula(Formula):
    """A formula of the form "R t1 t2 ... tn", where R is an n-ary relation
    symbol and t1 to tn are terms.
    """

    R: str
    arguments: list[Term]

    def __init__(self, language: Language, R: str, arguments: list[Term]):
        """Initialize this formula of the given language.

        Args:
            language: A language.
            R: A relation symbol of the language.
            arguments: A list of n terms of the language, where n is the arity
                of R.

        Raises:
            ValueError: If invalid arguments are given.
        """
        arity = language.get_relation_arity(R)
        if arity is None:
            raise ValueError(f"Not a relation symbol: {R}")
        if len(arguments) != arity:
            raise ValueError(
                f"Length of arguments does not match arity of R: "
                f"{len(arguments)} args given for {arity}-ary symbol."
            )
        if any([term.language != language for term in arguments]):
            raise ValueError("Language of term does not match given language.")

        super().__init__(language)
        self.R = R
        self.arguments = arguments.copy()

    def __repr__(self):
        return "RelationFormula(language=%r,R=%r,arguments=%r)" % (
            self.language,
            self.R,
            self.arguments,
        )

    def __str__(self):
        return f"{self.R} " f"{' '.join([str(arg) for arg in self.arguments])}"

    def __eq__(self, other: Formula):
        return (
            isinstance(other, RelationFormula)
            and self.language == other.language
            and self.R == other.R
            and self.arguments == other.arguments
        )

    @override
    def get_free_variables(self) -> set[str]:
        return set.union(*[term.get_variable_symbols() for term in self.arguments])

    @override
    def substitute(self, x: str, t: Term) -> Formula:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return RelationFormula(
            self.language, self.R, [term.substitute(x, t) for term in self.arguments]
        )

    @override
    def is_substitutable(self, x: str, t: Term) -> bool:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return True

    @override
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        if self.language != f.language:
            raise ValueError("f must be a formula of the same language.")
        if not isinstance(f, RelationFormula) or self.R != f.R:
            raise ValueError("The given substitution cannot be satisfied by any term.")
        candidates = [
            self.arguments[i].find_substituted_term(f.arguments[i], x)
            for i in range(len(self.arguments))
        ]
        if all({c is None for c in candidates}):
            return None
        term_candidates = [c for c in candidates if c is not None]
        if len(term_candidates) == 1:
            return term_candidates.pop()
        else:
            raise ValueError("The given substitution cannot be satisfied by any term.")


class NegationFormula(Formula):
    """A formula of the form "( !! P )" where P is a formula."""

    P: Formula

    def __init__(self, language: Language, P: Formula):
        """Initialize this formula of the given language.

        Args:
            language: A language.
            P: A formula of the language.

        Raises:
            ValueError: If invalid arguments are given.
        """
        if P.language != language:
            raise ValueError("Language of P does not match given language.")
        super().__init__(language)
        self.P = P

    def __repr__(self):
        return "NegationFormula(language=%r,P=%r)" % (self.language, self.P)

    def __str__(self):
        return f"( !! {str(self.P)} )"

    def __eq__(self, other: Formula):
        return (
            isinstance(other, NegationFormula)
            and self.language == other.language
            and self.P == other.P
        )

    @override
    def get_free_variables(self) -> set[str]:
        return self.P.get_free_variables()

    @override
    def substitute(self, x: str, t: Term) -> Formula:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return NegationFormula(self.language, self.P.substitute(x, t))

    @override
    def is_substitutable(self, x: str, t: Term) -> bool:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return self.P.is_substitutable(x, t)

    @override
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        if self.language != f.language:
            raise ValueError("f must be a formula of the same language.")
        if not isinstance(f, NegationFormula):
            raise ValueError("The given substitution cannot be satisfied by any term.")
        return self.P.find_substituted_term(f.P, x)


class DisjunctionFormula(Formula):
    """A formula of the form "( P || Q )" where P and Q are formulas."""

    P: Formula
    Q: Formula

    def __init__(self, language: Language, P: Formula, Q: Formula):
        """Initialize this formula of the given language.

        Args:
            language: A language.
            P: A formula of the language.
            Q: A formula of the language.

        Raises:
            ValueError: If invalid arguments are given.
        """
        if P.language != language or Q.language != language:
            raise ValueError("Language of P or Q does not match given language.")
        super().__init__(language)
        self.P = P
        self.Q = Q

    def __repr__(self):
        return "DisjunctionFormula(language=%r,P=%r,Q=%r)" % (
            self.language,
            self.P,
            self.Q,
        )

    def __str__(self):
        return f"( {str(self.P)} || {str(self.Q)} )"

    def __eq__(self, other: Formula):
        return (
            isinstance(other, DisjunctionFormula)
            and self.language == other.language
            and self.P == other.P
            and self.Q == other.Q
        )

    @override
    def get_free_variables(self) -> set[str]:
        return set.union(self.P.get_free_variables(), self.Q.get_free_variables())

    @override
    def substitute(self, x: str, t: Term) -> Formula:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return DisjunctionFormula(
            self.language, self.P.substitute(x, t), self.Q.substitute(x, t)
        )

    @override
    def is_substitutable(self, x: str, t: Term) -> bool:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return self.P.is_substitutable(x, t) and self.Q.is_substitutable(x, t)

    @override
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        if f.language != self.language:
            raise ValueError(f"f must be a formula of the same language.")
        if not isinstance(f, DisjunctionFormula):
            raise ValueError("The given substitution cannot be satisfied by any term.")
        candidate_one = self.P.find_substituted_term(f.P, x)
        candidate_two = self.Q.find_substituted_term(f.Q, x)
        if candidate_one is None:
            return candidate_two
        if candidate_two is None:
            return candidate_one
        if candidate_one == candidate_two:
            return candidate_one
        else:
            raise ValueError("The given substitution cannot be satisfied by any term.")


class QuantifiedFormula(Formula):
    """A formula of the form "( AA v ) ( P )" where v is a variable symbol
    and P is a formula.
    """

    v: str
    P: Formula

    def __init__(self, language: Language, v: str, P: Formula):
        """Initialize this formula of the given language.

        Args:
            language: A language.
            v: A variable symbol.
            P: A formula of the language.

        Raises:
            ValueError: If invalid arguments are given.
        """
        if P.language != language:
            raise ValueError("Language of P does not match given language.")
        if not Language.is_variable_symbol(v):
            raise ValueError("Not a variable symbol: {v}")
        super().__init__(language)
        self.v = v
        self.P = P

    def __repr__(self):
        return "QuantifiedFormula(language=%r,v=%r,P=%r)" % (
            self.language,
            self.v,
            self.P,
        )

    def __str__(self):
        return f"( AA {str(self.v)} ) ( {str(self.P)} )"

    def __eq__(self, other: Formula):
        return (
            isinstance(other, QuantifiedFormula)
            and self.language == other.language
            and self.v == other.v
            and self.P == other.P
        )

    @override
    def get_free_variables(self) -> set[str]:
        result = self.P.get_free_variables()
        result.discard(self.v)
        return result

    @override
    def substitute(self, x: str, t: Term) -> Formula:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        if x == self.v:
            return QuantifiedFormula(self.language, self.v, self.P)
        else:
            return QuantifiedFormula(self.language, self.v, self.P.substitute(x, t))

    @override
    def is_substitutable(self, x: str, t: Term) -> bool:
        if not Language.is_variable_symbol(x):
            raise ValueError(f"Not a variable symbol: {x}")
        if not t.language == self.language:
            raise ValueError(f"Given term has a different language: {t}")

        return not self.P.variable_free_in_formula(x) or (
            self.v not in t.get_variable_symbols() and self.P.is_substitutable(x, t)
        )

    @override
    def find_substituted_term(self, f: Formula, x: str) -> Term | None:
        if f.language != self.language:
            raise ValueError(f"f must be a formula of the same language.")
        if not isinstance(f, QuantifiedFormula):
            raise ValueError("The given substitution cannot be satisfied by any term.")
        if self.v == x:
            if self == f:
                return None
            raise ValueError("The given substitution cannot be satisfied by any term.")
        return self.P.find_substituted_term(f.P, x)


def get_top_level_logical_connective(symbols: list[str]) -> int:
    """Given a list of symbols representing a formula of the form "( P C Q )" where
    P and Q are formulas and C is one of ||, &&, ->, <->, return the index of C.

    Raises:
        ValueError: If the given symbols cannot be parsed as a formula "( P C Q )".
    """
    binary_logical_connectives = {"||", "&&", "->", "<->"}

    # Number of "(" seen minus number of ")" seen
    difference = 0
    for i in range(len(symbols)):
        if symbols[i] == "(":
            difference += 1
        elif symbols[i] == ")":
            difference -= 1
        elif symbols[i] in binary_logical_connectives and difference == 1:
            break

    if 1 < i < len(symbols) - 2:
        return i
    raise ValueError(f'Symbols cannot be parsed as a formula "( P C Q )": {symbols}')


def create_existential_formula(P: Formula, v: str) -> Formula:
    """Given a formula P and variable v, return a Formula instance that represents
    the existential quantification formula "( EE v ) ( P )".

    Raises:
        ValueError: If the given arguments are invalid.
    """
    return NegationFormula(
        P.language, QuantifiedFormula(P.language, v, NegationFormula(P.language, P))
    )


def create_conjunction_formula(P: Formula, Q: Formula) -> Formula:
    """Given two formulas, P and Q, return a Formula instance that represents their
    conjunction "( P && Q )".

    Raises:
        ValueError: If the given formulas are invalid.
    """
    language = P.language
    return NegationFormula(
        language,
        DisjunctionFormula(
            language, NegationFormula(language, P), NegationFormula(language, Q)
        ),
    )


def create_implication_formula(P: Formula, Q: Formula) -> Formula:
    """Given two formulas, P and Q, return a Formula instance that represents the
    implication formula "( P -> Q )".

    Raises:
        ValueError: If the given formulas are invalid.
    """
    language = P.language
    return DisjunctionFormula(language, NegationFormula(language, P), Q)


def create_equivalence_formula(P: Formula, Q: Formula) -> Formula:
    """Given two formulas, P and Q, return a Formula instance that represents the
    equivalence formula "( P <-> Q )".

    Raises:
        ValueError: If the given formulas are invalid.
    """
    return create_conjunction_formula(
        create_implication_formula(P, Q), create_implication_formula(Q, P)
    )


def string_to_formula(language: Language, string: str) -> Formula:
    """Given the string representation of a formula in the specified language,
    return a Formula instance corresponding to the formula.

    Args:
        language: A language.
        string: A string containing a space-delimited sequence of symbols
            representing a formula in the given language.

    Returns:
        A Formula instance corresponding to the given string.

    Raises:
        ValueError: If the given string cannot be parsed into a formula.
    """
    symbols = string.split()
    if len(symbols) < 2:
        raise ValueError("Cannot parse string into a formula.")

    if symbols[0] == "=":
        # split_index iterates through the possible start indices of t2
        for split_index in range(2, len(symbols)):
            try:
                return EqualityFormula(
                    language,
                    string_to_term(language, " ".join(symbols[1:split_index])),
                    string_to_term(language, " ".join(symbols[split_index:])),
                )
            except ValueError:
                pass

        raise ValueError("Cannot parse string into a formula.")

    arity = language.get_relation_arity(symbols[0])
    if arity is not None and len(symbols) >= arity + 1:
        if arity == 1:
            return RelationFormula(
                language, symbols[0], [string_to_term(language, " ".join(symbols[1:]))]
            )

        # split_indices iterates through the possible start indices of t2,...,tn
        for split_indices in itertools.combinations(range(2, len(symbols)), arity - 1):
            try:
                terms = []
                for i in range(len(split_indices)):
                    start = 1 if i == 0 else split_indices[i - 1]
                    end = split_indices[i]
                    terms.append(string_to_term(language, " ".join(symbols[start:end])))

                terms.append(
                    string_to_term(language, " ".join(symbols[split_indices[-1] :]))
                )

                return RelationFormula(language, symbols[0], terms)

            except ValueError:
                pass

        raise ValueError("Cannot parse string into a formula.")

    if symbols[0] != "(" or symbols[-1] != ")":
        raise ValueError("Cannot parse string into a formula.")

    if symbols[1] == "!!":
        return NegationFormula(
            language, string_to_formula(language, " ".join(symbols[2:-1]))
        )

    if (
        len(symbols) >= 6
        and symbols[1] == "AA"
        and Language.is_variable_symbol(symbols[2])
        and symbols[3] == ")"
        and symbols[4] == "("
    ):
        return QuantifiedFormula(
            language, symbols[2], string_to_formula(language, " ".join(symbols[5:-1]))
        )

    if (
        len(symbols) >= 6
        and symbols[1] == "EE"
        and Language.is_variable_symbol(symbols[2])
        and symbols[3] == ")"
        and symbols[4] == "("
    ):
        return create_existential_formula(
            string_to_formula(language, " ".join(symbols[5:-1])), symbols[2]
        )

    connective_index = get_top_level_logical_connective(symbols)
    connective = symbols[connective_index]

    if connective == "||":
        return DisjunctionFormula(
            language,
            string_to_formula(language, " ".join(symbols[1:connective_index])),
            string_to_formula(language, " ".join(symbols[connective_index + 1 : -1])),
        )
    elif connective == "&&":
        return create_conjunction_formula(
            string_to_formula(language, " ".join(symbols[1:connective_index])),
            string_to_formula(language, " ".join(symbols[connective_index + 1 : -1])),
        )
    elif connective == "->":
        return create_implication_formula(
            string_to_formula(language, " ".join(symbols[1:connective_index])),
            string_to_formula(language, " ".join(symbols[connective_index + 1 : -1])),
        )
    elif connective == "<->":
        return create_equivalence_formula(
            string_to_formula(language, " ".join(symbols[1:connective_index])),
            string_to_formula(language, " ".join(symbols[connective_index + 1 : -1])),
        )

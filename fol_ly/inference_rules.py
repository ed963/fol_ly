from fol_ly.formula import (
    Formula,
    NegationFormula,
    DisjunctionFormula,
    QuantifiedFormula,
)
from pysat import formula, solvers


# ===== Helpers =====


def is_tautology(propositional_formula: formula.Formula) -> bool:
    """Return whether the given propositional formula is a tautology."""
    solver = solvers.Solver()
    return not solver.append_formula(
        formula.Neg(propositional_formula), no_return=False
    )


def is_propositional_consequence(
    Gamma: set[formula.Formula], theta: formula.Formula
) -> bool:
    """Return whether the propositional formula theta is a propositional consequence of the
    set of propositional formulas Gamma.

    In other words, return true iff: Every truth assignment that satisfies every
    propositional formula in Gamma also satisfies theta.
    """
    if len(Gamma) == 0:
        return is_tautology(theta)
    else:
        return is_tautology(formula.Implies(formula.And(*Gamma), theta))


# ===== Propositional Consequence =====


def is_propositional_consequence_inference_rule(
    Gamma: set[Formula], theta: Formula
) -> bool:
    """Return whether (Gamma, theta) is an instance of the propositional consequence
    inference rule.

    Raises:
        ValueError: If given args are invalid.
    """
    if len(Gamma) > 0:
        check_language = next(iter(Gamma)).language
        for f in Gamma:
            if f.language != check_language:
                raise ValueError("All given formulas must be of the same language.")

    return is_propositional_consequence(
        {f.convert_to_propositional_formula() for f in Gamma},
        theta.convert_to_propositional_formula(),
    )


# ====== Quantifier Rules =====


def is_universal_quantifier_inference_rule(Gamma: set[Formula], theta: Formula) -> bool:
    """Return whether (Gamma, theta) is an instance of the universal quantifier
    inference rule.

    Raises:
        ValueError: If the given args are invalid.
    """
    if len(Gamma) != 1:
        return False

    gamma = next(iter(Gamma))
    if gamma.language != theta.language:
        raise ValueError("All given formulas must be of the same language.")

    if not isinstance(gamma, DisjunctionFormula) or not isinstance(
        gamma.P, NegationFormula
    ):
        return False

    psi = gamma.P.P
    phi = gamma.Q

    if not isinstance(theta, DisjunctionFormula) or not isinstance(
        theta.P, NegationFormula
    ):
        return False

    if theta.P.P != psi:
        return False

    if not isinstance(theta.Q, QuantifiedFormula):
        return False

    return theta.Q.P == phi and not psi.variable_free_in_formula(theta.Q.v)


def is_existential_quantifier_inference_rule(
    Gamma: set[Formula], theta: Formula
) -> bool:
    """Return whether (Gamma, theta) is an instance of the existential quantifier
    inference rule.

    Raises:
        ValueError: If the given args are invalid.
    """
    if len(Gamma) != 1:
        return False

    gamma = next(iter(Gamma))
    if gamma.language != theta.language:
        raise ValueError("All given formulas must be of the same language.")

    if not isinstance(gamma, DisjunctionFormula) or not isinstance(
        gamma.P, NegationFormula
    ):
        return False

    phi = gamma.P.P
    psi = gamma.Q

    if not isinstance(theta, DisjunctionFormula) or not isinstance(
        theta.P, NegationFormula
    ):
        return False

    if (
        not isinstance(theta.P.P, NegationFormula)
        or not isinstance(theta.P.P.P, QuantifiedFormula)
        or not isinstance(theta.P.P.P.P, NegationFormula)
        or theta.P.P.P.P.P != phi
    ):
        return False

    return theta.Q == psi and not psi.variable_free_in_formula(theta.P.P.P.v)

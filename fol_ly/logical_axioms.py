from fol_ly.language import Language
from fol_ly.term import Term, VariableTerm, FunctionTerm
from fol_ly.formula import (
    Formula,
    EqualityFormula,
    RelationFormula,
    QuantifiedFormula,
    create_conjunction_formula,
    create_implication_formula,
    create_existential_formula,
)


# ===== Equality Axioms =====


def create_reflexivity_axiom(language: Language, x: str) -> Formula:
    """Given a variable, return a Formula instance that represents the reflexivity
    axiom involving the variable.

    Args:
        language: A language.
        x: A variable.

    Returns:
        The formula "= x x"

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    return EqualityFormula(
        language, VariableTerm(language, x), VariableTerm(language, x)
    )


def create_conjunction_of_equalities(
    language: Language, variable_pairs: list[tuple[str, str]]
) -> Formula:
    """Given n 2-tuples of variables [t1, t2, ..., tn], return the formula formed by
    creating an Equality formula from each tuple, and taking the conjunction of the
    Equality formulas, i.e,

        ( ... ( = t1[0] t1[1] && = t2[0] t2[1] ) && = t3[0] t3[1] ) && ... ) && = tn[0] tn[1] )

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    if len(variable_pairs) < 1:
        raise ValueError("variable_pairs must contain at least one tuple.")

    if not all({len(tup) == 2 for tup in variable_pairs}):
        raise ValueError("variable_pairs must be a list of 2-tuples.")

    conjunctions = EqualityFormula(
        language,
        VariableTerm(language, variable_pairs[0][0]),
        VariableTerm(language, variable_pairs[0][1]),
    )

    for pair in variable_pairs[1:]:
        conjunctions = create_conjunction_formula(
            conjunctions,
            EqualityFormula(
                language,
                VariableTerm(language, pair[0]),
                VariableTerm(language, pair[1]),
            ),
        )

    return conjunctions


def create_function_substitution_axiom(
    language: Language, variable_pairs: list[tuple[str, str]], f: str
) -> Formula:
    """Given n pairs of variables and an n-ary function symbol of the given language,
    return a Formula instance that represents the function substitution axiom
    involving the given variables and function symbol.

    Args:
        language: A language.
        variable_pairs: A list of 2-tuples [t1, t2, ..., tn], where each ti is a
            pair of variables.
        f: An n-ary function symbol of the given language.

    Returns:
        A Formula instance:

            ( ( ... ( = t1[0] t1[1] && = t2[0] t2[1] ) && = t3[0] t3[1] ) && ... ) && = tn[0] tn[1] ) ->
              = f t1[0] ... tn[0] f t1[1] ... tn[1] )

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    conjunctions = create_conjunction_of_equalities(language, variable_pairs)
    functions = EqualityFormula(
        language,
        FunctionTerm(
            language, f, [VariableTerm(language, pair[0]) for pair in variable_pairs]
        ),
        FunctionTerm(
            language, f, [VariableTerm(language, pair[1]) for pair in variable_pairs]
        ),
    )

    return create_implication_formula(conjunctions, functions)


def create_relation_substitution_axiom(
    language: Language, variable_pairs: list[tuple[str, str]], R: str
) -> Formula:
    """Given n pairs of variables and an n-ary relation symbol of the given language,
    return a Formula instance that represents the relation substitution axiom
    involving the given variables and relation symbol.

    Args:
        language: A language.
        variable_pairs: A list of 2-tuples [t1, t2, ..., tn], where each ti is a pair
            of variables.
        R: An n-ary relation symbol of the given language.

    Returns:
        A Formula instance:

            ( ( ... ( = t1[0] t1[1] && = t2[0] t2[1] ) && = t3[0] t3[1] ) && ... ) && = tn[0] tn[1] ) ->
              ( R t1[0] ... tn[0] -> R t1[1] ... tn[1] ) )

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    conjunctions = create_conjunction_of_equalities(language, variable_pairs)
    relations = create_implication_formula(
        RelationFormula(
            language, R, [VariableTerm(language, pair[0]) for pair in variable_pairs]
        ),
        RelationFormula(
            language, R, [VariableTerm(language, pair[1]) for pair in variable_pairs]
        ),
    )

    return create_implication_formula(conjunctions, relations)


# ===== Quantifier Axioms =====


def create_universal_instantiation_axiom(
    language: Language, P: Formula, x: str, t: Term
) -> Formula:
    """Given a formula P, variable x, and term t, return a Formula instance that
    represents the universal instantiation axiom involving P, x, and t.

    t must be substitutable for x in P.

    Args:
        language: A language.
        P: A formula of the given language.
        x: A variable.
        t: A term of the given language.

    Returns:
        A Formula instance ( ( AA x ) ( P ) -> P^x_t ).

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    if not P.is_substitutable(x, t):
        raise ValueError(f"t must be substitutable for x in P.")

    return create_implication_formula(
        QuantifiedFormula(language, x, P), P.substitute(x, t)
    )


def create_existential_generalization_axiom(
    language: Language, P: Formula, x: str, t: Term
) -> Formula:
    """Given a formula P, variable x, and term t, return a Formula instance that
    represents the existential generalization axiom involving P, x, and t.

    t must be substitutable for x in P.

    Args:
        language: A language.
        P: A formula of the given language.
        x: A variable.
        t: A term of the given language.

    Returns:
        A Formula instance ( P^x_t -> ( EE x ) ( P ) ).

    Raises:
        ValueError: If any of the arguments are invalid.
    """
    if not P.is_substitutable(x, t):
        raise ValueError(f"t must be substitutable for x in P.")

    return create_implication_formula(
        P.substitute(x, t), create_existential_formula(P, x)
    )

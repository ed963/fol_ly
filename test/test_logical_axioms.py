import unittest

from fol_ly.language import Language
from fol_ly.term import VariableTerm, ConstantTerm, FunctionTerm
from fol_ly.formula import (
    EqualityFormula,
    RelationFormula,
    QuantifiedFormula,
    string_to_formula,
)
from fol_ly.logical_axioms import (
    create_reflexivity_axiom,
    create_function_substitution_axiom,
    create_relation_substitution_axiom,
    create_universal_instantiation_axiom,
    create_existential_generalization_axiom,
    is_reflexivity_axiom,
    is_function_substitution_axiom,
    is_relation_substitution_axiom,
    is_universal_instantiation_axiom,
    is_existential_generalization_axiom,
)


class TestLogicalAxioms(unittest.TestCase):
    def setUp(self):
        self.language = Language({"a", "b", "c"}, {1: {"f1"}, 3: {"f3"}}, {2: {"r2"}})
        self.term1 = ConstantTerm(self.language, "a")
        self.term2 = VariableTerm(self.language, "v4")
        self.term3 = FunctionTerm(self.language, "f1", [self.term1])
        self.term4 = FunctionTerm(
            self.language, "f3", [self.term1, self.term2, self.term3]
        )
        self.relation_formula = RelationFormula(
            self.language, "r2", [self.term1, self.term2]
        )
        self.equality_formula = EqualityFormula(
            self.language,
            self.term3,
            self.term4,
        )
        self.quantified_formula = QuantifiedFormula(
            self.language, "v1", self.equality_formula
        )

    def test_create_reflexivity_axiom(self):
        self.assertEqual(str(create_reflexivity_axiom(self.language, "v2")), "= v2 v2")

    def test_is_reflexivity_axiom_true(self):
        self.assertTrue(
            is_reflexivity_axiom(create_reflexivity_axiom(self.language, "v2"))
        )

    def test_is_reflexivity_axiom_false(self):
        self.assertFalse(
            is_reflexivity_axiom(string_to_formula(self.language, "= a a"))
        )

    def test_create_function_substitution_axiom(self):
        self.assertEqual(
            str(
                create_function_substitution_axiom(self.language, [("v1", "v2")], "f1")
            ),
            "( ( !! = v1 v2 ) || = f1 v1 f1 v2 )",
        )
        self.assertEqual(
            str(
                create_function_substitution_axiom(
                    self.language,
                    [("v11", "v12"), ("v21", "v22"), ("v31", "v32")],
                    "f3",
                )
            ),
            "( ( !! ( !! ( ( !! ( !! ( ( !! = v11 v12 ) || ( !! = v21 v22 ) ) ) ) || ( !! = v31 v32 ) ) ) ) || = f3 v11 v21 v31 f3 v12 v22 v32 )",
        )

    def test_is_function_substitution_axiom_true(self):
        self.assertTrue(
            is_function_substitution_axiom(
                create_function_substitution_axiom(self.language, [("v1", "v2")], "f1")
            )
        )
        self.assertTrue(
            is_function_substitution_axiom(
                create_function_substitution_axiom(
                    self.language,
                    [("v11", "v12"), ("v21", "v22"), ("v31", "v32")],
                    "f3",
                )
            )
        )

    def test_is_function_substitution_axiom_false(self):
        self.assertFalse(
            is_function_substitution_axiom(
                create_relation_substitution_axiom(
                    self.language, [("v11", "v12"), ("v21", "v22")], "r2"
                )
            )
        )
        self.assertFalse(
            is_function_substitution_axiom(
                string_to_formula(
                    self.language, "( = v1 v2 -> = f3 v1 v1 v1 f3 v2 v1 v1 )"
                )
            )
        )

    def test_create_relation_substitution_axiom(self):
        self.assertEqual(
            str(
                create_relation_substitution_axiom(
                    self.language, [("v11", "v12"), ("v21", "v22")], "r2"
                )
            ),
            "( ( !! ( !! ( ( !! = v11 v12 ) || ( !! = v21 v22 ) ) ) ) || ( ( !! r2 v11 v21 ) || r2 v12 v22 ) )",
        )

    def test_is_relation_substitution_axiom_true(self):
        self.assertTrue(
            is_relation_substitution_axiom(
                create_relation_substitution_axiom(
                    self.language, [("v11", "v12"), ("v21", "v22")], "r2"
                )
            )
        )

    def test_is_relation_substitution_axiom_false(self):
        self.assertFalse(
            is_relation_substitution_axiom(
                create_function_substitution_axiom(
                    self.language,
                    [("v11", "v12"), ("v21", "v22"), ("v31", "v32")],
                    "f3",
                )
            )
        )
        self.assertFalse(
            is_relation_substitution_axiom(
                string_to_formula(
                    self.language,
                    "( ( = v11 v12 && = v21 v22 ) -> ( r2 v11 v12 -> r2 v21 v22 ) )",
                )
            )
        )

    def test_create_universal_instantiation_axiom(self):
        self.assertEqual(
            str(
                create_universal_instantiation_axiom(
                    self.language, self.relation_formula, "v4", self.term3
                )
            ),
            "( ( !! ( AA v4 ) ( r2 a v4 ) ) || r2 a f1 a )",
        )

    def test_is_universal_instantiation_axiom_true(self):
        self.assertTrue(
            is_universal_instantiation_axiom(
                create_universal_instantiation_axiom(
                    self.language, self.relation_formula, "v4", self.term3
                )
            )
        )

    def test_is_universal_instantiation_axiom_false(self):
        self.assertFalse(
            is_universal_instantiation_axiom(
                create_existential_generalization_axiom(
                    self.language, self.equality_formula, "v4", self.term1
                )
            )
        )
        self.assertFalse(
            is_universal_instantiation_axiom(
                string_to_formula(
                    self.language, "( ( AA v1 ) ( = v1 v1 ) -> = v1 f1 v1 )"
                )
            )
        )

    def test_create_existential_generalization_axiom(self):
        self.assertEqual(
            str(
                create_existential_generalization_axiom(
                    self.language, self.equality_formula, "v4", self.term1
                )
            ),
            "( ( !! = f1 a f3 a a f1 a ) || ( !! ( AA v4 ) ( ( !! = f1 a f3 a v4 f1 a ) ) ) )",
        )

    def test_is_existential_generalization_axiom_true(self):
        self.assertTrue(
            is_existential_generalization_axiom(
                create_existential_generalization_axiom(
                    self.language, self.equality_formula, "v4", self.term1
                )
            )
        )

    def test_is_existential_generalization_axiom_false(self):
        self.assertFalse(
            is_existential_generalization_axiom(
                create_universal_instantiation_axiom(
                    self.language, self.relation_formula, "v4", self.term3
                )
            )
        )
        self.assertFalse(
            is_existential_generalization_axiom(
                string_to_formula(
                    self.language, "( = f1 a v1 -> ( EE v1 ) ( = v2 v1 ) )"
                )
            )
        )


if __name__ == "__main__":
    unittest.main()

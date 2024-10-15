import unittest

from fol_ly.language import Language
from fol_ly.formula import string_to_formula
from fol_ly.inference_rules import (
    is_propositional_consequence_inference_rule,
    is_universal_quantifier_inference_rule,
    is_existential_quantifier_inference_rule,
)


class TestInferenceRules(unittest.TestCase):
    def setUp(self):
        self.language = Language({"a", "b", "c"}, {1: {"f1"}, 3: {"f3"}}, {2: {"r2"}})

    def test_is_propositional_consequence_inference_rule_true_modus_ponens(self):
        Gamma = {
            string_to_formula(self.language, "( r2 v1 v2 -> ( = v1 a && = v2 b ) )"),
            string_to_formula(self.language, "r2 v1 v2"),
        }
        theta = string_to_formula(self.language, "( = v1 a && = v2 b )")
        self.assertTrue(is_propositional_consequence_inference_rule(Gamma, theta))

    def test_is_propositional_consequence_inference_rule_true_tautology(self):
        Gamma = {}
        theta = string_to_formula(self.language, "( ( r2 v1 v2 && = v1 a ) -> = v1 a )")
        self.assertTrue(is_propositional_consequence_inference_rule(Gamma, theta))

    def test_is_propositional_consequence_inference_rule_true_vaccuous(self):
        Gamma = {
            string_to_formula(self.language, "r2 v1 v2"),
            string_to_formula(self.language, "( = v1 v2 || r2 f1 v3 f1 v4 )"),
            string_to_formula(self.language, "( ( !! r2 v1 v2 ) && ( !! = v1 v2 ) )"),
        }
        theta = string_to_formula(self.language, "( !! r2 f1 v3 f1 v4 )")
        self.assertTrue(is_propositional_consequence_inference_rule(Gamma, theta))

    def test_is_propositional_consequence_inference_rule_true_complex(self):
        Gamma = {
            string_to_formula(
                self.language, "( ( AA v1 ) ( = v1 a ) -> ( EE v2 ) ( r2 v2 a ) )"
            ),
            string_to_formula(self.language, "( ( EE v2 ) ( r2 v2 a ) -> = v1 a )"),
            string_to_formula(self.language, "( ( !! = v1 a ) <-> = v2 c )"),
        }
        theta = string_to_formula(
            self.language, "( ( AA v1 ) ( = v1 a ) -> ( !! = v2 c ) )"
        )
        self.assertTrue(is_propositional_consequence_inference_rule(Gamma, theta))

    def test_is_propositional_consequence_inference_rule_false(self):
        Gamma = {
            string_to_formula(self.language, "( = v1 v2 && r2 v2 a )"),
            string_to_formula(self.language, "( r2 v2 a || = v2 c )"),
        }
        theta = string_to_formula(self.language, "= v2 c")
        self.assertFalse(is_propositional_consequence_inference_rule(Gamma, theta))

    def test_is_universal_quantifier_inference_rule_true(self):
        Gamma = {string_to_formula(self.language, "( ( !! r2 f1 v1 a ) -> = v1 v2 )")}
        theta = string_to_formula(
            self.language, "( ( !! r2 f1 v1 a ) -> ( AA v2 ) ( = v1 v2 ) )"
        )
        self.assertTrue(is_universal_quantifier_inference_rule(Gamma, theta))

    def test_is_universal_quantifier_inference_rule_false(self):
        Gamma = {string_to_formula(self.language, "( r2 f1 v1 a -> = v1 v2 )")}
        theta = string_to_formula(
            self.language, "( r2 f1 v1 a -> ( AA v1 ) ( = v1 v2 ) )"
        )
        self.assertFalse(is_universal_quantifier_inference_rule(Gamma, theta))

    def test_is_existential_quantifier_inference_rule_true(self):
        Gamma = {
            string_to_formula(
                self.language, "( ( = v1 a && = f1 v1 a ) -> ( AA v1 ) ( r2 v1 v1 ) )"
            )
        }
        theta = string_to_formula(
            self.language,
            "( ( EE v1 ) ( ( = v1 a && = f1 v1 a ) ) -> ( AA v1 ) ( r2 v1 v1 ) )",
        )
        self.assertTrue(is_existential_quantifier_inference_rule(Gamma, theta))

    def test_is_existential_quantifier_inference_rule_false(self):
        Gamma = {
            string_to_formula(self.language, "( ( = v1 a && = f1 v1 a ) -> r2 v1 v1 )")
        }
        theta = string_to_formula(
            self.language, "( ( EE v1 ) ( ( = v1 a && = f1 v1 a ) ) -> r2 v1 v1 )"
        )
        self.assertFalse(is_existential_quantifier_inference_rule(Gamma, theta))


if __name__ == "__main__":
    unittest.main()

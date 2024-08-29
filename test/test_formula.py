import unittest
from typing import override

from fol_ly.language import Language
from fol_ly.term import VariableTerm, ConstantTerm, FunctionTerm
from fol_ly.formula import (
    EqualityFormula,
    RelationFormula,
    NegationFormula,
    DisjunctionFormula,
    QuantifiedFormula,
    string_to_formula,
)


class TestFormula(unittest.TestCase):
    def setUp(self):
        self.language1 = Language({"a", "b", "c"}, {1: {"f1"}, 3: {"f3"}}, {2: {"r2"}})
        self.language2 = Language(
            {"a", "y", "z"}, {1: {"f1", "f2"}}, {2: {"r2"}, 3: {"r3"}}
        )
        self.term1 = ConstantTerm(self.language1, "a")
        self.term2 = VariableTerm(self.language1, "v4")
        self.term3 = FunctionTerm(self.language1, "f1", [self.term1])
        self.term4 = FunctionTerm(
            self.language1, "f3", [self.term1, self.term2, self.term3]
        )
        self.term5 = VariableTerm(self.language2, "v5")
        self.term6 = FunctionTerm(self.language2, "f2", [self.term5])


class TestEqualityFormula(TestFormula):
    def test_init_sunny(self):
        f = EqualityFormula(self.language1, self.term1, self.term2)
        self.assertEqual(f.language, self.language1)
        self.assertEqual(f.t1, self.term1)
        self.assertEqual(f.t2, self.term2)

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            EqualityFormula(self.language2, self.term1, self.term2)
        with self.assertRaises(ValueError):
            EqualityFormula(self.language1, self.term1, self.term5)

    def test_str(self):
        f = EqualityFormula(self.language1, self.term1, self.term2)
        self.assertEqual(f, string_to_formula(self.language1, str(f)))

    def test_eq_true(self):
        f1 = EqualityFormula(self.language1, self.term1, self.term2)
        f2 = EqualityFormula(self.language1, self.term1, self.term2)
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f2)

    def test_eq_false(self):
        f1 = EqualityFormula(self.language1, self.term2, self.term2)
        f2 = EqualityFormula(self.language1, self.term2, self.term3)
        f3 = EqualityFormula(self.language2, self.term5, self.term5)
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(f1, f3)

    def test_get_free_variables(self):
        f1 = EqualityFormula(self.language1, self.term1, self.term3)
        self.assertEqual(f1.get_free_variables(), set())

        f2 = EqualityFormula(self.language1, self.term1, self.term4)
        self.assertEqual(f2.get_free_variables(), {"v4"})

    def test_variable_free_in_formula_true(self):
        f = EqualityFormula(self.language1, self.term1, self.term4)
        self.assertTrue(f.variable_free_in_formula("v4"))

    def test_variable_free_in_formula_false(self):
        f = EqualityFormula(self.language1, self.term1, self.term4)
        self.assertFalse(f.variable_free_in_formula("v1"))
        self.assertFalse(f.variable_free_in_formula("v10"))

    def test_is_sentence_true(self):
        f = EqualityFormula(self.language1, self.term1, self.term3)
        self.assertTrue(f.is_sentence())

    def test_is_sentence_false(self):
        f = EqualityFormula(self.language1, self.term1, self.term4)
        self.assertFalse(f.is_sentence())


class TestRelationFormula(TestFormula):
    def test_init_sunny(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term2])
        self.assertEqual(f.language, self.language1)
        self.assertEqual(f.R, "r2")
        self.assertEqual(f.arguments, [self.term1, self.term2])

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            RelationFormula(self.language1, "f1", [self.term1, self.term2])
        with self.assertRaises(ValueError):
            RelationFormula(self.language1, "r2", [self.term1, self.term2, self.term3])
        with self.assertRaises(ValueError):
            RelationFormula(self.language1, "r2", [self.term1, self.term5])

    def test_str(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term2])
        self.assertEqual(f, string_to_formula(self.language1, str(f)))

    def test_eq_true(self):
        f1 = RelationFormula(self.language1, "r2", [self.term1, self.term2])
        f2 = RelationFormula(self.language1, "r2", [self.term1, self.term2])
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f2)

    def test_eq_false(self):
        f1 = RelationFormula(self.language2, "r2", [self.term5, self.term6])
        f2 = RelationFormula(self.language2, "r2", [self.term5, self.term5])
        f3 = RelationFormula(self.language2, "r3", [self.term5, self.term5, self.term6])
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(f1, f3)

    def test_get_free_variables(self):
        f1 = RelationFormula(self.language1, "r2", [self.term1, self.term3])
        self.assertEqual(f1.get_free_variables(), set())

        f2 = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        self.assertEqual(f2.get_free_variables(), {"v4"})

    def test_variable_free_in_formula_true(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        self.assertTrue(f.variable_free_in_formula("v4"))

    def test_variable_free_in_formula_false(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        self.assertFalse(f.variable_free_in_formula("v1"))
        self.assertFalse(f.variable_free_in_formula("v10"))

    def test_is_sentence_true(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term3])
        self.assertTrue(f.is_sentence())

    def test_is_sentence_false(self):
        f = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        self.assertFalse(f.is_sentence())


class TestNegationFormula(TestFormula):
    @override
    def setUp(self):
        super().setUp()
        self.language1_relation_formula = RelationFormula(
            self.language1, "r2", [self.term1, self.term2]
        )
        self.language2_equality_formula = EqualityFormula(
            self.language2,
            ConstantTerm(self.language2, "z"),
            VariableTerm(self.language2, "v1"),
        )

    def test_init_sunny(self):
        f = NegationFormula(self.language1, self.language1_relation_formula)
        self.assertEqual(f.language, self.language1)
        self.assertEqual(f.P, self.language1_relation_formula)

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            NegationFormula(self.language1, self.language2_equality_formula)

    def test_str(self):
        f = NegationFormula(self.language1, self.language1_relation_formula)
        self.assertEqual(f, string_to_formula(self.language1, str(f)))

    def test_eq_true(self):
        f1 = NegationFormula(self.language1, self.language1_relation_formula)
        f2 = NegationFormula(self.language1, self.language1_relation_formula)
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f2)

    def test_eq_false(self):
        rf1 = RelationFormula(self.language2, "r2", [self.term5, self.term6])
        f1 = NegationFormula(self.language2, rf1)
        rf2 = RelationFormula(self.language2, "r2", [self.term5, self.term5])
        f2 = NegationFormula(self.language2, rf2)
        rf3 = RelationFormula(
            self.language2, "r3", [self.term5, self.term5, self.term6]
        )
        f3 = NegationFormula(self.language2, rf3)
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(f1, f3)

    def test_get_free_variables(self):
        rf1 = RelationFormula(self.language1, "r2", [self.term1, self.term3])
        f1 = NegationFormula(self.language1, rf1)
        self.assertEqual(f1.get_free_variables(), set())

        rf2 = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        f2 = NegationFormula(self.language1, rf2)
        self.assertEqual(f2.get_free_variables(), {"v4"})

    def test_variable_free_in_formula_true(self):
        rf = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        f = NegationFormula(self.language1, rf)
        self.assertTrue(f.variable_free_in_formula("v4"))

    def test_variable_free_in_formula_false(self):
        rf = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        f = NegationFormula(self.language1, rf)
        self.assertFalse(f.variable_free_in_formula("v1"))
        self.assertFalse(f.variable_free_in_formula("v10"))

    def test_is_sentence_true(self):
        rf = RelationFormula(self.language1, "r2", [self.term1, self.term3])
        f = NegationFormula(self.language1, rf)
        self.assertTrue(f.is_sentence())

    def test_is_sentence_false(self):
        rf = RelationFormula(self.language1, "r2", [self.term1, self.term4])
        f = NegationFormula(self.language1, rf)
        self.assertFalse(f.is_sentence())


class TestDisjunctionFormula(TestFormula):
    @override
    def setUp(self):
        super().setUp()
        self.language1_relation_formula = RelationFormula(
            self.language1, "r2", [self.term1, self.term2]
        )
        self.language1_equality_formula = EqualityFormula(
            self.language1,
            ConstantTerm(self.language1, "a"),
            VariableTerm(self.language1, "v1"),
        )
        self.language2_equality_formula = EqualityFormula(
            self.language2,
            ConstantTerm(self.language2, "z"),
            ConstantTerm(self.language2, "a"),
        )

    def test_init_sunny(self):
        f = DisjunctionFormula(
            self.language1,
            self.language1_relation_formula,
            self.language1_equality_formula,
        )
        self.assertEqual(f.language, self.language1)
        self.assertEqual(f.P, self.language1_relation_formula)
        self.assertEqual(f.Q, self.language1_equality_formula)

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            DisjunctionFormula(
                self.language1,
                self.language1_equality_formula,
                self.language2_equality_formula,
            )

    def test_str(self):
        f = DisjunctionFormula(
            self.language1,
            self.language1_relation_formula,
            self.language1_equality_formula,
        )
        self.assertEqual(f, string_to_formula(self.language1, str(f)))

    def test_eq_true(self):
        f1 = DisjunctionFormula(
            self.language1,
            self.language1_relation_formula,
            self.language1_equality_formula,
        )
        f2 = DisjunctionFormula(
            self.language1,
            self.language1_relation_formula,
            self.language1_equality_formula,
        )
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f2)

    def test_eq_false(self):
        f1 = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_equality_formula,
        )
        f2 = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_relation_formula,
        )
        f3 = DisjunctionFormula(
            self.language2,
            self.language2_equality_formula,
            self.language2_equality_formula,
        )
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(f1, f3)

    def test_get_free_variables(self):
        f1 = DisjunctionFormula(
            self.language2,
            self.language2_equality_formula,
            self.language2_equality_formula,
        )
        self.assertEqual(f1.get_free_variables(), set())

        f2 = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_equality_formula,
        )
        self.assertEqual(f2.get_free_variables(), {"v1"})

        f3 = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_relation_formula,
        )
        self.assertEqual(f3.get_free_variables(), {"v4", "v1"})

    def test_variable_free_in_formula_true(self):
        f = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_relation_formula,
        )
        self.assertTrue(f.variable_free_in_formula("v4"))

    def test_variable_free_in_formula_false(self):
        f = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_equality_formula,
        )
        self.assertFalse(f.variable_free_in_formula("v10"))

    def test_is_sentence_true(self):
        f = DisjunctionFormula(
            self.language2,
            self.language2_equality_formula,
            self.language2_equality_formula,
        )
        self.assertTrue(f.is_sentence())

    def test_is_sentence_false(self):
        f = DisjunctionFormula(
            self.language1,
            self.language1_equality_formula,
            self.language1_equality_formula,
        )
        self.assertFalse(f.is_sentence())


class TestQuantifiedFormula(TestFormula):
    @override
    def setUp(self):
        super().setUp()
        self.language1_relation_formula = RelationFormula(
            self.language1, "r2", [self.term1, self.term2]
        )
        self.language1_equality_formula = EqualityFormula(
            self.language1,
            ConstantTerm(self.language1, "a"),
            VariableTerm(self.language1, "v1"),
        )
        self.language2_equality_formula = EqualityFormula(
            self.language2,
            ConstantTerm(self.language2, "z"),
            ConstantTerm(self.language2, "a"),
        )

    def test_init_sunny(self):
        f = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertEqual(f.language, self.language1)
        self.assertEqual(f.v, "v1")
        self.assertEqual(f.P, self.language1_equality_formula)

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            QuantifiedFormula(self.language1, "v1", self.language2_equality_formula)
        with self.assertRaises(ValueError):
            QuantifiedFormula(self.language1, "f2", self.language1_equality_formula)

    def test_str(self):
        f = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertEqual(f, string_to_formula(self.language1, str(f)))

    def test_eq_true(self):
        f1 = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        f2 = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertEqual(f1, f1)
        self.assertEqual(f1, f2)

    def test_eq_false(self):
        f1 = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        f2 = QuantifiedFormula(self.language1, "v4", self.language1_equality_formula)
        f3 = QuantifiedFormula(self.language1, "v1", self.language1_relation_formula)
        self.assertNotEqual(f1, f2)
        self.assertNotEqual(f1, f3)

    def test_get_free_variables(self):
        f1 = QuantifiedFormula(self.language2, "v1", self.language2_equality_formula)
        self.assertEqual(f1.get_free_variables(), set())

        f2 = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertEqual(f2.get_free_variables(), set())

        f3 = QuantifiedFormula(self.language1, "v10", self.language1_equality_formula)
        self.assertEqual(f3.get_free_variables(), {"v1"})

    def test_variable_free_in_formula_true(self):
        f = QuantifiedFormula(self.language1, "v1", self.language1_relation_formula)
        self.assertTrue(f.variable_free_in_formula("v4"))

    def test_variable_free_in_formula_false(self):
        f = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertFalse(f.variable_free_in_formula("v1"))
        self.assertFalse(f.variable_free_in_formula("v10"))

    def test_is_sentence_true(self):
        f1 = QuantifiedFormula(self.language2, "v1", self.language2_equality_formula)
        self.assertTrue(f1.is_sentence())

        f2 = QuantifiedFormula(self.language1, "v1", self.language1_equality_formula)
        self.assertTrue(f2.is_sentence())

    def test_is_sentence_false(self):
        f = QuantifiedFormula(self.language1, "v10", self.language1_equality_formula)
        self.assertFalse(f.is_sentence())


class TestStringToTerm(TestFormula):
    def test_string_to_term_rainy(self):
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "blah")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "f1")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "f3 a")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "|| AA")

        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "v1")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "f3 a v1 f1 c")

        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "r2")
        with self.assertRaises(ValueError):
            string_to_formula(self.language1, "r2 f3 a v1 f1 c")


if __name__ == "__main__":
    unittest.main()

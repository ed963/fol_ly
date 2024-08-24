import unittest

from fol_ly.language import Language
from fol_ly.term import VariableTerm, ConstantTerm, FunctionTerm, string_to_term


class TestTerm(unittest.TestCase):
    def setUp(self):
        self.language1 = Language({"a", "b", "c"}, {1: {"f1"}, 3: {"f3"}}, {2: {"r2"}})
        self.language2 = Language(
            {"a", "y", "z"}, {1: {"f1", "f2"}}, {2: {"r2"}, 3: {"r3"}}
        )


class TestVariableTerm(TestTerm):
    def test_init_sunny(self):
        t = VariableTerm(self.language1, "v5")
        self.assertEqual(t.language, self.language1)
        self.assertEqual(t.variable, "v5")

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            VariableTerm(self.language1, "blah")
        with self.assertRaises(ValueError):
            VariableTerm(self.language1, "a")
        with self.assertRaises(ValueError):
            VariableTerm(self.language1, "f1")
        with self.assertRaises(ValueError):
            VariableTerm(self.language1, "r2")

    def test_str(self):
        t = VariableTerm(self.language1, "v5")
        self.assertEqual(t, string_to_term(self.language1, str(t)))

    def test_eq_true(self):
        t1 = VariableTerm(self.language1, "v5")
        t2 = VariableTerm(self.language1, "v5")
        self.assertEqual(t1, t1)
        self.assertEqual(t1, t2)

    def test_eq_false(self):
        t1 = VariableTerm(self.language1, "v5")
        t2 = VariableTerm(self.language1, "v6")
        t3 = VariableTerm(self.language2, "v5")
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_get_variable_symbols(self):
        t = VariableTerm(self.language1, "v5")
        self.assertEqual(t.get_variable_symbols(), {"v5"})


class TestConstantTerm(TestTerm):
    def test_init_sunny(self):
        t = ConstantTerm(self.language1, "a")
        self.assertEqual(t.language, self.language1)
        self.assertEqual(t.constant, "a")

    def test_init_rainy(self):
        with self.assertRaises(ValueError):
            ConstantTerm(self.language1, "blah")
        with self.assertRaises(ValueError):
            ConstantTerm(self.language1, "v1")
        with self.assertRaises(ValueError):
            ConstantTerm(self.language1, "f1")
        with self.assertRaises(ValueError):
            ConstantTerm(self.language1, "r2")

    def test_str(self):
        t = ConstantTerm(self.language1, "a")
        self.assertEqual(t, string_to_term(self.language1, str(t)))

    def test_eq_true(self):
        t1 = ConstantTerm(self.language1, "b")
        t2 = ConstantTerm(self.language1, "b")
        self.assertEqual(t1, t1)
        self.assertEqual(t1, t2)

    def test_eq_false(self):
        t1 = ConstantTerm(self.language1, "a")
        t2 = ConstantTerm(self.language1, "b")
        t3 = ConstantTerm(self.language2, "a")
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_get_variable_symbols(self):
        t = ConstantTerm(self.language1, "c")
        self.assertEqual(t.get_variable_symbols(), set())


class TestFunctionTerm(TestTerm):
    def test_init_sunny(self):
        t_constant = ConstantTerm(self.language1, "a")
        t1 = FunctionTerm(self.language1, "f1", [t_constant])
        self.assertEqual(t1.language, self.language1)
        self.assertEqual(t1.f, "f1")
        self.assertEqual(t1.arguments, [t_constant])

        t2 = FunctionTerm(self.language1, "f3", [t_constant, t_constant, t_constant])
        self.assertEqual(t2.language, self.language1)
        self.assertEqual(t2.f, "f3")
        self.assertEqual(t2.arguments, [t_constant, t_constant, t_constant])

        t3 = FunctionTerm(self.language1, "f3", [t_constant, t1, t2])
        self.assertEqual(t3.language, self.language1)
        self.assertEqual(t3.f, "f3")
        self.assertEqual(t3.arguments, [t_constant, t1, t2])

    def test_init_rainy_non_function(self):
        t_constant = ConstantTerm(self.language1, "a")
        with self.assertRaises(ValueError):
            FunctionTerm(self.language1, "a", [t_constant])
        with self.assertRaises(ValueError):
            FunctionTerm(self.language1, "blah", [t_constant])

    def test_init_rainy_arity_mismatch(self):
        t_constant = ConstantTerm(self.language1, "a")
        with self.assertRaises(ValueError):
            FunctionTerm(self.language1, "f1", [t_constant, t_constant])

    def test_str(self):
        t_constant = ConstantTerm(self.language1, "a")
        t1 = FunctionTerm(self.language1, "f1", [t_constant])
        t2 = FunctionTerm(self.language1, "f3", [t_constant, t_constant, t_constant])
        t3 = FunctionTerm(self.language1, "f3", [t_constant, t1, t2])
        self.assertEqual(t1, string_to_term(self.language1, str(t1)))
        self.assertEqual(t2, string_to_term(self.language1, str(t2)))
        self.assertEqual(t3, string_to_term(self.language1, str(t3)))

    def test_eq_true(self):
        t_constant = ConstantTerm(self.language1, "a")
        t1 = FunctionTerm(self.language1, "f1", [t_constant])
        t2 = FunctionTerm(self.language1, "f1", [t_constant])
        self.assertEqual(t1, t1)
        self.assertEqual(t1, t2)

    def test_eq_false(self):
        t_constant1 = ConstantTerm(self.language1, "a")
        t_constant2 = ConstantTerm(self.language2, "a")
        t_variable = VariableTerm(self.language1, "v1")
        t1 = FunctionTerm(self.language1, "f1", [t_constant1])
        t2 = FunctionTerm(self.language1, "f1", [t_variable])
        t3 = FunctionTerm(self.language2, "f1", [t_constant2])
        t4 = FunctionTerm(self.language1, "f3", [t_constant1, t_constant1, t_constant1])
        self.assertNotEqual(t1, t2)
        self.assertNotEqual(t1, t3)
        self.assertNotEqual(t1, t4)

    def test_get_variable_symbols_empty(self):
        t_constant = ConstantTerm(self.language1, "a")
        t = FunctionTerm(self.language1, "f1", [t_constant])
        self.assertEqual(t.get_variable_symbols(), set())

    def test_get_variable_symbols_simple(self):
        t_variable1 = VariableTerm(self.language1, "v1")
        t_variable2 = VariableTerm(self.language1, "v5")
        t = FunctionTerm(self.language1, "f3", [t_variable1, t_variable1, t_variable2])
        self.assertEqual(t.get_variable_symbols(), {"v1", "v5"})

    def test_get_variable_symbols_nested_function_term(self):
        t_variable = VariableTerm(self.language1, "v1")
        t1 = FunctionTerm(self.language1, "f1", [t_variable])
        t2 = FunctionTerm(self.language1, "f1", [t1])
        self.assertEqual(t1.get_variable_symbols(), {"v1"})
        self.assertEqual(t2.get_variable_symbols(), {"v1"})


class TestStringToTerm(TestTerm):
    def test_string_to_term_rainy(self):
        with self.assertRaises(ValueError):
            string_to_term(self.language1, "")
        with self.assertRaises(ValueError):
            string_to_term(self.language1, "blah")
        with self.assertRaises(ValueError):
            string_to_term(self.language1, "f1")
        with self.assertRaises(ValueError):
            string_to_term(self.language1, "f3 a")
        with self.assertRaises(ValueError):
            string_to_term(self.language1, "|| AA")


if __name__ == "__main__":
    unittest.main()

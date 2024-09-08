import unittest

from fol_ly.language import Language, is_disjoint_sets


class TestIsDisjointSets(unittest.TestCase):
    def test_is_disjoint_sets_false(self):
        self.assertFalse(is_disjoint_sets({"a", "b", "c"}, {"c", "d", "e"}))
        self.assertFalse(is_disjoint_sets({"a"}, {"c", "d", "e"}, {"d"}, {"f"}))

    def test_is_disjoint_sets_true(self):
        self.assertTrue(is_disjoint_sets({"a", "b", "c"}, {"x", "y", "z"}))
        self.assertTrue(is_disjoint_sets({"a"}, {"c", "d", "e"}, {"f"}, {"g"}))


class TestLanguage(unittest.TestCase):
    def test_init_sunny_empty(self):
        l = Language(set(), {}, {})
        self.assertEqual(l._constants, set())
        self.assertEqual(l._functions, {})
        self.assertEqual(l._relations, {})

    def test_init_sunny_compex(self):
        l = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        self.assertEqual(l._constants, {"a", "b", "pi"})
        self.assertEqual(l._functions, {1: {"f1", "f2"}, 3: {"f3"}})
        self.assertEqual(l._relations, {2: {"r1"}})

    def test_init_rainy_invalid_symbol(self):
        with self.assertRaises(ValueError):
            Language({"v1"}, {}, {})

        with self.assertRaises(ValueError):
            Language(set(), {1: {"||"}}, {})

        with self.assertRaises(ValueError):
            Language(set(), {}, {2: {"r 2"}})

        with self.assertRaises(ValueError):
            Language({"->"}, {}, {})

    def test_init_rainy_repeat_symbol(self):
        with self.assertRaises(ValueError):
            Language({"a"}, {1: {"a"}}, {})

    def test_eq_true(self):
        l1 = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        l2 = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        self.assertEqual(l1, l1)
        self.assertEqual(l1, l2)

    def test_eq_false(self):
        l1 = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        l2 = Language({"a", "b"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        l3 = Language({"a", "b", "pi"}, {3: {"f1", "f2"}, 1: {"f3"}}, {2: {"r1"}})
        l4 = Language({"a", "b", "pi"}, {3: {"f1", "f2"}, 1: {"f3"}}, {})
        self.assertNotEqual(l1, l2)
        self.assertNotEqual(l1, l3)
        self.assertNotEqual(l1, l4)

    def test_is_valid_non_logical_symbol_false(self):
        self.assertFalse(Language.is_valid_nonlogical_symbol(3.14))
        self.assertFalse(Language.is_valid_nonlogical_symbol(["x"]))
        self.assertFalse(Language.is_valid_nonlogical_symbol("AA"))
        self.assertFalse(Language.is_valid_nonlogical_symbol("("))
        self.assertFalse(Language.is_valid_nonlogical_symbol("A 2"))
        self.assertFalse(Language.is_valid_nonlogical_symbol("v314"))

    def test_is_valid_non_logical_symbol_true(self):
        self.assertTrue(Language.is_valid_nonlogical_symbol("A"))
        self.assertTrue(Language.is_valid_nonlogical_symbol("x2"))

    def test_is_variable_symbol_true(self):
        self.assertTrue(Language.is_variable_symbol("v1"))
        self.assertTrue(Language.is_variable_symbol("v1111"))

    def test_is_variable_symbol_false(self):
        self.assertFalse(Language.is_variable_symbol("v"))
        self.assertFalse(Language.is_variable_symbol("1v"))
        self.assertFalse(Language.is_variable_symbol("v 2"))
        self.assertFalse(Language.is_variable_symbol("v 0"))

    def test_get_function_arity_symbol_exists(self):
        l = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        self.assertEqual(l.get_function_arity("f1"), 1)
        self.assertEqual(l.get_function_arity("f3"), 3)

    def test_get_function_arity_none(self):
        l = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        self.assertIsNone(l.get_function_arity("f5"))
        self.assertIsNone(l.get_function_arity("r1"))
        self.assertIsNone(l.get_function_arity("pi"))

    def test_get_relation_arity_symbol_exists(self):
        l = Language(
            {"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}, 10: {"r10"}}
        )
        self.assertEqual(l.get_relation_arity("r1"), 2)
        self.assertEqual(l.get_relation_arity("r10"), 10)

    def test_get_relation_arity_none(self):
        l = Language({"a", "b", "pi"}, {1: {"f1", "f2"}, 3: {"f3"}}, {2: {"r1"}})
        self.assertIsNone(l.get_relation_arity("f1"))
        self.assertIsNone(l.get_relation_arity("r2"))
        self.assertIsNone(l.get_relation_arity("a"))

    def test_get_variable_index(self):
        self.assertEqual(Language.get_variable_index("v1"), 1)
        self.assertEqual(Language.get_variable_index("v345"), 345)


if __name__ == "__main__":
    unittest.main()

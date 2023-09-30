from typing import Dict
import unittest
from DataStorage import DataStorage

class TestDataStorage(unittest.TestCase):
    storage: DataStorage

    def setup_storage(self, initial_data: Dict[str, object]) -> None:
        self.data: Dict[str, object] = initial_data
        self.storage: DataStorage = DataStorage(self.data)

    def assert_result(self, result: Dict[str, object], key: str, value: object, original_value: object) -> None:
        self.assertEqual(self.data[key], value)
        self.assertEqual(result["cmd"], "SetReply")
        self.assertEqual(result["key"], key)
        self.assertEqual(result["value"], value)
        self.assertEqual(result["original_value"], original_value)

    def test_adding_number(self):
        self.setup_storage({ "BasicAdd": 10 })

        set_cmd: Dict[str, object] = { 
            "key": "BasicAdd", 
            "operations": [{"operation": "add", "value": 12}] 
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "BasicAdd", 22, 10)

    def test_adding_number_with_default(self):
        self.setup_storage({})

        set_cmd: Dict[str, object] = { 
            "key": "AddWithDefault", 
            "default": 35,
            "operations": [{"operation": "add", "value": 6}]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "AddWithDefault", 41, 35)

    # Default is currently weird in two ways:
    # * The operation requires a "value" but its contents is ignored
    # * The original_value is also updated to the value
    def test_default_operation(self):
        self.setup_storage({})

        set_cmd: Dict[str, object] = { 
            "key": "Default", 
            "default": "Hello",
            "operations": [{"operation": "default", "value": None}]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "Default", "Hello", "Hello")

    def test_default_should_not_override_existing_value(self):
        self.setup_storage({ "DefaultWithExistingValue": "ExistingValue" })

        set_cmd: Dict[str, object] = { 
            "key": "DefaultWithExistingValue", 
            "default": "NewValue",
            "operations": [{"operation": "default", "value": "Ignored"}]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "DefaultWithExistingValue", "ExistingValue", "ExistingValue")

    def test_should_raise_error_on_failure_if_no_error_handling_is_specified(self):
        self.setup_storage({ "RaiseOnPopWithNonExistingKey": {} })

        set_cmd: Dict[str, object] = { 
            "key": "RaiseOnPopWithNonExistingKey", 
            "operations": [{"operation": "pop", "value": "non_existing_key"}]
        }

        with self.assertRaises(KeyError):
            self.storage.set(set_cmd)

    def test_should_raise_error_on_failure_if_handling_is_specified_as_raise(self):
        self.setup_storage({ "RaiseOnPopWithNonExistingKeyAndOnErrorRaise": {} })

        set_cmd: Dict[str, object] = { 
            "key": "RaiseOnPopWithNonExistingKeyAndOnErrorRaise", 
            "on_error": "raise",
            "operations": [{"operation": "pop", "value": "non_existing_key"}]
        }

        with self.assertRaises(KeyError):
            self.storage.set(set_cmd)

    def test_should_set_key_to_default_if_on_error_is_set_default(self):
        self.setup_storage({ "DoNotRaiseOnPopWithNonExistingKeyAndOnErrorSetDefault": {} })

        set_cmd: Dict[str, object] = { 
            "key": "DoNotRaiseOnPopWithNonExistingKeyAndOnErrorSetDefault", 
            "default": "Something",
            "on_error": "set_default",
            "operations": [{"operation": "pop", "value": "non_existing_key"}]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "DoNotRaiseOnPopWithNonExistingKeyAndOnErrorSetDefault", "Something", {})

    def test_should_undo_any_operations_on_key_if_on_error_is_undo(self):
        self.setup_storage({ "UndoOperationsWithOnErrorUndo": 10 })

        set_cmd: Dict[str, object] = { 
            "key": "UndoOperationsWithOnErrorUndo", 
            "on_error": "undo",
            "operations": [
                {"operation": "add", "value": 9},
                {"operation": "pop", "value": "not_a_dict"}
            ]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "UndoOperationsWithOnErrorUndo", 10, 10)

    def test_should_abort_any_further_operations_on_key_if_on_error_abort(self):
        self.setup_storage({ "AbortOperationsWithOnErrorAbort": 10 })

        set_cmd: Dict[str, object] = { 
            "key": "AbortOperationsWithOnErrorAbort", 
            "on_error": "abort",
            "operations": [
                {"operation": "add", "value": 9},
                {"operation": "pop", "value": "not_a_dict"},
                {"operation": "add", "value": 10}
            ]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "AbortOperationsWithOnErrorAbort", 19, 10)

    def test_should_ignore_any_errors_on_operations_on_if_on_error_ignore(self):
        self.setup_storage({ "IgnoreErrorsOnOperationsWithOnErrorIgnore": 10 })

        set_cmd: Dict[str, object] = { 
            "key": "IgnoreErrorsOnOperationsWithOnErrorIgnore", 
            "on_error": "ignore",
            "operations": [
                {"operation": "add", "value": 9},
                {"operation": "pop", "value": "not_a_dict"},
                {"operation": "add", "value": 10}
            ]
        }

        result: Dict[str, object] = self.storage.set(set_cmd)

        self.assert_result(result, "IgnoreErrorsOnOperationsWithOnErrorIgnore", 29, 10)

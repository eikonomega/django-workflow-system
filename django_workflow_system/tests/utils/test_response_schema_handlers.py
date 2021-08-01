from django.core.exceptions import ValidationError
from django.test import TestCase

from ...api.tests.factories.workflows.workflow_collection import (
    WorkflowCollectionFactory,
)
from ...api.tests.factories.workflows.step import (
    _WorkflowStepUserInputFactory,
    _WorkflowStepUserInputTypeFactory,
)
from ...models import WorkflowStep, WorkflowStepUserInput


class TestWorkflowCollection(TestCase):
    def setUp(self):
        self.my_collection = WorkflowCollectionFactory(
            **{
                "category": "SURVEY",
                "workflow_set": [
                    {
                        "workflowstep_set": [
                            {
                                "workflowstepuserinput_set": [
                                    {
                                        "required": True,
                                        "type": _WorkflowStepUserInputTypeFactory(
                                            json_schema={
                                                "type": "object",
                                                "required": ["label", "inputOptions"],
                                                "properties": {
                                                    "id": {
                                                        "type": "string",
                                                        "description": "This value may be managed outside of the object specification and so is optional.",
                                                        "examples": [
                                                            "4125-1351-1251-asfd"
                                                        ],
                                                    },
                                                    "label": {
                                                        "type": "string",
                                                        "title": "UI Label for Input",
                                                        "description": "Label that should be displayed by user interfaces for this input.",
                                                        "examples": [
                                                            "The label to display for the input/question."
                                                        ],
                                                    },
                                                    "inputOptions": {
                                                        "$id": "#/properties/options",
                                                        "type": "array",
                                                        "title": "Question Options",
                                                        "description": "The options to be displayed to the user for this question.",
                                                        "minItems": 2,
                                                        "uniqueItems": True,
                                                        "items": {
                                                            "anyOf": [
                                                                {"type": "number"},
                                                                {"type": "string"},
                                                            ]
                                                        },
                                                    },
                                                    "correctInput": {
                                                        "description": "Indicates which answer is the correct one.",
                                                        "anyOf": [
                                                            {"type": "string"},
                                                            {"type": "number"},
                                                        ],
                                                    },
                                                    "meta": {
                                                        "type": "object",
                                                        "properties": {
                                                            "inputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not an answer should be required from the user.",
                                                            },
                                                            "correctInputRequired": {
                                                                "type": "boolean",
                                                                "description": "Whether or not the correct answer should be required from the user.",
                                                            },
                                                        },
                                                    },
                                                },
                                            }
                                        ),
                                        "specification": {
                                            "label": "What is your favorite color?",
                                            "inputOptions": ["Red", "Blue"],
                                            "correctInput": "Red",
                                            "meta": {
                                                "inputRequired": True,
                                                "correctInputRequired": True,
                                            },
                                        },
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        )

    def test_single_choice_question_possibilities(self):
        """
        Test all possible outcomes for a single_choice_question.
        """
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=self.my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "single_choice_question"
        my_step_input.type.save()
        # Ensure if correct answer is required, that the enum is just the correct answer
        self.assertEquals(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "string"}, {"type": "number"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"], ["Red"]
        )

        # Change the example so that the correct answer isn't required
        my_step_input.specification = {
            "label": "What is your favorite color?",
            "inputOptions": ["Red", "Blue"],
            "correctInput": "Red",
            "meta": {"inputRequired": True, "correctInputRequired": False},
        }
        my_step_input.save()

        # Ensure that if the correct answer isn't required, we have all options in the enum
        self.assertEquals(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "string"}, {"type": "number"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            ["Red", "Blue"],
        )

        # Change the example so that neither input nor correct input is required
        my_step_input.specification = {
            "label": "What is your favorite color?",
            "inputOptions": ["Red", "Blue"],
            "correctInput": "Red",
            "meta": {"inputRequired": False, "correctInputRequired": False},
        }
        my_step_input.save()

        # Ensure that if neither are required, we have all options in the enum + None
        self.assertEquals(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "string"}, {"type": "number"}, {"type": "null"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            ["Red", "Blue", None],
        )

    def test_multi_choice_question_possibilities(self):
        """
        Test all possible outcomes of a multi choice question.
        """
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=self.my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "multiple_choice_question"
        my_step_input.type.json_schema = {
            "type": "object",
            "title": "User Input: Multiple Choice Question",
            "description": "A schema representing a multiple choice question user input.",
            "required": ["label", "inputOptions"],
            "properties": {
                "id": {
                    "type": "string",
                    "title": "A string-based user input identifier.",
                    "description": "This value may be managed outside of the object specification and so is optional.",
                    "examples": ["4125-1351-1251-asfd"],
                },
                "label": {
                    "type": "string",
                    "title": "UI Label for Input",
                    "description": "Label that should be displayed by user interfaces for this input.",
                    "examples": ["The label to display for the input/question."],
                },
                "inputOptions": {
                    "$id": "#/properties/options",
                    "type": "array",
                    "title": "Question Options",
                    "description": "The options to be displayed to the user for this question.",
                    "minItems": 2,
                    "uniqueItems": True,
                    "items": {"anyOf": [{"type": "number"}, {"type": "string"}]},
                },
                "correctInput": {
                    "description": "Indicates which answers are the correct ones.",
                    "type": "array",
                    "items": {"anyOf": [{"type": "number"}, {"type": "string"}]},
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "inputRequired": {
                            "type": "boolean",
                            "description": "Whether or not an answer should be required from the user.",
                        },
                        "correctInputRequired": {
                            "type": "boolean",
                            "description": "Whether or not the correct answer should be required from the user.",
                        },
                    },
                },
            },
        }
        my_step_input.type.save()

        my_step_input.specification = {
            "label": "What are your favorite Marvel movies?",
            "inputOptions": ["Avengers", "Captain America", "WandaVision"],
            "correctInput": ["Avengers", "WandaVision"],
            "meta": {"inputRequired": True, "correctInputRequired": True},
        }
        my_step_input.save()

        # Ensure if correct answer is required, that the enum is just the correct answer
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "array"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            [["Avengers", "WandaVision"]],
        )

        # Change the example so correctInput is not required
        my_step_input.specification = {
            "label": "What are your favorite Marvel movies?",
            "inputOptions": ["Avengers", "Captain America", "WandaVision"],
            "correctInput": ["Avengers", "WandaVision"],
            "meta": {"inputRequired": True, "correctInputRequired": False},
        }
        my_step_input.save()
        all_possible_options = [
            ["Avengers"],
            ["Captain America"],
            ["WandaVision"],
            ["Avengers", "Captain America"],
            ["Avengers", "WandaVision"],
            ["Captain America", "WandaVision"],
            ["Avengers", "Captain America", "WandaVision"],
        ]
        # Ensure that if the correct answer isn't required, we have all options in the enum
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "array"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            all_possible_options,
        )

        # Change the example so correctInput and Input are not required
        my_step_input.specification = {
            "label": "What are your favorite Marvel movies?",
            "inputOptions": ["Avengers", "Captain America", "WandaVision"],
            "correctInput": ["Avengers", "WandaVision"],
            "meta": {"inputRequired": False, "correctInputRequired": False},
        }
        my_step_input.save()
        all_possible_options.append(None)
        # Ensure that if neither are required, we have all options in the enum + None
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "array"}, {"type": "null"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            all_possible_options,
        )

    def test_numeric_range_question_possibilities(self):
        """
        Test all possible outcomes of a numeric range question.
        """
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=self.my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "numeric_range_question"
        my_step_input.type.json_schema = {
            "type": "object",
            "title": "User Input: Numeric Range Question",
            "description": "A schema representing a numeric range question user input.",
            "required": ["label", "inputOptions"],
            "properties": {
                "id": {
                    "type": "string",
                    "title": "A string-based user input identifier.",
                    "description": "This value may be managed outside of the object specification and so is optional.",
                    "examples": ["4125-1351-1251-asfd"],
                },
                "label": {
                    "type": "string",
                    "title": "UI Label for Input",
                    "description": "Label that should be displayed by user interfaces for this input.",
                    "examples": ["The label to display for the input/question."],
                },
                "inputOptions": {
                    "type": "object",
                    "properties": {
                        "minimumValue": {
                            "$id": "#/properties/options",
                            "type": "number",
                            "title": "Minimum Value",
                            "description": "The minimum value to be displayed to the user for this question.",
                        },
                        "maximumValue": {
                            "$id": "#/properties/options",
                            "type": "number",
                            "title": "Maximum Value",
                            "description": "The maximum value to be displayed to the user for this question.",
                        },
                        "step": {
                            "$id": "#/properties/options",
                            "type": "number",
                            "title": "Step Value",
                            "description": "The number between each entry between minimum and maximum.",
                        },
                    },
                },
                "correctInput": {
                    "description": "Indicates which answers are the correct ones.",
                    "type": "number",
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "inputRequired": {
                            "type": "boolean",
                            "description": "Whether or not an answer should be required from the user.",
                        },
                        "correctInputRequired": {
                            "type": "boolean",
                            "description": "Whether or not the correct answer should be required from the user.",
                        },
                    },
                },
            },
        }
        my_step_input.type.save()

        my_step_input.specification = {
            "label": "What is your favorite number?",
            "inputOptions": {"minimumValue": 0, "maximumValue": 25, "step": 1},
            "correctInput": 3,
            "meta": {"correctInputRequired": True, "inputRequired": True},
        }
        my_step_input.save()

        # Ensure if correct answer is required, that the enum is just the correct answer
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "number"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"], [3]
        )

        # Change the example so correctInput is not required
        my_step_input.specification = {
            "label": "What is your favorite number?",
            "inputOptions": {"minimumValue": 0, "maximumValue": 15, "step": 1},
            "correctInput": 3,
            "meta": {"correctInputRequired": False, "inputRequired": True},
        }
        my_step_input.save()

        # Ensure that if the correct answer isn't required, we have all options in the enum
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "number"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        )

        # Change the example so correctInput and Input are not required
        my_step_input.specification = {
            "label": "What is your favorite number?",
            "inputOptions": {"minimumValue": 0, "maximumValue": 15, "step": 1},
            "correctInput": 3,
            "meta": {"correctInputRequired": False, "inputRequired": False},
        }
        my_step_input.save()

        # Ensure that if neither are required, we have all options in the enum + None
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "number"}, {"type": "null"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, None],
        )

    def test_date_range_question_possibilities(self):
        """
        Test all possible outcomes of a date range question.
        """
        my_step = WorkflowStep.objects.get(
            workflow__workflowcollectionmember__workflow_collection=self.my_collection
        )
        my_step_input = WorkflowStepUserInput.objects.get(workflow_step=my_step)
        my_step_input.type.name = "date_range_question"
        my_step_input.type.json_schema = {
            "type": "object",
            "title": "User Input: Date Range Question",
            "description": "A schema representing a date range question user input.",
            "required": ["label", "inputOptions"],
            "properties": {
                "id": {
                    "type": "string",
                    "title": "A string-based user input identifier.",
                    "description": "This value may be managed outside of the object specification and so is optional.",
                    "examples": ["4125-1351-1251-asfd"],
                },
                "label": {
                    "type": "string",
                    "title": "UI Label for Input",
                    "description": "Label that should be displayed by user interfaces for this input.",
                    "examples": ["The label to display for the input/question."],
                },
                "inputOptions": {
                    "type": "object",
                    "properties": {
                        "earliestDate": {
                            "$id": "#/properties/options",
                            "type": "string",
                            "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[469]|11)[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[13578]|1[02])[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))",
                            "title": "Earliest Date",
                            "description": "The earliest date to be displayed to the user for this question.",
                        },
                        "latestDate": {
                            "$id": "#/properties/options",
                            "type": "string",
                            "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[469]|11)[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[13578]|1[02])[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))",
                            "title": "Latest Date",
                            "description": "The latest date to be displayed to the user for this question.",
                        },
                        "step": {"type": "number", "title": "Step Value"},
                        "stepInterval": {
                            "$id": "#/properties/options",
                            "type": "string",
                            "enum": ["year", "month", "day"],
                            "title": "Step Interval Value",
                            "description": "The time between each date entry",
                        },
                    },
                },
                "correctInput": {
                    "description": "Indicates which answers are the correct ones.",
                    "type": "string",
                    "pattern": "(((19|20)([2468][048]|[13579][26]|0[48])|2000)[/-]02[/-]29|((19|20)[0-9]{2}[/-](0[469]|11)[/-](0[1-9]|[12][0-9]|30)|(19|20)[0-9]{2}[/-](0[13578]|1[02])[/-](0[1-9]|[12][0-9]|3[01])|(19|20)[0-9]{2}[/-]02[/-](0[1-9]|1[0-9]|2[0-8])))",
                },
                "meta": {
                    "type": "object",
                    "properties": {
                        "inputRequired": {
                            "type": "boolean",
                            "description": "Whether or not an answer should be required from the user.",
                        },
                        "correctInputRequired": {
                            "type": "boolean",
                            "description": "Whether or not the correct answer should be required from the user.",
                        },
                    },
                },
            },
        }
        my_step_input.type.save()

        my_step_input.specification = {
            "label": "What is my birthday?",
            "meta": {"inputRequired": True, "correctInputRequired": True},
            "inputOptions": {
                "earliestDate": "1989-01-01",
                "latestDate": "1991-01-01",
                "step": 1,
                "stepInterval": "year",
            },
            "correctInput": "1990-01-01",
        }
        my_step_input.save()

        # Ensure if correct answer is required, that the enum is just the correct answer
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "string"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            ["1990-01-01"],
        )

        # Change the example so correctInput is not required
        my_step_input.specification = {
            "label": "What is my birthday?",
            "meta": {"inputRequired": True, "correctInputRequired": False},
            "inputOptions": {
                "earliestDate": "1989-01-01",
                "latestDate": "1991-01-01",
                "step": 1,
                "stepInterval": "year",
            },
            "correctInput": "1990-01-01",
        }
        my_step_input.save()

        # Ensure that if the correct answer isn't required, we have all options in the enum
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "string"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            ["1989-01-01", "1990-01-01", "1991-01-01"],
        )

        # Check for months
        my_step_input.specification = {
            "label": "What is my birthday?",
            "meta": {"inputRequired": True, "correctInputRequired": False},
            "inputOptions": {
                "earliestDate": "1989-01-01",
                "latestDate": "1990-01-01",
                "step": 1,
                "stepInterval": "month",
            },
            "correctInput": "1990-01-01",
        }
        my_step_input.save()
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "string"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            [
                "1989-01-01",
                "1989-02-01",
                "1989-03-01",
                "1989-04-01",
                "1989-05-01",
                "1989-06-01",
                "1989-07-01",
                "1989-08-01",
                "1989-09-01",
                "1989-10-01",
                "1989-11-01",
                "1989-12-01",
                "1990-01-01",
            ],
        )

        # Check for days
        my_step_input.specification = {
            "label": "What is my birthday?",
            "meta": {"inputRequired": True, "correctInputRequired": False},
            "inputOptions": {
                "earliestDate": "1989-01-01",
                "latestDate": "1989-01-07",
                "step": 1,
                "stepInterval": "day",
            },
            "correctInput": "1989-01-06",
        }
        my_step_input.save()
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["type"], "string"
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            [
                "1989-01-01",
                "1989-01-02",
                "1989-01-03",
                "1989-01-04",
                "1989-01-05",
                "1989-01-06",
                "1989-01-07",
            ],
        )

        # Change the example so correctInput and Input are not required
        my_step_input.specification = {
            "label": "What is my birthday?",
            "meta": {"inputRequired": False, "correctInputRequired": False},
            "inputOptions": {
                "earliestDate": "1989-01-01",
                "latestDate": "1991-01-01",
                "step": 1,
                "stepInterval": "year",
            },
            "correctInput": "1990-01-01",
        }
        my_step_input.save()

        # Ensure that if neither are required, we have all options in the enum + None
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["anyOf"],
            [{"type": "string"}, {"type": "null"}],
        )
        self.assertEqual(
            my_step_input.response_schema["properties"]["userInput"]["enum"],
            ["1989-01-01", "1990-01-01", "1991-01-01", None],
        )

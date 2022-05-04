# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails


class Intent(Enum):
    # BOOK_FLIGHT = "BookFlight"
    BOOK_FLIGHT = "book"
    CANCEL = "Cancel"
    GET_WEATHER = "GetWeather"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            # print("--a")
            recognizer_result = await luis_recognizer.recognize(turn_context)
            # print("--b")

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                result = BookingDetails()

                dst_entities = recognizer_result.entities.get("$instance", {}).get(
                    "dst_city", []
                )
                if len(dst_entities) > 0:
                    print('dst_city')
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.destination = dst_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            dst_entities[0]["text"].capitalize()
                        )


                or_entities = recognizer_result.entities.get("$instance", {}).get(
                    "or_city", []
                )
                if len(or_entities) > 0:
                    print('or_city')
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.origin = or_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            or_entities[0]["text"].capitalize()
                        )

                str_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "str_date", []
                )
                if len(str_date_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.str_date = str_date_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            str_date_entities[0]["text"].capitalize()
                        )

                end_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "end_date", []
                )
                if len(end_date_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.end_date = end_date_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            end_date_entities[0]["text"].capitalize()
                        )

                budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "end_date", []
                )
                if len(budget_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.budget = budget_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            budget_entities[0]["text"].capitalize()
                        )

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "To", []
                )
                if len(to_entities) > 0:
                    if recognizer_result.entities.get("To", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.destination = to_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            to_entities[0]["text"].capitalize()
                        )

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "From", []
                )
                if len(from_entities) > 0:
                    if recognizer_result.entities.get("From", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.origin = from_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_airports.append(
                            from_entities[0]["text"].capitalize()
                        )

                # This value will be a TIMEX. And we are only interested in a Date so grab the first result and drop
                # the Time part. TIMEX is a format that represents DateTime expressions that include some ambiguity.
                # e.g. missing a Year.
                date_entities = recognizer_result.entities.get("datetime", [])
                if date_entities:
                    timex = date_entities[0]["timex"]

                    if timex:
                        datetime = timex[0].split("T")[0]

                        result.travel_date = datetime

                else:
                    result.travel_date = None

        except Exception as exception:
            print("--c")
            print(exception)

        return intent, result
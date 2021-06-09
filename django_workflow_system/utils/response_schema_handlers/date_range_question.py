"""Response Schema Generator Module for a Date Range Question"""
import copy
import datetime
from dateutil.relativedelta import relativedelta
import math

from django_workflow_system.utils import RESPONSE_SCHEMA


def get_response_schema(workflow_step_user_input):
    """
    Build and returns a response schema for a given WorkflowStepUserInput w/
    a WorkflowStepUserInputType of 'Date Range Question'.
    """
    response_schema = copy.deepcopy(RESPONSE_SCHEMA)

    # Now we need to check some things.....
    if workflow_step_user_input.specification['meta']['inputRequired'] and workflow_step_user_input.specification['meta']['correctInputRequired']:
        # They need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = workflow_step_user_input.type.json_schema['properties']['correctInput']['type']
        response_schema['properties']['userInput']['enum'] = [
            workflow_step_user_input.specification['correctInput']]

    elif workflow_step_user_input.specification['meta']['inputRequired'] and not workflow_step_user_input.specification['meta']['correctInputRequired']:
        # They don't need to respond with the correct answer.
        response_schema['properties']['userInput']['type'] = workflow_step_user_input.type.json_schema['properties']['correctInput']['type']

        response_schema['properties']['userInput']['enum'] = fetch_all_possible_dates(
            workflow_step_user_input)

    else:
        # Answer is not required and correct is not required, so null should be an option in potential responses
        response_schema['properties']['userInput']['anyOf'] = [
            {"type": workflow_step_user_input.type.json_schema['properties']['correctInput']['type']}, {"type": "null"}]
        new_enum = fetch_all_possible_dates(workflow_step_user_input)
        new_enum.append(None)
        response_schema['properties']['userInput']['enum'] = new_enum

    return response_schema


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (datetime.date(d.year + years, 1, 1) - datetime.date(d.year, 1, 1))


def fetch_all_possible_dates(workflow_step_user_input):
    """
    Fetch all possible dates that can be answered.
    """
    step = workflow_step_user_input.specification['inputOptions']['step']
    # We need to enumerate our options here....
    start_date = datetime.datetime.strptime(
        workflow_step_user_input.specification['inputOptions']['earliestDate'], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(
        workflow_step_user_input.specification['inputOptions']['latestDate'], "%Y-%m-%d")
    list_of_dates = []
    list_of_dates.append(workflow_step_user_input.specification['inputOptions']['earliestDate'])
    list_of_dates.append(workflow_step_user_input.specification['inputOptions']['latestDate'])

    # Is there a smarter way to check whether its days, years or months????
    if workflow_step_user_input.specification['inputOptions']['stepInterval'] == 'year':
        number_of_years = math.floor(((end_date - start_date).days + 1) / 365.25)
        for year in range(0, number_of_years + 1, step):
            list_of_dates.append(add_years(start_date, year).strftime("%Y-%m-%d"))

    elif workflow_step_user_input.specification['inputOptions']['stepInterval'] == 'month':
        number_of_months = (end_date.year - start_date.year) * \
            12 + (end_date.month - start_date.month)

        for month in range(0, number_of_months + 1, step):
            list_of_dates.append((start_date + relativedelta(months=+month)).strftime("%Y-%m-%d"))

    elif workflow_step_user_input.specification['inputOptions']['stepInterval'] == 'day':
        number_of_days = (end_date - start_date).days + 1
        for day in range(1, number_of_days, step):
            list_of_dates.append((start_date + datetime.timedelta(days=day)).strftime("%Y-%m-%d"))

    return sorted(list(set(list_of_dates)))

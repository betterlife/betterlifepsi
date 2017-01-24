from __future__ import print_function

import json
import logging

import warnings
from flask import current_app
from flask_restful import Resource, reqparse

from app.reports.handlers_config import report_config
from app.utils import has_role, return_error_as_json

parser = reqparse.RequestParser()
parser.add_argument('report_type', type=int, help='Report type')
parser.add_argument('report_period', type=int, help='Report Period')


class ReportApi(Resource):

    @staticmethod
    def get_handle_function(report_type, report_period):
        return report_config.get(report_type).get(report_period)

    @has_role("report_view", return_error_as_json)
    def get(self, report_type, report_period):
        handle_function = self.get_handle_function(report_type, report_period)
        result = json.dumps(handle_function(report_type, report_period), indent=2)
        logging.getLogger('psi.report').info(
            """\nReport Type\t\t: [{2}]\nReport Period\t: [{3}]\nReport Handler\t: [{1}]\nReport Result\t: {0}"""
            .format(result, handle_function, report_type, report_period))
        return result, 200





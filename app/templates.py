from datetime import datetime

import pendulum
from fastapi.templating import Jinja2Templates


def date_iso8601(date: pendulum.DateTime | datetime) -> str:
    if isinstance(date, datetime):
        date = pendulum.instance(date)
    return date.to_iso8601_string()


def date_rfc1123(date: pendulum.DateTime | datetime) -> str:
    if isinstance(date, datetime):
        date = pendulum.instance(date)
    return date.to_rfc1123_string()


def date_relative(date: pendulum.DateTime | datetime) -> str:
    if isinstance(date, datetime):
        date = pendulum.instance(date)
    return date.diff_for_humans()


html_templates = Jinja2Templates(directory="ui/templates/html")
html_templates.env.filters["date_iso8601"] = date_iso8601
html_templates.env.filters["date_rfc1123"] = date_rfc1123
html_templates.env.filters["date_relative"] = date_relative

js_templates = Jinja2Templates(directory="ui/templates/js")
misc_templates = Jinja2Templates(directory="ui/templates/misc")

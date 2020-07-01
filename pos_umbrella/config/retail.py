from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("Retail Operations"),
            "icon": "fa fa-star",
            "items": [
                {
                    "type": "report",
                    "name": "EOD Report",
                    "doctype": "Sales Invoice",
                    "is_query_report": True,
                },

            ]
        }
    ]
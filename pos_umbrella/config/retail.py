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
                    "description": _("EOD Report"),
                    "onboard": 1,
                },

            ]
        }
    ]
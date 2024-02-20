
{
    "name": "Uruguayan Currency Rate Update",
    "version": "0.1",
    "author": "Grupo YACCK",
    "website": "http://www.grupoyacck.com/",
    "license": "AGPL-3",
    "category": "Financial Management/Configuration",
    "summary": "Update exchange uruguayan rates using OCA modules",
    "depends": ["currency_rate_update"],
    "data": [
        "views/res_currency_rate_provider.xml",
    ],
    'external_dependencies': {
        'python': ['pysimplesoap'],
    },
    "installable": True,
}

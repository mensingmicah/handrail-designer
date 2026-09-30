"""The one pint unit registry for the whole tool.

pint only allows quantities from the same registry to be combined, so every
module imports ``ureg`` and ``Q_`` from here rather than making its own.

Note on force units: in pint, ``lb`` is pound *mass*. Every force in this tool
is ``lbf`` internally; the PDF prints it as "lb" per the brief's fixed units.
"""

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

# Fixed display units for v1 (docs/BRIEF.md, Output).
DISPLAY_UNITS = {
    "length": "inch",
    "force": "lbf",
    "moment": "lbf * inch",
    "stress": "ksi",
    "force_per_length": "lbf / inch",
}

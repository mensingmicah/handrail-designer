"""The one pint unit registry for the whole tool.

pint only allows quantities from the same registry to be combined, so every
module imports ``ureg`` and ``Q_`` from here rather than making its own.

Note on force units: in pint, ``lb`` is pound *mass*. Every force in this tool
is ``lbf`` internally; the PDF prints it as "lb" per the brief's fixed units.
"""

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

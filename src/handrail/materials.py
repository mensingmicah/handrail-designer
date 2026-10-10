"""Which registry entry holds each material value the checks read.

The values themselves are registry entries (CLAUDE.md rule 1); this module
only maps a grade or electrode name to the id of its entry. A grade with
no entry here is one the tool does not support yet, and validation stops
on it (validate.py).
"""

# Fy entry for each rail and post grade this slice supports.
FY_ENTRY = {"A53 Gr B": "material.A53_GrB.Fy"}
# Fu entry for each grade a weld's fusion face can be (W12): the rail and
# post grades, and the baseplate.
FU_ENTRY = {"A53 Gr B": "material.A53_GrB.Fu", "A36": "material.A36.Fu"}
# Baseplate grades accepted: A36 only, for all of v1 (W12).
BASEPLATE_GRADES = ("A36",)
# F_EXX entry for each electrode accepted: E70XX only (W12).
FEXX_ENTRY = {"E70XX": "material.E70XX.FEXX"}

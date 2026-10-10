"""Every stop the tool has, by id (docs/brief/inputs.md, S5-9).

A stop is any place the tool refuses to compute and says why: a bad or
conflicting input, a section it will not check, a combination of sections
it has no decision for, or a registry it cannot trust. Each one has an id
here, and every error that stops a calc carries one (errors.InputError).

docs/brief/stops.md lists every id with its condition, the decision it
comes from and the test that triggers it. tests/test_stops.py holds this
list and that file to each other: every id here is in stops.md, every id
in stops.md is here, and every id has a test that triggers it. So this
list and stops.md change together, in the same commit (CLAUDE.md, Git).

The id is not part of the message. Messages are worded at the place that
raises them.
"""

from enum import StrEnum


class Stop(StrEnum):
    # -- the project file (project.py) ----------------------------------
    FILE_NOT_FOUND = "file.not_found"
    FILE_INVALID_TOML = "file.invalid_toml"
    FILE_UNKNOWN_KEY = "file.unknown_key"
    FILE_NOT_A_TABLE = "file.not_a_table"
    FILE_MISSING_KEY = "file.missing_key"
    FILE_NOT_TEXT = "file.not_text"
    FILE_NOT_A_TEXT_LIST = "file.not_a_text_list"
    FILE_NOT_A_BOOLEAN = "file.not_a_boolean"
    FILE_NOT_A_NUMBER = "file.not_a_number"
    FILE_NOT_POSITIVE = "file.not_positive"
    FILE_NOT_A_DIMENSION = "file.not_a_dimension"
    FILE_DIMENSION_NOT_POSITIVE = "file.dimension_not_positive"
    GEOMETRY_BASEPLATE_NOT_BELOW_POST_HEIGHT = "geometry.baseplate_thickness_not_below_post_height"
    LOADS_EXEMPTION_NEEDS_STATEMENT = "loads.exemption_needs_statement"
    MEMBER_SECTION_WITH_CUSTOM_DIMENSIONS = "member.section_with_custom_dimensions"
    MEMBER_SHAPE_UNSUPPORTED = "member.shape_unsupported"
    MEMBER_WALL_HALF_OD_OR_MORE = "member.wall_half_od_or_more"
    INTERMEDIATE_NONE_AND_SAME = "intermediate.none_and_same"
    INTERMEDIATE_NONE_WITH_INPUTS = "intermediate.none_with_inputs"
    INTERMEDIATE_SAME_WITH_INPUTS = "intermediate.same_with_inputs"
    INTERMEDIATE_OWN_NEEDS_SECTION = "intermediate.own_needs_section"
    INTERMEDIATE_OWN_NEEDS_WELD_SIZE = "intermediate.own_needs_weld_size"

    # -- a dimension as typed (dimensions.py) ----------------------------
    DIMENSION_EMPTY = "dimension.empty"
    DIMENSION_NEGATIVE = "dimension.negative"
    DIMENSION_UNREADABLE = "dimension.unreadable"
    DIMENSION_ZERO_DENOMINATOR = "dimension.zero_denominator"
    DIMENSION_INCHES_12_OR_MORE = "dimension.inches_12_or_more"

    # -- sections, grades and the baseplate (shapes.py, validate.py) -----
    SECTION_NOT_FOUND = "section.not_found"
    GRADE_UNSUPPORTED = "grade.unsupported"
    GRADE_WALL_OVER_LIMIT = "grade.wall_over_limit"
    GRADE_POST_FU_FY_BELOW_LIMIT = "grade.post_fu_fy_below_limit"
    WELD_ELECTRODE_UNSUPPORTED = "weld.electrode_unsupported"
    BASEPLATE_GRADE_UNSUPPORTED = "baseplate.grade_unsupported"
    BASEPLATE_SMALLER_THAN_POST = "baseplate.smaller_than_post"
    SECTION_CHORD_D_T_OVER_LIMIT = "section.chord_D_t_over_limit"
    SECTION_POST_WIDER_THAN_RAIL = "section.post_wider_than_rail"
    SECTION_INTERMEDIATE_WIDER_THAN_POST = "section.intermediate_wider_than_post"

    # -- which section families may meet at each joint (joints.py) -------
    JOINT_CHECK3_NOT_SUPPORTED = "joint.check3.not_supported"
    JOINT_CHECK3_NO_CELL = "joint.check3.no_cell"
    JOINT_CHECK4B_NOT_SUPPORTED = "joint.check4b.not_supported"
    JOINT_CHECK4B_NO_CELL = "joint.check4b.no_cell"
    JOINT_CHECK7_NOT_SUPPORTED = "joint.check7.not_supported"
    JOINT_CHECK7_NO_CELL = "joint.check7.no_cell"

    # -- a section the checks will not check (flexure.py, post.py) -------
    SECTION_BEYOND_F8_LIMIT = "section.beyond_F8_limit"
    SECTION_SLENDER_IN_FLEXURE = "section.slender_in_flexure"
    SECTION_SLENDER_IN_COMPRESSION = "section.slender_in_compression"
    CHECK5_SECOND_ORDER_NOT_NEGLIGIBLE = "check5.second_order_not_negligible"

    # -- the code-value registry (registry.py; CLAUDE.md rule 1) ---------
    REGISTRY_FILE_NOT_FOUND = "registry.file_not_found"
    REGISTRY_INVALID_TOML = "registry.invalid_toml"
    REGISTRY_MISSING_FIELD = "registry.missing_field"
    REGISTRY_BAD_STATUS = "registry.bad_status"
    REGISTRY_VERIFIED_WITHOUT_SIGNOFF = "registry.verified_without_signoff"
    REGISTRY_DRAFTED_WITH_SIGNOFF = "registry.drafted_with_signoff"
    REGISTRY_DUPLICATE_ID = "registry.duplicate_id"
    REGISTRY_NO_REVIEW_LIST = "registry.no_review_list"
    REGISTRY_DUPLICATE_REVIEW_ID = "registry.duplicate_review_id"
    REGISTRY_REVIEW_LIST_MISMATCH = "registry.review_list_mismatch"
    REGISTRY_MISSING_ENTRY = "registry.missing_entry"
    REGISTRY_NOT_A_QUANTITY = "registry.not_a_quantity"
    REGISTRY_CITE_NAMES_NO_EQUATION = "registry.cite_names_no_equation"

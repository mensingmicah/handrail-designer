# Brief: stops

Part of the product brief; index in docs/BRIEF.md. Every place the tool
refuses to compute, and which section families may meet at each joint.
(S5-9, Micah 2026-10-09; docs/brief/inputs.md, "Stops and supported
combinations".)

A stop is any place the tool refuses to compute and says why: a bad or
conflicting input, a section it will not check, a combination of sections
it has no decision for, or a code-value registry it cannot trust. The tool
prints the reason as one line and produces no calc.

This file is calc code. A test holds the code to it
(tests/test_stops.py), the way a test holds the printed assumptions to
output.md: every stop in the code has an id that is listed here, every id
listed here is in the code, and each has a test that triggers it. The
tables under "Supported combinations" are compared cell for cell with the
tables the code decides by (src/handrail/joints.py). So this file changes
only on a calc branch, in the same commit as the code it describes
(CLAUDE.md, Git).

## Supported combinations

One table per joint says which section families may meet there. A cell is
either "allowed" or a stop naming the slice that brings the family.

**Allowed means listed as allowed.** A pair of families with no cell in a
joint's table stops the calc, with a message naming the joint and both
families. Nothing unlisted is ever computed. (Binding; Micah, 2026-10-09.)

As built in step 1 of slice 5, the only allowed pair is AISC pipe on AISC
pipe, which is what the tool computed before the tables existed. Step 5 of
slice 5 sets the round HSS and custom round tube cells to allowed
(docs/plans/slice-5.md, "Supported combinations").

### Check 3 joint (top rail as chord, post as branch)

| Chord \ Branch | AISC pipe | round HSS | custom round tube | rectangular HSS, custom rectangular tube | solid round bar, solid rectangular bar |
| --- | --- | --- | --- | --- | --- |
| AISC pipe | allowed | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| round HSS | stop: slice 5 | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| custom round tube | stop: slice 5 | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| rectangular HSS, custom rectangular tube | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 7 |
| solid round bar, solid rectangular bar | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 |

### Check 4b joint (post as chord, intermediate rail as branch)

The same table as the Check 3 joint.

| Chord \ Branch | AISC pipe | round HSS | custom round tube | rectangular HSS, custom rectangular tube | solid round bar, solid rectangular bar |
| --- | --- | --- | --- | --- | --- |
| AISC pipe | allowed | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| round HSS | stop: slice 5 | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| custom round tube | stop: slice 5 | stop: slice 5 | stop: slice 5 | stop: slice 6 | stop: slice 7 |
| rectangular HSS, custom rectangular tube | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 6 | stop: slice 7 |
| solid round bar, solid rectangular bar | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 | stop: slice 7 |

### Check 7 joint (post on the baseplate)

A36 plate is the only baseplate (W12).

| Post | Cell |
| --- | --- |
| AISC pipe | allowed |
| round HSS | stop: slice 5 |
| custom round tube | stop: slice 5 |
| rectangular HSS, custom rectangular tube | stop: slice 6 |
| solid round bar, solid rectangular bar | stop: slice 7 |

### What each cell cites

- **Allowed, chord and branch.** W7 as kept for slice 5 by S5-3: the chord
  wall's local strength is a stated assumption, not a check. W2's branch
  rule: k_ds = 1.0 at a branch-to-chord weld.
- **Allowed, post on the baseplate.** Welded all around; W2's directional
  strength increase applies.
- **Stop.** The family is not supported until the slice named, by S5-1,
  which regrouped slices 5 to 7 by engineering: 5 hollow round, 6 hollow
  rectangular, 7 every solid bar. Until then W7 and W2 have been decided
  for round hollow sections only. In the chord and branch tables the
  message names the member whose family brings the stop, then the joint,
  both families and the slice. Its first sentences are the wording the
  stop has had since slices 3 and 4.
- **No cell.** S5-9. The message names the joint and both families.

## Every stop

Each table lists the stop's id, what the tool refuses, the decision it
comes from, and the test that triggers it. Every test is in
tests/test_stops.py. Rules about dimensions, not families, are ordinary
stops on this same list: W8, S4-11, B and N against the post OD.

### The project file

The reader is strict because a typo must never turn into a plausible calc
for inputs the engineer did not intend (src/handrail/project.py).

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `file.not_found` | The project file does not exist. | Project file (output.md) | `test_stop_is_triggered[file.not_found]` |
| `file.invalid_toml` | The project file is not valid TOML. | Project file (output.md) | `test_stop_is_triggered[file.invalid_toml]` |
| `file.unknown_key` | A table or key is not one the tool reads; a misspelled override would otherwise fall back silently to the code value. | Strict reader (slice 1) | `test_stop_is_triggered[file.unknown_key]` |
| `file.not_a_table` | A value is given where a table is expected. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_a_table]` |
| `file.missing_key` | A required table or key is left out: the post, the weld sizes and the baseplate's B and N have no default. | D9 (slice 2); W12 (slice 3); S4-6 | `test_stop_is_triggered[file.missing_key]` |
| `file.not_text` | A text field is not quoted text. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_text]` |
| `file.not_a_text_list` | References or assumptions are not a list of quoted text. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_a_text_list]` |
| `file.not_a_boolean` | A true or false field is quoted text; the text "false" must never read as true. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_a_boolean]` |
| `file.not_a_number` | A load or a deflection limit is not a bare number. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_a_number]` |
| `file.not_positive` | A load or a deflection limit is zero or less. | Strict reader (slice 1) | `test_stop_is_triggered[file.not_positive]` |
| `file.not_a_dimension` | A dimension is neither text nor a number. | Dimension entry (inputs.md) | `test_stop_is_triggered[file.not_a_dimension]` |
| `file.dimension_not_positive` | A dimension is zero. | Dimension entry (inputs.md); D9 for the baseplate thickness | `test_stop_is_triggered[file.dimension_not_positive]` |
| `geometry.baseplate_thickness_not_below_post_height` | The baseplate thickness is not less than the post height h. | D9 (slice 2; inputs.md) | `test_stop_is_triggered[geometry.baseplate_thickness_not_below_post_height]` |
| `loads.exemption_needs_statement` | The distributed-load exemption is ticked with no statement of why ASCE 7-22 §4.5.1.1 exempts the guard. | Distributed-load exemption (inputs.md) | `test_stop_is_triggered[loads.exemption_needs_statement]` |
| `intermediate.none_and_same` | The intermediate rail is both "none" and "same as the top rail". | S4-1; conflicting inputs (Micah, 2026-10-09) | `test_stop_is_triggered[intermediate.none_and_same]` |
| `intermediate.none_with_inputs` | "None", with a section, a grade, an intermediate weld size or an intermediate deflection limit given. | S4-1; conflicting inputs (Micah, 2026-10-09) | `test_stop_is_triggered[intermediate.none_with_inputs]` |
| `intermediate.same_with_inputs` | "Same as the top rail", with a section, a grade, an intermediate weld size or an intermediate deflection limit given. | S4-1; conflicting inputs (Micah, 2026-10-09) | `test_stop_is_triggered[intermediate.same_with_inputs]` |
| `intermediate.own_needs_section` | Its own section is chosen and no section is given. | S4-1; conflicting inputs (Micah, 2026-10-09) | `test_stop_is_triggered[intermediate.own_needs_section]` |
| `intermediate.own_needs_weld_size` | Its own section is given with no intermediate rail to post weld size. | S4-8 | `test_stop_is_triggered[intermediate.own_needs_weld_size]` |

### A dimension as typed

Anything ambiguous is rejected with a message, not guessed at: a misread
dimension gives a plausible wrong number (src/handrail/dimensions.py). A
dimension stop reaches the engineer through the project file, which adds
the table and key it was typed under.

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `dimension.empty` | The dimension is blank. | Dimension entry (inputs.md) | `test_stop_is_triggered[dimension.empty]` |
| `dimension.negative` | The dimension is negative. | Dimension entry (inputs.md) | `test_stop_is_triggered[dimension.negative]` |
| `dimension.unreadable` | The text is not one of the accepted forms (5' 6-1/8", 66.125 in, 3 ft 6 in, 42). | Dimension entry (inputs.md) | `test_stop_is_triggered[dimension.unreadable]` |
| `dimension.zero_denominator` | A fraction has a zero denominator. | Dimension entry (inputs.md) | `test_stop_is_triggered[dimension.zero_denominator]` |
| `dimension.inches_12_or_more` | Feet are given and the inches part is 12 or more. | Dimension entry (inputs.md) | `test_stop_is_triggered[dimension.inches_12_or_more]` |

### Sections, grades and the baseplate

Input validation: these run before anything is computed
(src/handrail/validate.py).

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `section.not_found` | A section's designation is not in the shapes database file. | Standard sections (checks.md) | `test_stop_is_triggered[section.not_found]` |
| `grade.unsupported` | A rail or post grade has no Fy or no Fu registry entry. The message names the grade and the grades supported. | W12; grades (inputs.md) | `test_stop_is_triggered[grade.unsupported]` |
| `grade.post_fu_fy_below_limit` | The post grade's Fu/Fy is below 1.20, so yielding no longer governs over rupture and Check 5 no longer covers the post wall at the weld. | W5 (welds.md); S5-13 | `test_stop_is_triggered[grade.post_fu_fy_below_limit]` |
| `weld.electrode_unsupported` | The electrode is not E70XX. | W12 | `test_stop_is_triggered[weld.electrode_unsupported]` |
| `baseplate.grade_unsupported` | The baseplate grade is not A36. | W12 | `test_stop_is_triggered[baseplate.grade_unsupported]` |
| `baseplate.smaller_than_post` | B or N is smaller than the post OD. | S4-6 | `test_stop_is_triggered[baseplate.smaller_than_post]` |
| `section.post_wider_than_rail` | The post OD is greater than the top rail OD: the coped post to rail underside detail requires post OD ≤ rail OD. Equal ODs are allowed. | W8 (welds.md) | `test_stop_is_triggered[section.post_wider_than_rail]` |
| `section.intermediate_wider_than_post` | The intermediate rail OD is greater than the post OD: its end is coped to the side of the post. Equal ODs are allowed. | S4-11 (welds.md) | `test_stop_is_triggered[section.intermediate_wider_than_post]` |

### Section families at a joint

The tables above (src/handrail/joints.py). Validation tests all three
joints before anything is computed. The Check 7 weld tests its own joint
again, so a calc computed without validation still never computes an
unlisted post.

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `joint.check3.not_supported` | The top rail and post families meet at a stop cell of the Check 3 joint's table. | S5-9; S5-1; W7 as kept by S5-3 | `test_stop_is_triggered[joint.check3.not_supported]` |
| `joint.check3.no_cell` | The top rail and post families have no cell in the Check 3 joint's table. | S5-9 (binding) | `test_stop_is_triggered[joint.check3.no_cell]` |
| `joint.check4b.not_supported` | The post and intermediate rail families meet at a stop cell of the Check 4b joint's table. | S5-9; S5-1; W7 extended by S4-12 | `test_stop_is_triggered[joint.check4b.not_supported]` |
| `joint.check4b.no_cell` | The post and intermediate rail families have no cell in the Check 4b joint's table. | S5-9 (binding) | `test_stop_is_triggered[joint.check4b.no_cell]` |
| `joint.check7.not_supported` | The post's family is a stop cell of the Check 7 joint's table. | S5-9; S5-1; W2 | `test_stop_is_triggered[joint.check7.not_supported]` |
| `joint.check7.no_cell` | The post's family has no cell in the Check 7 joint's table. | S5-9 (binding) | `test_stop_is_triggered[joint.check7.no_cell]` |

### A section the checks will not check

Raised inside the checks. Each names the ratio and the limit.

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `section.beyond_F8_limit` | A round section's D/t is not less than 0.45E/Fy, the AISC 360-22 §F8 limit of applicability. | Flexural capacity (checks.md) | `test_stop_is_triggered[section.beyond_F8_limit]` |
| `section.slender_in_flexure` | The wall is slender in flexure: D/t above λr of Table B4.1b. | Section classification (checks.md); scope.md | `test_stop_is_triggered[section.slender_in_flexure]` |
| `section.slender_in_compression` | The post wall is slender in compression: D/t above λr of Table B4.1a. | Classification in compression (checks.md); scope.md | `test_stop_is_triggered[section.slender_in_compression]` |
| `check5.second_order_not_negligible` | αPr/Pe is above the limit in a moment case of Check 5. The tool does not amplify for second-order effects. | Second-order effects: a ratio and a stop (checks.md; slice 2, D1) | `test_stop_is_triggered[check5.second_order_not_negligible]` |

### The code-value registry

CLAUDE.md rule 1 is enforced when the registry loads and when a calc reads
it (src/handrail/registry.py). These stop every calc until the registry
file is put right; no project input causes them.

| Id | Stops when | Decision | Test |
| --- | --- | --- | --- |
| `registry.file_not_found` | The registry file does not exist. | CLAUDE.md rule 1 | `test_stop_is_triggered[registry.file_not_found]` |
| `registry.invalid_toml` | The registry file is not valid TOML. | CLAUDE.md rule 1 | `test_stop_is_triggered[registry.invalid_toml]` |
| `registry.missing_field` | An entry is missing a required field. | CLAUDE.md rule 1 (code-values.md) | `test_stop_is_triggered[registry.missing_field]` |
| `registry.bad_status` | An entry's status is neither "drafted" nor "verified". | CLAUDE.md rule 1 (code-values.md) | `test_stop_is_triggered[registry.bad_status]` |
| `registry.verified_without_signoff` | An entry is marked verified with no verified-by name or date. | CLAUDE.md rule 1: only Micah marks an entry verified | `test_stop_is_triggered[registry.verified_without_signoff]` |
| `registry.drafted_with_signoff` | A drafted entry has a verified-by name or date filled in. | CLAUDE.md rule 1 (code-values.md) | `test_stop_is_triggered[registry.drafted_with_signoff]` |
| `registry.duplicate_id` | Two entries share an id. | CLAUDE.md rule 1 (code-values.md) | `test_stop_is_triggered[registry.duplicate_id]` |
| `registry.no_review_list` | The registry has no review list. | CLAUDE.md rule 1: every drafted entry is listed | `test_stop_is_triggered[registry.no_review_list]` |
| `registry.duplicate_review_id` | The review list names an id twice. | CLAUDE.md rule 1: every drafted entry is listed | `test_stop_is_triggered[registry.duplicate_review_id]` |
| `registry.review_list_mismatch` | The review list is not exactly the set of drafted entries. | CLAUDE.md rule 1: every drafted entry is listed | `test_stop_is_triggered[registry.review_list_mismatch]` |
| `registry.missing_entry` | A calc needs an entry that does not exist. The message names it. | CLAUDE.md rule 1: the tool stops naming any entry it needs that does not exist | `test_stop_is_triggered[registry.missing_entry]` |
| `registry.not_a_quantity` | The code reads a text, list or equation entry as a number. | CLAUDE.md rule 1 (code-values.md) | `test_stop_is_triggered[registry.not_a_quantity]` |
| `registry.cite_names_no_equation` | The code asks an entry for its equation number and its citation names none. | D1 (slice 1): equations have registry entries | `test_stop_is_triggered[registry.cite_names_no_equation]` |

## Stops slice 5 will add

Listed here when their code lands, in the same commit: the chord D/t limit
(S5-3); the OD tolerance inside W8 and S4-11 (S5-4, a change to two
existing stops); the A618 wall over 1-1/2 in (S5-7); the custom tube input
stops (S5-8); a grade with no Fy or Fu entry for the shape (the existing
`grade.unsupported`, now per shape).

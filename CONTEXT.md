# Handrail Designer

A checker for baseplate-mounted steel guards: one post and one span, checked
against AISC 360-22 and ASCE 7-22, output as a calculation package the
engineer of record can backcheck by hand and seal.

## Language

### Members

**Top rail**:
The uppermost horizontal member of the guard, spanning between posts and receiving the guard loads.
_Avoid_: Handrail (when meaning this member), cap rail

**Intermediate rail**:
A horizontal member below the top rail, spanning between posts, checked only for the component load.
_Avoid_: Mid rail, middle rail

**Post**:
The vertical cantilever member welded to a baseplate that supports the rails.
_Avoid_: Stanchion, upright

**Standard section**:
A section taken from AISC Shapes Database v16.0 (pipe, round HSS, rectangular HSS).

**Custom section**:
A section defined by the engineer's dimensions. Every solid bar is a custom section.

**Slender section**:
A section with any element beyond the slender limit in flexure or compression; the tool refuses to check it.

### Geometry

**Span**:
Post-to-post distance, center to center; also the tributary length for the post.
_Avoid_: Tributary area, bay

**Post height (h)**:
Distance from top of concrete to the top rail centerline.
_Avoid_: Guard height, rail height

### Loads

**Guard load**:
The ASCE 7-22 concentrated or distributed load applied to the top rail.
_Avoid_: Handrail load, rail load

**Component load**:
The ASCE 7-22 §4.5.1.2 load applied horizontally to an intermediate rail, acting alone.
_Avoid_: Infill load

**Direction case**:
One of outward, inward, downward, upward or longitudinal: the direction a guard load is applied in.

**Transverse**:
Horizontal and perpendicular to the rail; covers the outward and inward direction cases.
_Avoid_: Perpendicular (ambiguous when describing a moment)

**Longitudinal**:
Horizontal and parallel to the rail.
_Avoid_: Parallel (ambiguous when describing a moment)

**Envelope**:
The full set of direction cases and load types a check is evaluated over.

**Controlling direction**:
The direction case that produces the highest ratio for a given check.

**Engineering-judgement combination**:
A load combination the engineer of record adopts that is not an ASCE 7 combination, and is labeled as such in the output.
_Avoid_: ASCE combination (for these)

### Output

**Anchor reaction set**:
One simultaneous set of factored base shear, axial and moment from a single case, for input into anchor software; named by load direction (lateral, in any horizontal direction; upward).
_Avoid_: Max reactions, reaction envelope

**Code value**:
A number, equation or provision text taken from a referenced standard, held as an entry in the code-value registry with its exact citation and source.
_Avoid_: Constant, default

**Drafted entry**:
A registry entry written by Claude from memory or the web, or supplied directly by the engineer of record (source "engineer"), and not yet verified by the engineer of record; any calc using one is marked DRAFT.

**Verified entry**:
A registry entry the engineer of record has checked against the standard and signed off with name and date.

### Verification

**Test case**:
A project's inputs plus the values the tool's results are compared against at 0.5%; either a full-hand case (every value from the engineer of record's hand calc) or an independent-calc case.
_Avoid_: Hand case (for an independent-calc case)

**Independent calc**:
A complete calc of a test case written by an agent in a fresh session from the code, the brief, the plan's decisions, the case inputs, verified entries and AISC's Shapes Database workbook only, never from the tool's code or output.
_Avoid_: Agent calc, second opinion

**Governing-case calc**:
The engineer of record's line-by-line recomputation, by calculator, of the tool's printed controlling case of a new check, or of a new anchor reaction set, in a test case, with each provision checked against the code. Not blind; his recorded values are his own results, never copied from the tool's output. Blind independence comes from the independent calc. From slice 2 on it is done in the v1 release review, and until then its [hand] values are marked "deferred" (ADR 0006).
_Avoid_: Spot check (when meaning this)

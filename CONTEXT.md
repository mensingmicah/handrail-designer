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

### Loads

**Guard load**:
The ASCE 7-22 concentrated or distributed load applied to the top rail.
_Avoid_: Handrail load, rail load

**Component load**:
The ASCE 7-22 §4.5.1.2 load applied horizontally to an intermediate rail, acting alone.
_Avoid_: Infill load

**Direction case**:
One of outward, inward, downward or upward: the direction a guard load is applied in.

**Envelope**:
The full set of direction cases and load types a check is evaluated over.

**Controlling direction**:
The direction case that produces the highest ratio for a given check.

**Engineering-judgement combination**:
A load combination the engineer of record adopts that is not an ASCE 7 combination, and is labeled as such in the output.
_Avoid_: ASCE combination (for these)

### Output

**Anchor reaction set**:
One simultaneous set of factored base shear, axial and moment from a single case, for input into anchor software.
_Avoid_: Max reactions, reaction envelope

**Code value**:
A number taken from a referenced standard, held in the code-value registry with its citation and entered only by the engineer of record.

# Brief: welds

Part of the product brief; index in docs/BRIEF.md. Method for the weld
checks (Checks 3 and 7 in checks.md).

## Weld checks

Weld checks (3 and 7) use the elastic method, treating the weld as a line.
The AISC 360-22 §J2.4 directional strength increase is allowed for fillet
welds, based on the angle between the weld force and the weld axis; its
limits on weld groups loaded at varying angles, and any Chapter K
restrictions for welds to HSS, are registry entries to verify, and the
increase is not assumed to apply everywhere. Base metal: per inch of weld,
weld shear strength on the throat is compared with base metal shear rupture
over the thickness on the fusion face (§J2.4 with §J4.2), for both
connected parts (post wall and rail, or post wall and baseplate); the lower
governs. Minimum and maximum fillet sizes are pass/fail lines. The rail to
post weld length is the post perimeter, conservative against the true
saddle length. The post to baseplate weld moment arm is h minus the
baseplate thickness.

# Independent visual evaluator — experiment

Read the task brief and the supplied anonymous PNGs. Do not read SVG source,
model names, generation logs, developer self-assessments, or test results
until the initial visual judgment is recorded. Do not infer capabilities
from absent states; use anonymous interaction maps in a second pass.

For each design, record concrete image evidence and rate:
- Product/interaction logic: does the screen prioritize its actual job?
  Are important actions discoverable and rare actions appropriately placed?
- Visual hierarchy: what attracts attention first; is the main content clear?
- Composition/density: does every element earn space? Alignment, grouping,
  spacing and proportion; enough real content without crowding.
- Typography and craft: readable text, rhythm, meaningful contrast and details.
- Coherence: intentional styling, meaningful accent, platform appropriateness.
Use 0 = poor, 1 = material issues, 2 = adequate, 3 = polished per dimension.
These ordinal ratings are diagnostic, not an objective beauty metric.

Compare the two selected concepts directly, then the unselected concepts as
additional evidence. Choose A, B or TIE, giving two to three decisive visual
observations and relevant trade-offs. "Both inadequate" is a valid outcome.
After the image-only verdict, inspect both interaction maps for feature
coverage. A strong visual impression cannot excuse lost functionality,
inaccessible/hidden critical actions or scope/brand violations.

Absolute decision per candidate: ACCEPTABLE_CONCEPT, CHANGES_REQUIRED or
BLOCKED. Do not pass a design with serious hierarchy or product-logic
problems merely because it beats the other one. Missing image -> BLOCKED.
Static mockups do not establish working behavior, real touch-target semantics,
theme correctness, native fidelity or accessibility compliance.
Return actionable findings, not vague "make it cleaner" feedback.
For calibration first evaluate the known weak PR #25 screenshot (if supplied)
against the original product brief; it should be rejected for content priority
and scope issues. Evaluate the reference pair separately and explain actual
differences. Then freeze this rubric before judging anonymous candidates.
Record disagreement with the owner rather than tuning scores to fit one result.

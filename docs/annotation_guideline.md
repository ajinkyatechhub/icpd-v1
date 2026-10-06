# Annotation guideline (ICPD v1)

## Per image

1. Add exactly one `image_info` tag and fill every attribute. Disease names go on polygons, never in a tag.
2. Outline plant parts first, then symptoms on top of them.
3. Save (Ctrl+S) after every part. Check the Objects panel count before moving on.

## What to annotate

- **Every** leaf, stem or fruit that is in focus, not tiny, and shows symptoms. Missing a clear symptomatic part is an error: models learn unlabelled pixels as background.
- In stem close-ups, outline the stem segments and the damage. Healthy leaves can be skipped, but say so in notes.
- Skip blurred background, very small leaves, flowers and buds, hands, soil, pipes, and stakes.

## How to draw

- Polygon tool, 10-20 points along the true edge; more for complex shapes, fewer for small holes.
- Plant-part polygon on the edge; symptom polygon on the affected area (just inside the part when the whole part is affected).
- Thin features (leaf-miner trails, stems): follow the feature closely and zoom in.
- Many small spots (powdery mildew): one `cluster` polygon per dense region instead of one per spot.
- Parts running off the photo edge: put points on the edge and set `visibility = cut_by_frame`.

## Confidence rules

| Situation | Setting |
|---|---|
| Unmistakable visual sign (open borer hole with frass) | confident |
| Typical symptom without lab confirmation (virus curl) | probable |
| Can't name it (unknown insect, unexplained marks) | unsure + `insect_visible` / `unknown_symptom` |
| Image needs a specialist (look-alikes such as blight vs Tuta mines) | image `label_confidence = needs_expert` |

## Reported vs visible

Field reports go in `disease_reported` / `pests_reported` exactly as given. Draw only what is visible.
If something was reported but isn't visible, write that in notes and set `pest_evidence = field_observed_only`.

## Duplicates and splits

Photos of the same leaf or plant share a `duplicate_group` value (e.g. `RG-LEAF-01`) and must stay in the same split.

## Export

From CVAT, export both **COCO 1.0** (polygons) and **CVAT for images 1.1** (keeps the `image_info` tag, which COCO drops).

# Taxonomy

The machine-readable schema is `cvat_labels.json` (imported directly into CVAT).
In COCO, category ids 1-20 follow the order below (`image_info` is image-level, not a category).

## 1. Plant parts (polygon)

| Label | What to outline |
|---|---|
| `leaf` | One whole leaf, following its edge |
| `boll` | One cotton boll or fruit |
| `shoot_stem` | A stem or shoot segment |
| `whole_plant` | One entire plant (only when it is clearly separable from neighbours) |

Attributes (all plant parts):

| Attribute | Values | Meaning |
|---|---|---|
| visibility | full / partial / cut_by_frame | partial = hidden by another object; cut_by_frame = runs off the photo edge |
| status | symptomatic / healthy / dead | |
| severity | 0, 1, 2, 3, 4, 5 | share of this part affected: 0 none, 1 <5%, 2 5-10%, 3 10-25%, 4 25-50%, 5 >50% |

## 2. Symptoms and pests (polygon, drawn on or inside a plant part)

| Label | Type | Visual definition |
|---|---|---|
| `leaf_curl_virus` | disease | Puckered, crinkled, upward- or downward-curling leaf tissue (begomovirus complex, whitefly/thrips-vectored) |
| `shoot_borer_damage` | pest damage | Entry or exit hole, tunnel, or frass on a shoot or stem |
| `wilted_shoot` | symptom | Drooping or withered shoot tip |
| `insect_visible` | pest | Any insect visible in the photo; species goes in notes when known |
| `powdery_mildew` | disease | White powdery spots or patches on the leaf surface |
| `downy_mildew` | disease | Angular, vein-bounded yellow patches, later brown |
| `leaf_miner_mine` | pest damage | Thin, winding, pale serpentine trail inside the leaf |
| `leaf_miner_blotch` | pest damage | Pale, papery blotch mine (e.g. Tuta absoluta on tomato) |
| `boll_rot_lesion` | disease | Dark, sunken or discoloured patch on a boll or fruit |
| `leaf_reddening_necrosis` | symptom | Red or bronze discoloration with brown dead tissue (hopperburn, Mg deficiency look-alike) |
| `early_blight` | disease | Brown lesion with concentric rings, often with a yellow halo |
| `late_blight` | disease | Large, water-soaked, dark lesions, often at the leaf edge |
| `leaf_spot` | disease | Small, distinct spots that don't fit the classes above |
| `vascular_wilt` | disease | Whole-plant or branch wilting from vascular blockage |
| `mechanical_damage` | abiotic | Tears, cuts, hail or handling damage |
| `unknown_symptom` | unknown | Abnormal tissue whose cause can't be told from the photo |

Attributes (all symptoms and pests):

| Attribute | Values | Meaning |
|---|---|---|
| instance_type | single / cluster | cluster = one polygon around many small spots (COCO iscrowd = 1) |
| confidence | confident / probable / unsure | annotator's confidence in this specific label |

## 3. Image level (`image_info` tag, one per image)

| Attribute | Values |
|---|---|
| crop | chilli, brinjal, ridge_gourd, cotton, tomato, other |
| quality | good, slightly_blurred, reject |
| view | leaf_close_up, stem_close_up, boll_fruit, whole_plant |
| overall_health | healthy, mild, moderate, severe |
| disease_reported | free text, as reported by the field team |
| pests_reported | free text, as reported by the field team |
| pest_evidence | visible_in_photo, field_observed_only, none |
| label_confidence | confident, probable, needs_expert |
| duplicate_group | free text; same value = near-duplicate photos of the same subject |
| notes | free text: what is visible, what was deliberately not annotated, and why |

`group_id` (plant or plot) is added in `metadata.csv` for split control.

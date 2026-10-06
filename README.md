# ICPD v1: Indian Crop Pest & Disease field images (batch 01)

Field photographs of Indian vegetable crops with polygon annotations of plant parts,
disease symptoms and pest damage, plus image-level diagnosis metadata.
Built by Ajinkya Tech from its own field photos. No internet images.

| | |
|---|---|
| Version | 1.0.0-batch01 (2026-10-07) |
| Images | 5 annotated (1 chilli, 4 brinjal); 7 more captured and pending annotation |
| Annotations | 44 polygons across 7 classes in use (20 defined) |
| Formats | COCO instance segmentation, YOLO segmentation |
| Annotation tool | CVAT (app.cvat.ai), manual polygons |
| Licence | Proprietary, all rights reserved. See [LICENSE.md](LICENSE.md) |

## Folder structure

```
icpd-v1/
├── README.md                     this file (dataset card)
├── LICENSE.md
├── CHANGELOG.md
├── checksums.sha256              SHA-256 of every file under data/, schema/, source/, scripts/, docs/
├── requirements.txt
├── data/                         THE RELEASE: use this folder
│   ├── images/                   ICPD-000001.jpg …   EXIF removed
│   ├── annotations/
│   │   ├── coco/instances.json   COCO polygons + per-annotation attributes + per-image image_info
│   │   └── yolo_seg/             labels/*.txt, classes.txt, data.yaml
│   ├── metadata.csv              one row per image (crop, view, health, reported disease/pests, evidence, confidence, notes)
│   ├── splits/groups.csv         group ids for leakage-free train/val/test splitting
│   └── previews/                 images with annotations drawn on, for quick review
├── schema/
│   ├── cvat_labels.json          exact label + attribute schema used in CVAT
│   └── taxonomy.md               every label, attribute and value explained
├── docs/
│   ├── annotation_guideline.md   rules annotators followed
│   ├── qa_report.md              checks run, statistics, known limitations
│   └── corrections_log.md        every change applied on top of the raw export
├── source/                       raw inputs (never edited)
│   ├── cvat_export/              untouched CVAT "COCO 1.0" export
│   ├── images/                   EXIF-stripped originals
│   ├── image_info.csv            image-level labels (CVAT image_info tag)
│   └── corrections.json          machine-readable corrections
├── pending/manifest.csv          captured images not yet annotated, with field notes
└── scripts/
    ├── build_release.py          source/  ->  data/   (fully reproducible)
    └── validate.py               integrity and schema checks
```

## Label design

Two layers of polygons plus one image-level record:

1. **Plant parts**: `leaf`, `shoot_stem`, `boll`, `whole_plant`, each with `visibility` (full / partial / cut_by_frame), `status` (symptomatic / healthy / dead) and `severity` 0-5 (0 none, 1 <5%, 2 5-10%, 3 10-25%, 4 25-50%, 5 >50% of the part affected).
2. **Symptoms and pests**: e.g. `leaf_curl_virus`, `shoot_borer_damage`, `wilted_shoot`, `insect_visible`, `powdery_mildew`, `leaf_miner_mine`, each with `instance_type` (single / cluster) and `confidence` (confident / probable / unsure). `cluster` regions are exported with COCO `iscrowd = 1`.
3. **Image level** (`image_info`): crop, quality, view, overall health, disease and pests **as reported by the field team**, `pest_evidence` (visible_in_photo / field_observed_only / none), `label_confidence` (confident / probable / needs_expert), `duplicate_group` and free-text notes.

Full definitions: [schema/taxonomy.md](schema/taxonomy.md).

## Design decisions that matter for model training

- **Reported vs visible are kept separate.** `disease_reported` / `pests_reported` record what the field team saw on the plant. Polygons record only what is visible in the photo. For example, leaf miner was reported on the brinjal plants but no mines are visible in these photos, so none are drawn and `notes` says so.
- **Uncertainty is labelled, not hidden.** Virus diagnoses are `probable` (no lab test). Unidentified insects are `insect_visible` + `unsure`. Unexplained marks are `unknown_symptom`.
- **Complete annotation per image.** Every in-focus, non-tiny symptomatic leaf or stem is outlined. Deliberate omissions (blurred background, hands, flowers, healthy leaves in stem close-ups) are listed in each image's notes.
- **Leakage-free splits.** Images are grouped by plant or plot (`group_id`) and by near-duplicate (`duplicate_group`). A group must never be split across train and test. With only 5 images, splits are `unassigned` in this batch.
- **No pesticide advice in this release.** Any future advisory content will use doses only from the CIB&RC registered label for that crop and pest.

## Class counts (batch 01)

| Class | Polygons | Images |
|---|---|---|
| leaf | 13 | 1 |
| leaf_curl_virus | 13 | 1 |
| shoot_stem | 6 | 4 |
| shoot_borer_damage | 6 | 3 |
| insect_visible | 3 | 2 |
| wilted_shoot | 2 | 2 |
| unknown_symptom | 1 | 1 |
| **Total** | **44** | **5** |

## Quick start

```python
import json
coco = json.load(open("data/annotations/coco/instances.json"))
cats = {c["id"]: c["name"] for c in coco["categories"]}
for img in coco["images"]:
    anns = [a for a in coco["annotations"] if a["image_id"] == img["id"]]
    print(img["file_name"], img["image_info"]["crop"], [cats[a["category_id"]] for a in anns])
```

pycocotools works directly on `instances.json`. For YOLO segmentation, point your trainer at `data/annotations/yolo_seg/data.yaml`.

Rebuild and check everything from the raw export:

```bash
pip install -r requirements.txt
python3 scripts/build_release.py
python3 scripts/validate.py
```

## Known limitations

See [docs/qa_report.md](docs/qa_report.md). In short: this is a small first batch (5 images, 2 crops). Diagnoses are visual, not lab-confirmed. Insect species are not identified. Single annotator, and an independent second review is still pending.

## Contact

Ajinkya Tech, ajinkyatechhub on GitHub.

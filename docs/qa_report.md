# QA report: 1.0.0-batch01

## Automated checks (`scripts/validate.py`): all passed

- 5 images exist, open, match COCO width/height, and carry no EXIF metadata.
- 44 annotations: valid category, at least 3 points, all points inside the image, area > 0.
- Every attribute value is allowed by `schema/cvat_labels.json`, and no required attribute is missing.
- Every image has image-level info with allowed values.
- YOLO label files exist for all 5 images, with polygon counts equal to COCO.
- `checksums.sha256` matches every file on disk.

## Manual review

- Every image was annotated with a step-by-step reference overlay, then checked against a screenshot from CVAT.
- Default attribute values (`full` / `0` / `probable`) left by mistake were checked shape by shape. None remain in the export.
- Previews in `data/previews/` were inspected for polygon placement.

## Corrections

2 attribute corrections on ICPD-000003 (main stem and branch `status`/`severity` were swapped). Logged in `docs/corrections_log.md` and applied by the build script; the raw export is unchanged.

## Statistics

| Image | Crop | View | Polygons | Health |
|---|---|---|---|---|
| ICPD-000001 | chilli | leaf_close_up | 26 (13 leaf + 13 leaf_curl_virus) | moderate |
| ICPD-000002 | brinjal | stem_close_up | 4 | moderate |
| ICPD-000003 | brinjal | stem_close_up | 5 | mild |
| ICPD-000004 | brinjal | whole_plant | 4 | moderate |
| ICPD-000005 | brinjal | stem_close_up | 5 | severe |

## Known limitations

1. **Small batch**: 5 images, 2 crops, 2 plant/plot groups. Not enough for train/val/test yet, so splits are `unassigned`.
2. **No lab confirmation**: leaf curl is a visual diagnosis (`probable`). The borer larva in ICPD-000005 is unconfirmed.
3. **Insects not identified to species**: ICPD-000003 insects look ant-like, so they're labelled `insect_visible` + `unsure`.
4. **Reported leaf miner not visible** on brinjal images 2-5. It's kept in `disease_reported`, but no mine polygons are drawn.
5. **Image-level info source**: CVAT's COCO export does not include tags. `image_info` was compiled from the annotation session values in `source/image_info.csv`. Next batch: also export "CVAT for images 1.1" and reconcile.
6. **Single annotator**: an independent second annotator or agronomist review is pending. Inter-annotator agreement is not yet measured.
7. **Location and date**: field, district and capture date are not yet recorded for every image.

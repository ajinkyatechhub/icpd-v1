# QA report: 1.2.0

## Automated checks (`scripts/validate.py`): all passed

- 12 images exist, open, match COCO width/height, and carry no EXIF metadata.
- 104 annotations: valid category, at least 3 points, all points inside the image, area > 0.
- Every attribute value is allowed by `schema/cvat_labels.json`, and no required attribute is missing.
- Every image has image-level info with allowed values.
- YOLO label files exist for all 12 images, with polygon counts equal to COCO.
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
| ICPD-000006 | ridge_gourd | leaf_close_up | 11 (2 leaf, 5 powdery_mildew, 4 leaf_miner_mine) | moderate |
| ICPD-000007 | ridge_gourd | leaf_close_up | 11 (3 leaf, 7 downy_mildew, 1 mechanical_damage) | severe |
| ICPD-000008 | ridge_gourd | leaf_close_up | 11 (2 leaf, 5 powdery_mildew, 4 leaf_miner_mine) | moderate |
| ICPD-000009 | cotton | boll_fruit | 10 (2 boll, 3 leaf, 1 boll_rot_lesion, 4 leaf_reddening_necrosis) | moderate |
| ICPD-000010 | cotton | boll_fruit | 2 (1 boll, 1 boll_rot_lesion) | moderate |
| ICPD-000011 | tomato | leaf_close_up | 10 (6 leaf, 4 unknown_symptom) | moderate |
| ICPD-000012 | tomato | whole_plant | 5 (1 whole_plant, 1 shoot_stem, 3 vascular_wilt) | severe |

## Known limitations

1. **Small set**: 12 images, 5 crops, 5 plant/plot groups. Not enough for train/val/test yet, so splits are `unassigned`.
2. **No lab confirmation**: leaf curl is a visual diagnosis (`probable`). The borer larva in ICPD-000005 is unconfirmed.
3. **Insects not identified to species**: ICPD-000003 insects look ant-like, so they're labelled `insect_visible` + `unsure`.
4. **Reported leaf miner not visible** on brinjal images 2-5. It's kept in `disease_reported`, but no mine polygons are drawn.
5. **Image-level info source**: CVAT's COCO export does not include tags. `image_info` was compiled from the annotation session values in `source/image_info.csv`. Next batch: also export "CVAT for images 1.1" and reconcile.
6. **Single annotator**: an independent second annotator or agronomist review is pending. Inter-annotator agreement is not yet measured.
7. **Look-alikes needing confirmation**: downy mildew on ICPD-000007 needs an underside photo; red leaf margins on ICPD-000009 could be jassid hopperburn, magnesium deficiency or senescence (`needs_expert`); pink bollworm on ICPD-000010 needs boll dissection; tomato leaflet patches on ICPD-000011 (blight vs Tuta absoluta mines) need a light/dissection check, and one small dry strip on its left leaflet is not annotated; wilt on ICPD-000012 needs a stem-cut or ooze test (Fusarium vs bacterial).
8. **Location and date**: field, district and capture date are not yet recorded for every image.

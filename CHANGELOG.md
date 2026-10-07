# Changelog

## 1.1.0-batch02 (2026-10-07)

- Added 5 annotated images: ICPD-000006 to 000008 (ridge gourd: powdery mildew, downy mildew, leaf miner trails) and ICPD-000009 to 000010 (cotton: boll rot, leaf reddening/necrosis). 45 new polygons, 89 in total.
- Cluster regions (powdery mildew, downy mildew, boll rot, reddening) exported with iscrowd = 1.
- ICPD-000006 and ICPD-000008 share duplicate_group RG-LEAF-01 (same leaf); new group ids G03-RIDGEGOURD and G04-COTTON.
- Leaf-miner trails on ICPD-000006 redrawn as thin polygons following each trail.
- Pending: ICPD-000011 and 000012 (tomato).

## 1.0.0-batch01 (2026-10-07)

- First release: 5 annotated field images (ICPD-000001 chilli, ICPD-000002 to 000005 brinjal), 44 polygons.
- COCO and YOLO-segmentation exports, metadata.csv, group ids for splitting, previews.
- Two attribute corrections applied on ICPD-000003 (stem status swap); see docs/corrections_log.md.
- 7 further images (ridge gourd, cotton, tomato) captured and listed in pending/manifest.csv.

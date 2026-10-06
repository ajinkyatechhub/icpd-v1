#!/usr/bin/env python3
"""Validate the ICPD release. Exits non-zero if any check fails.

Checks:
  - every image in COCO exists, opens, matches width/height, and has no EXIF
  - every annotation has a valid category, a polygon of >= 3 points inside the image,
    a non-zero area, and attribute values allowed by schema/cvat_labels.json
  - every image has image-level info with allowed values
  - YOLO label files exist for every image and line counts match COCO
  - checksums.sha256 matches the files on disk
Usage:  python3 scripts/validate.py
"""
import csv
import hashlib
import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def err(msg):
    errors.append(msg)


schema = {lab["name"]: lab for lab in json.load(open(os.path.join(ROOT, "schema", "cvat_labels.json")))}
allowed = {name: {a["name"]: set(a["values"]) for a in lab["attributes"] if a["input_type"] == "select"}
           for name, lab in schema.items()}

coco = json.load(open(os.path.join(ROOT, "data", "annotations", "coco", "instances.json")))
cats = {c["id"]: c["name"] for c in coco["categories"]}
imgs = {im["id"]: im for im in coco["images"]}

for im in coco["images"]:
    p = os.path.join(ROOT, "data", "images", im["file_name"])
    if not os.path.exists(p):
        err(f"missing image {im['file_name']}")
        continue
    with Image.open(p) as f:
        if f.size != (im["width"], im["height"]):
            err(f"{im['file_name']}: size {f.size} != COCO {(im['width'], im['height'])}")
        if len(f.getexif()):
            err(f"{im['file_name']}: EXIF present")
    for k, v in im["image_info"].items():
        if k in allowed["image_info"] and v not in allowed["image_info"][k]:
            err(f"{im['file_name']}: image_info {k}={v!r} not allowed")

seen = set()
for a in coco["annotations"]:
    im = imgs.get(a["image_id"])
    name = cats.get(a["category_id"])
    if im is None or name is None:
        err(f"annotation {a['id']}: bad image or category")
        continue
    seen.add(a["image_id"])
    for poly in a["segmentation"]:
        if len(poly) < 6:
            err(f"annotation {a['id']} ({name}): polygon has fewer than 3 points")
        for x, y in zip(poly[0::2], poly[1::2]):
            if not (-1 <= x <= im["width"] + 1 and -1 <= y <= im["height"] + 1):
                err(f"annotation {a['id']} ({name}): point ({x},{y}) outside image")
                break
    if a["area"] <= 0:
        err(f"annotation {a['id']} ({name}): zero area")
    for k, v in a["attributes"].items():
        if str(v) not in allowed[name].get(k, {str(v)}):
            err(f"annotation {a['id']} ({name}): {k}={v!r} not allowed")
    for k in allowed[name]:
        if k not in a["attributes"]:
            err(f"annotation {a['id']} ({name}): missing attribute {k}")

for i, im in imgs.items():
    if i not in seen:
        err(f"{im['file_name']}: no annotations")
    stem = os.path.splitext(im["file_name"])[0]
    yp = os.path.join(ROOT, "data", "annotations", "yolo_seg", "labels", stem + ".txt")
    if not os.path.exists(yp):
        err(f"{im['file_name']}: missing YOLO label file")
    else:
        n_yolo = sum(1 for line in open(yp) if line.strip())
        n_coco = sum(len(a["segmentation"]) for a in coco["annotations"] if a["image_id"] == i)
        if n_yolo != n_coco:
            err(f"{im['file_name']}: YOLO has {n_yolo} polygons, COCO has {n_coco}")

for line in open(os.path.join(ROOT, "checksums.sha256")):
    h, rel = line.rstrip("\n").split("  ", 1)
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        err(f"checksum: missing {rel}")
    elif hashlib.sha256(open(p, "rb").read()).hexdigest() != h:
        err(f"checksum mismatch: {rel}")

n_ann = len(coco["annotations"])
print(f"Checked {len(imgs)} images, {n_ann} annotations, {len(coco['categories'])} categories")
if errors:
    print(f"FAILED: {len(errors)} problem(s)")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("ALL CHECKS PASSED")

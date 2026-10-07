#!/usr/bin/env python3
"""Build the ICPD release from the raw CVAT export.

Inputs (never edited by this script):
  source/cvat_export/instances_default.json   CVAT "COCO 1.0" export
  source/images/*.jpg                          EXIF-stripped field photos
  source/image_info.csv                        image-level labels (the CVAT image_info tag)
  source/corrections.json                      logged fixes applied on top of the export
  schema/cvat_labels.json                      label schema used in CVAT

Outputs (regenerated every run):
  data/images/                 images in the release
  data/annotations/coco/instances.json
  data/annotations/yolo_seg/   YOLO segmentation labels + classes.txt + data.yaml
  data/metadata.csv            one row per image
  data/splits/groups.csv       group ids for leakage-free splitting
  data/previews/               images with annotations drawn on, for review
  docs/corrections_log.md      every correction applied
  checksums.sha256

Usage:  python3 scripts/build_release.py
Needs:  Pillow
"""
import csv
import hashlib
import json
import os
import shutil
from collections import Counter, defaultdict

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
OUT = os.path.join(ROOT, "data")

VERSION = "1.2.0"
RELEASE_DATE = "2026-10-07"

PART_LABELS = {"leaf", "boll", "shoot_stem", "whole_plant"}
PEST_LABELS = {"insect_visible", "shoot_borer_damage", "leaf_miner_mine", "leaf_miner_blotch"}
TAG_LABEL = "image_info"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def supercategory(name):
    if name in PART_LABELS:
        return "plant_part"
    if name in PEST_LABELS:
        return "pest_or_pest_damage"
    if name == "unknown_symptom":
        return "unknown"
    return "disease_or_symptom"


def polygon_area(flat):
    xs, ys = flat[0::2], flat[1::2]
    n = len(xs)
    return abs(sum(xs[i] * ys[(i + 1) % n] - xs[(i + 1) % n] * ys[i] for i in range(n))) / 2.0


def reset_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path)


def main():
    raw = load_json(os.path.join(SRC, "cvat_export", "instances_default.json"))
    schema = load_json(os.path.join(ROOT, "schema", "cvat_labels.json"))
    corrections = load_json(os.path.join(SRC, "corrections.json"))
    with open(os.path.join(SRC, "image_info.csv"), encoding="utf-8") as f:
        info = {row["file_name"]: row for row in csv.DictReader(f)}

    # Release = images that have both annotations and image-level info.
    annotated_ids = {a["image_id"] for a in raw["annotations"]}
    images = [im for im in raw["images"] if im["id"] in annotated_ids and im["file_name"] in info]
    images.sort(key=lambda im: im["file_name"])
    keep_ids = {im["id"] for im in images}

    # Categories: drop the tag-only label, renumber 1..N in schema order.
    shape_names = [lab["name"] for lab in schema if lab["name"] != TAG_LABEL]
    new_cat = {name: i + 1 for i, name in enumerate(shape_names)}
    raw_cat = {c["id"]: c["name"] for c in raw["categories"]}
    categories = [{"id": new_cat[n], "name": n, "supercategory": supercategory(n)} for n in shape_names]

    # Apply logged corrections.
    anns = [dict(a) for a in raw["annotations"] if a["image_id"] in keep_ids]
    by_id = {a["id"]: a for a in anns}
    log = []
    for c in corrections:
        a = by_id[c["annotation_id"]]
        for k, v in c["from"].items():
            if a["attributes"].get(k) != v:
                raise SystemExit(f"Correction for annotation {a['id']} expected {k}={v}, found {a['attributes'].get(k)}")
        a["attributes"] = {**a["attributes"], **c["to"]}
        log.append(c)

    # Clean annotations.
    clean = []
    for a in sorted(anns, key=lambda a: (a["image_id"], a["id"])):
        name = raw_cat[a["category_id"]]
        attrs = {k: v for k, v in a["attributes"].items() if k != "occluded"}
        if "severity" in attrs:
            attrs["severity"] = int(attrs["severity"])
        seg = a["segmentation"]
        iscrowd = 1 if attrs.get("instance_type") == "cluster" else 0
        clean.append({
            "id": len(clean) + 1,
            "image_id": a["image_id"],
            "category_id": new_cat[name],
            "segmentation": seg,
            "area": round(sum(polygon_area(p) for p in seg), 2),
            "bbox": [round(v, 2) for v in a["bbox"]],
            "iscrowd": iscrowd,
            "attributes": attrs,
            "source_annotation_id": a["id"],
        })

    # Images with image-level labels attached.
    out_images = []
    for im in images:
        row = info[im["file_name"]]
        out_images.append({
            "id": im["id"],
            "file_name": im["file_name"],
            "width": im["width"],
            "height": im["height"],
            "license": 1,
            "image_info": {k: row[k] for k in row if k != "file_name"},
        })

    coco = {
        "info": {
            "description": "Indian Crop Pest & Disease dataset (ICPD), field photos with polygon annotations",
            "version": VERSION,
            "year": 2026,
            "contributor": "Ajinkya Tech",
            "date_created": RELEASE_DATE,
            "url": "",
        },
        "licenses": [{"id": 1, "name": "Proprietary - see LICENSE.md", "url": ""}],
        "images": out_images,
        "annotations": clean,
        "categories": categories,
    }

    # ---- write images ----
    img_out = os.path.join(OUT, "images")
    reset_dir(img_out)
    for im in images:
        shutil.copy2(os.path.join(SRC, "images", im["file_name"]), os.path.join(img_out, im["file_name"]))

    # ---- COCO ----
    coco_dir = os.path.join(OUT, "annotations", "coco")
    reset_dir(coco_dir)
    with open(os.path.join(coco_dir, "instances.json"), "w", encoding="utf-8") as f:
        json.dump(coco, f, indent=1, ensure_ascii=False)

    # ---- YOLO segmentation ----
    yolo_dir = os.path.join(OUT, "annotations", "yolo_seg")
    reset_dir(os.path.join(yolo_dir, "labels"))
    with open(os.path.join(yolo_dir, "classes.txt"), "w") as f:
        f.write("\n".join(shape_names) + "\n")
    with open(os.path.join(yolo_dir, "data.yaml"), "w") as f:
        f.write("# Ultralytics-style dataset file. Paths are relative to this folder.\n")
        f.write("path: ../..\ntrain: images\nval: images\n")
        f.write(f"nc: {len(shape_names)}\nnames:\n")
        for i, n in enumerate(shape_names):
            f.write(f"  {i}: {n}\n")
    ann_by_img = defaultdict(list)
    for a in clean:
        ann_by_img[a["image_id"]].append(a)
    for im in images:
        lines = []
        for a in ann_by_img[im["id"]]:
            for poly in a["segmentation"]:
                pts = [f"{(poly[i] / im['width']):.6f} {(poly[i + 1] / im['height']):.6f}" for i in range(0, len(poly), 2)]
                lines.append(f"{a['category_id'] - 1} " + " ".join(pts))
        stem = os.path.splitext(im["file_name"])[0]
        with open(os.path.join(yolo_dir, "labels", stem + ".txt"), "w") as f:
            f.write("\n".join(lines) + "\n")

    # ---- metadata.csv ----
    with open(os.path.join(OUT, "metadata.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        cols = ["file_name", "width", "height", "crop", "quality", "view", "overall_health",
                "disease_reported", "pests_reported", "pest_evidence", "label_confidence",
                "duplicate_group", "group_id", "num_annotations", "labels_present", "notes"]
        w.writerow(cols)
        for im in images:
            row = info[im["file_name"]]
            names = Counter(shape_names[a["category_id"] - 1] for a in ann_by_img[im["id"]])
            w.writerow([im["file_name"], im["width"], im["height"]] +
                       [row[c] for c in cols[3:13]] +
                       [sum(names.values()), "; ".join(f"{k}:{v}" for k, v in sorted(names.items())), row["notes"]])

    # ---- splits ----
    split_dir = os.path.join(OUT, "splits")
    reset_dir(split_dir)
    with open(os.path.join(split_dir, "groups.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file_name", "group_id", "duplicate_group", "split"])
        for im in images:
            row = info[im["file_name"]]
            w.writerow([im["file_name"], row["group_id"], row["duplicate_group"], "unassigned"])

    # ---- previews ----
    render_previews(images, ann_by_img, shape_names, os.path.join(OUT, "previews"))

    # ---- corrections log ----
    with open(os.path.join(ROOT, "docs", "corrections_log.md"), "w") as f:
        f.write("# Corrections log\n\nCorrections applied on top of the raw CVAT export by `scripts/build_release.py`.\n")
        f.write("The raw export in `source/cvat_export/` is never edited.\n\n")
        f.write("| Image | Source annotation id | Changed | From | To | Reason |\n|---|---|---|---|---|---|\n")
        for c in log:
            f.write(f"| {c['file_name']} | {c['annotation_id']} | {c['field']} | {c['from']} | {c['to']} | {c['reason']} |\n")

    write_checksums()
    print(f"Built {VERSION}: {len(images)} images, {len(clean)} annotations, {len(log)} corrections applied")


COLORS = {
    "plant_part": (40, 200, 60),
    "disease_or_symptom": (170, 60, 230),
    "pest_or_pest_damage": (235, 50, 40),
    "unknown": (255, 170, 0),
}


def render_previews(images, ann_by_img, names, out_dir):
    reset_dir(out_dir)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for im in images:
        base = Image.open(os.path.join(OUT, "images", im["file_name"])).convert("RGBA")
        layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        anns = sorted(ann_by_img[im["id"]], key=lambda a: supercategory(names[a["category_id"] - 1]) != "plant_part")
        for a in anns:
            name = names[a["category_id"] - 1]
            col = COLORS[supercategory(name)]
            for poly in a["segmentation"]:
                pts = list(zip(poly[0::2], poly[1::2]))
                d.polygon(pts, fill=col + (45,))
                d.line(pts + [pts[0]], fill=col + (255,), width=3)
        out = Image.alpha_composite(base, layer).convert("RGB")
        d = ImageDraw.Draw(out)
        for a in anns:
            name = names[a["category_id"] - 1]
            if supercategory(name) == "plant_part":
                continue
            x, y = a["bbox"][0], max(0, a["bbox"][1] - 22)
            d.text((x, y), name, font=font, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
        legend = "green: part  purple: disease  red: pest  orange: unknown"
        d.rectangle((0, out.height - 30, out.width, out.height), fill=(0, 0, 0))
        d.text((8, out.height - 26), legend, font=font, fill=(255, 255, 255))
        stem = os.path.splitext(im["file_name"])[0]
        out.save(os.path.join(out_dir, stem + "_preview.jpg"), quality=88)


def write_checksums():
    lines = []
    for base in ["data", "schema", "source", "scripts", "docs"]:
        for dirpath, _, files in os.walk(os.path.join(ROOT, base)):
            for fn in sorted(files):
                p = os.path.join(dirpath, fn)
                if "__pycache__" in p:
                    continue
                with open(p, "rb") as f:
                    lines.append(f"{hashlib.sha256(f.read()).hexdigest()}  {os.path.relpath(p, ROOT)}")
    with open(os.path.join(ROOT, "checksums.sha256"), "w") as f:
        f.write("\n".join(sorted(lines, key=lambda l: l.split("  ", 1)[1])) + "\n")


if __name__ == "__main__":
    main()

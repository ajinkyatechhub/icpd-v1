# Corrections log

Corrections applied on top of the raw CVAT export by `scripts/build_release.py`.
The raw export in `source/cvat_export/` is never edited.

| Image | Source annotation id | Changed | From | To | Reason |
|---|---|---|---|---|---|
| ICPD-000003.jpg | 31 | attributes | {'status': 'healthy', 'severity': '0'} | {'status': 'symptomatic', 'severity': '1'} | Main stem (node down to bottom edge) carries the dark marks; status was swapped with the branch polygon during annotation. |
| ICPD-000003.jpg | 35 | attributes | {'status': 'symptomatic', 'severity': '1'} | {'status': 'healthy', 'severity': '0'} | Up-right branch shows no symptoms; status was swapped with the main stem polygon during annotation. |

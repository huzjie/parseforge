"""Reading order: sort regions top-to-bottom, then left-to-right.

For multi-column layouts a true reader uses column detection; here we use a
band-based sort (group by vertical band, sort within band by x) which is the
standard first approximation and keeps the output JSON in document flow.
"""


def reading_order(regions, band=0.5):
    """Return region indices sorted in reading order.

    ``band`` is a fraction of the median region height used to group rows.
    """
    if not regions:
        return []
    heights = [r["bbox"]["y1"] - r["bbox"]["y0"] for r in regions]
    median = sorted(heights)[len(heights) // 2] if heights else 1
    tol = max(1.0, median * band)
    indexed = sorted(enumerate(regions),
                     key=lambda ir: (ir[1]["bbox"]["y0"], ir[1]["bbox"]["x0"]))
    # group into bands by y0 proximity
    bands = []
    cur = []
    cur_y = None
    for idx, r in indexed:
        y0 = r["bbox"]["y0"]
        if cur_y is None or abs(y0 - cur_y) <= tol:
            cur.append((idx, r))
            if cur_y is None:
                cur_y = y0
        else:
            bands.append(cur)
            cur = [(idx, r)]
            cur_y = y0
    if cur:
        bands.append(cur)
    order = []
    for band_regions in bands:
        for idx, _r in sorted(band_regions, key=lambda ir: ir[1]["bbox"]["x0"]):
            order.append(idx)
    return order

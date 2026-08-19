"""Fetch exact 16-bit crops from the Archimedes Palimpsest mirror via HTTP range
requests. The rasters are 8160x10880x3 uncompressed 16-bit (532 MB each), so we
parse the remote IFD, then pull only the byte range covering the rows we want.
No resampling, no format conversion: the integers that land here are the
integers the camera wrote (A1 preserved from the source).
"""
import struct
import subprocess
import sys

import numpy as np

BASE = ("https://mirrors.rit.edu/archie/post-2007/HTML_TIFF/Data/16bit_tif/")


def curl(url, rng=None, out=None, timeout=300):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if rng:
        cmd += ["-r", rng]
    cmd += [url, "-o", out]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl failed {r.returncode}: {r.stderr[:200]}")
    return out


def read_ifd(url):
    curl(url, "0-4095", "/tmp/_hdr.bin", timeout=90)
    d = open("/tmp/_hdr.bin", "rb").read()
    end = "<" if d[:2] == b"II" else ">"
    off = struct.unpack(end + "I", d[4:8])[0]
    n = struct.unpack(end + "H", d[off:off + 2])[0]
    tags = {}
    for i in range(n):
        e = d[off + 2 + i * 12: off + 14 + i * 12]
        tag, typ, cnt = struct.unpack(end + "HHI", e[:8])
        tags[tag] = struct.unpack(end + "I", e[8:12])[0]
    return {
        "end": end,
        "width": tags[256], "height": tags[257],
        "spp": tags.get(277, 3), "strip": tags[273],
        "compression": tags.get(259, 1),
    }


def fetch_rows(url, r0, nrows, dest):
    info = read_ifd(url)
    if info["compression"] != 1:
        raise RuntimeError("compressed TIFF — range crop not applicable")
    stride = info["width"] * info["spp"] * 2
    start = info["strip"] + r0 * stride
    end_b = start + nrows * stride - 1
    curl(url, f"{start}-{end_b}", dest)
    raw = np.fromfile(dest, dtype=("<u2" if info["end"] == "<" else ">u2"))
    exp = nrows * info["width"] * info["spp"]
    if raw.size < exp:
        nrows = raw.size // (info["width"] * info["spp"])
        raw = raw[:nrows * info["width"] * info["spp"]]
    return raw.reshape(nrows, info["width"], info["spp"]).astype(np.int64), info


if __name__ == "__main__":
    folio, band, r0, nrows, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    c0, c1 = (int(x) for x in cols.split(":"))
    url = f"{BASE}{folio}_Sinar_{band}_01_raw.tif"
    arr, info = fetch_rows(url, r0, nrows, "/tmp/_rows.bin")
    crop = arr[:, c0:c1, :]
    np.save(f"/home/claude/corpus/{folio}_{band}.npy", crop)
    print(f"{folio} {band}: {crop.shape} dtype=int64 "
          f"min={int(crop.min())} max={int(crop.max())} src={info['width']}x{info['height']}")

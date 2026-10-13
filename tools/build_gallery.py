#!/usr/bin/env python3
"""
SerGo Photography — build script.

What it does (run it every time you add, remove or change photos):
  1. Reads the original photos in newgallery/images/fulls/<album>/ (never modified).
  2. Creates web versions in newgallery/images/web/<album>/ at several widths,
     high-quality WebP (quality 90), keeping the sRGB colour profile and EXIF.
  3. Does the same, at fewer sizes, for the unprocessed versions in
     newgallery/images/raw/<album>/<name>_ori.jpg (the "raw" view), if present.
  4. Reads ISO, shutter speed, aperture, focal length, camera and date from EXIF
     (no exiftool needed).
  5. Writes the five gallery pages newgallery/<album>.html.
  6. Creates web versions of the cover photo (cover/cover.jpg).

Only new or changed photos are processed, so re-running it is quick.

Requirements: Python 3.8+ and Pillow 9+  ->  pip install Pillow
Usage (from anywhere):  python tools/build_gallery.py
"""

from __future__ import annotations

import html
import io
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

try:
    from PIL import Image, ImageCms, ImageOps
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

ROOT = Path(__file__).resolve().parent.parent
GALLERY = ROOT / "newgallery"
FULLS = GALLERY / "images" / "fulls"
RAWS = GALLERY / "images" / "raw"
WEB = GALLERY / "images" / "web"
COVER = ROOT / "cover"
SITE_URL = "https://asergom.github.io/sergophotography/"  # used for social-media previews

# Album order = order in the menus.  (folder name, title shown, icon file)
ALBUMS = [
    ("thenightof", "The night of", "thenightoflogo.svg"),
    ("streetwalking", "Street walking", "streetwalkinglogo.svg"),
    ("shapes", "Shapes", "shapeslogo.svg"),
    ("everyday", "Everyday", "everydaylogo.svg"),
    ("outland", "Outland", "outlandlogo.svg"),
]

WIDTHS = [480, 960, 1600, 2560]      # developed photos
RAW_WIDTHS = [960, 1600]             # unprocessed comparison
COVER_WIDTHS = [960, 1600, 2560]
WEBP_OPTS = dict(quality=90, method=6)

# EXIF tags
EXIF_IFD = 0x8769
T_MODEL, T_EXPOSURE, T_FNUMBER, T_ISO, T_DATE, T_FOCAL = 272, 33434, 33437, 34855, 36867, 37386


def underscored(title: str) -> str:
    return "_" + title.replace(" ", "_")


# --------------------------------------------------------------------------- images

def needs_update(src: Path, dst: Path) -> bool:
    return not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime


def to_srgb(im, icc):
    """Convert any colour space (e.g. CMYK, Adobe RGB) to sRGB, the colour space browsers expect."""
    if icc:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        if "srgb" not in ImageCms.getProfileDescription(src).lower() or im.mode != "RGB":
            srgb = ImageCms.createProfile("sRGB")
            im = ImageCms.profileToProfile(im, src, srgb, outputMode="RGB",
                                           renderingIntent=ImageCms.Intent.PERCEPTUAL)
            icc = ImageCms.ImageCmsProfile(srgb).tobytes()
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im, icc


def make_versions(src: Path, dst_stem: Path, widths: list[int]) -> list[tuple[int, Path]]:
    """Resize src to each width (never upscaling). Returns [(width, path)]."""
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        exif = im.getexif()
        im = ImageOps.exif_transpose(im)
        if 274 in exif:
            exif[274] = 1  # already rotated above
        exif_bytes = exif.tobytes()
        im, icc = to_srgb(im, icc)

        targets = sorted({min(w, im.width) for w in widths})
        out = []
        for w in targets:
            dst = dst_stem.with_name(f"{dst_stem.name}-{w}.webp")
            if needs_update(src, dst):
                h = round(im.height * w / im.width)
                resized = im if w == im.width else im.resize((w, h), Image.LANCZOS)
                dst.parent.mkdir(parents=True, exist_ok=True)
                kwargs = dict(WEBP_OPTS, exif=exif_bytes)
                if icc:
                    kwargs["icc_profile"] = icc
                resized.save(dst, "WEBP", **kwargs)
            out.append((w, dst))
        return out


def fmt_exposure(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError, ZeroDivisionError):
        return ""
    if v <= 0:
        return ""
    if v < 0.5:
        return f"1/{round(1 / v)} s"
    return f"{v:g} s"


def read_exif(path: Path) -> dict:
    with Image.open(path) as im:
        exif = im.getexif()
        ifd = exif.get_ifd(EXIF_IFD)
        w, h = ImageOps.exif_transpose(im).size if exif.get(274, 1) in (5, 6, 7, 8) else im.size
        # average colour, used as placeholder while the photo loads
        small = im.copy()
        small.draft("RGB", (64, 64))
        r, g, b = small.convert("RGB").resize((1, 1), Image.BOX).getpixel((0, 0))

    def num(tag, fmt):
        v = ifd.get(tag)
        try:
            return fmt.format(float(v)) if v is not None else ""
        except (TypeError, ValueError, ZeroDivisionError):
            return ""

    date = str(ifd.get(T_DATE) or "")[:10].replace(":", "-")
    return {
        "w": w,
        "h": h,
        "iso": str(ifd.get(T_ISO) or ""),
        "exposure": fmt_exposure(ifd.get(T_EXPOSURE)),
        "aperture": num(T_FNUMBER, "f/{:g}"),
        "focal": num(T_FOCAL, "{:g} mm"),
        "camera": str(exif.get(T_MODEL) or "").strip(),
        "date": date,
        "color": f"#{r:02x}{g:02x}{b:02x}",
    }


def process_photo(job):
    album, src = job
    name = src.stem
    info = read_exif(src)
    info["name"] = name
    info["versions"] = [(w, p.relative_to(GALLERY).as_posix())
                        for w, p in make_versions(src, WEB / album / name, WIDTHS)]
    raw = RAWS / album / f"{name}_ori.jpg"
    if raw.exists():
        with Image.open(raw) as r:
            info["raw_w"], info["raw_h"] = ImageOps.exif_transpose(r).size
        info["raw"] = [(w, p.relative_to(GALLERY).as_posix())
                       for w, p in make_versions(raw, WEB / album / f"{name}-raw", RAW_WIDTHS)]
    return album, info


def process_cover():
    src = COVER / "cover.jpg"
    if src.exists():
        og = COVER / "cover-og.jpg"  # JPEG for social-media link previews
        if needs_update(src, og):
            with Image.open(src) as im:
                im, icc = to_srgb(ImageOps.exif_transpose(im), im.info.get("icc_profile"))
                im.thumbnail((1200, 1200), Image.LANCZOS)
                im.save(og, "JPEG", quality=88, progressive=True, optimize=True, icc_profile=icc)
        return [(w, p.relative_to(ROOT).as_posix()) for w, p in make_versions(src, COVER / "cover", COVER_WIDTHS)]
    return []


# --------------------------------------------------------------------------- html

ICONS = {
    "prev": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 4 7 12l8 8"/></svg>',
    "next": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 4 8 8-8 8"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"/></svg>',
}

GRID_SIZES = "(max-width: 599px) 100vw, (max-width: 1099px) 50vw, (min-width: 1800px) calc((100vw - 120px) / 4), calc((100vw - 120px) / 3)"


def srcset(versions):
    return ", ".join(f"{p} {w}w" for w, p in versions)


def nav_html(current: str) -> str:
    items = []
    for slug, title, icon in ALBUMS:
        cur = ' aria-current="page"' if slug == current else ""
        items.append(
            f'<li><a href="{slug}.html"{cur} title="{html.escape(title)}">'
            f'<img src="../icons/{icon}" alt="" width="50" height="50">'
            f'<span class="nav-label">{html.escape(underscored(title))}</span></a></li>'
        )
    return "\n        ".join(items)


def tile_html(album: str, title: str, i: int, n: int, p: dict) -> str:
    e = html.escape
    versions = p["versions"]
    default = next((pth for w, pth in versions if w >= 960), versions[-1][1])
    eager = i < 3
    attrs = {
        "href": f"images/fulls/{album}/{p['name']}.jpg",
        "id": p["name"],
        "data-srcset": srcset(versions),
        "data-w": p["w"],
        "data-h": p["h"],
        "data-iso": p["iso"],
        "data-exposure": p["exposure"],
        "data-aperture": p["aperture"],
        "data-focal": p["focal"],
        "data-camera": p["camera"],
        "data-date": p["date"],
    }
    if p.get("raw"):
        attrs.update({"data-raw-srcset": srcset(p["raw"]), "data-raw-w": p["raw_w"], "data-raw-h": p["raw_h"]})
    a = " ".join(f'{k}="{e(str(v))}"' for k, v in attrs.items() if v != "")

    rows = [("ISO", p["iso"]), ("Exposure", p["exposure"]), ("Aperture", p["aperture"]), ("Focal length", p["focal"])]
    info = "".join(f"<dt>{k}</dt><dd>{e(v)}</dd>" for k, v in rows if v)
    loading = 'fetchpriority="high"' if i == 0 else ('loading="eager"' if eager else 'loading="lazy"')

    return (
        f'<li class="tile" style="--ph:{p["color"]}">'
        f'<a {a}>'
        f'<img src="{default}" srcset="{srcset(versions)}" sizes="{GRID_SIZES}" '
        f'width="{p["w"]}" height="{p["h"]}" alt="{e(title)}, photograph {i + 1} of {n}" '
        f'{loading} decoding="async">'
        f'<dl class="tile-info">{info}</dl>'
        f"</a></li>"
    )


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title} · SerGo Photography</title>
  <meta name="description" content="{title} — a photo series by SerGo Photography ({n} photographs).">
  <meta name="theme-color" content="#000000">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} · SerGo Photography">
  <meta property="og:image" content="{og_image}">
  <link rel="icon" href="../icons/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="../assets/fonts/typewriter-webfont.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../assets/css/gallery.css">
  <script>document.documentElement.classList.add("js")</script>
  <script src="../assets/js/gallery.js" defer></script>
</head>
<body>
  <a class="skip" href="#photos">Skip to photos</a>
  <header class="site-nav">
    <a class="home" href="../index.html">back<br>home</a>
    <nav aria-label="Series">
      <ul>
        {nav}
      </ul>
    </nav>
  </header>

  <main id="photos">
    <h1 class="album-title">{title_u} <span class="count">{n}&nbsp;photos</span></h1>
    <ul class="grid">
      {tiles}
    </ul>
  </main>

  <dialog class="lb" aria-label="Photo viewer">
    <figure class="lb-stage">
      <img class="lb-img" alt="">
    </figure>
    <button class="lb-btn lb-prev" type="button" aria-label="Previous photo">{prev}</button>
    <button class="lb-btn lb-next" type="button" aria-label="Next photo">{next}</button>
    <button class="lb-btn lb-close" type="button" aria-label="Close">{close}</button>
    <div class="lb-bar">
      <span class="lb-count" aria-live="polite"></span>
      <span class="lb-exif"></span>
      <span class="lb-actions">
        <button class="lb-raw" type="button" hidden aria-pressed="false">raw_view</button>
        <a class="lb-full" target="_blank" rel="noopener">full_resolution&nbsp;&#8599;</a>
      </span>
    </div>
  </dialog>
</body>
</html>
"""


def write_gallery(album: str, title: str, photos: list[dict]):
    photos.sort(key=lambda p: p["name"])
    n = len(photos)
    first = photos[0]["versions"]
    og = next((pth for w, pth in first if w >= 1600), first[-1][1])
    page = PAGE.format(
        title=html.escape(title),
        title_u=html.escape(underscored(title)),
        n=n,
        og_image=SITE_URL + "newgallery/" + og,
        nav=nav_html(album),
        tiles="\n      ".join(tile_html(album, title, i, n, p) for i, p in enumerate(photos)),
        **ICONS,
    )
    (GALLERY / f"{album}.html").write_text(page, encoding="utf-8")


# --------------------------------------------------------------------------- main

def main():
    jobs = []
    for album, _, _ in ALBUMS:
        folder = FULLS / album
        if not folder.is_dir():
            print(f"! missing folder {folder}")
            continue
        jobs += [(album, f) for f in sorted(folder.iterdir()) if f.suffix.lower() in (".jpg", ".jpeg")]

    print(f"Processing {len(jobs)} photos…")
    results: dict[str, list] = {a: [] for a, _, _ in ALBUMS}
    workers = max(1, (os.cpu_count() or 2) - 1)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for k, (album, info) in enumerate(pool.map(process_photo, jobs, chunksize=1), 1):
            results[album].append(info)
            print(f"  [{k}/{len(jobs)}] {album}/{info['name']}")

    # remove web versions of photos that no longer exist
    keep = {p for infos in results.values() for i in infos for _, p in i["versions"] + i.get("raw", [])}
    for f in WEB.rglob("*.webp"):
        if f.relative_to(GALLERY).as_posix() not in keep:
            f.unlink()

    for album, title, _ in ALBUMS:
        if results[album]:
            write_gallery(album, title, results[album])
            print(f"Wrote newgallery/{album}.html ({len(results[album])} photos)")

    cover = process_cover()
    if cover:
        print("Cover versions:", ", ".join(p for _, p in cover))
    print("Done.")


if __name__ == "__main__":
    main()

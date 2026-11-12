"""Younis Travel — site generator (single entry point).

Pipeline stages live in the gen/ package and run in order:
base -> layout -> seo -> countries -> publish_fixes -> agents -> booking -> oauth.
Each stage layers its features onto the same output tree (site_v3/).

Run:  python3 generator/build_site.py
"""
import os, sys, glob, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _seed_images():
    # Master destination photos live in assets/images/. The pipeline derives
    # WebP copies and resized variants from the JPGs inside the output tree,
    # so seed any missing JPG before the stages run (no-op on existing trees).
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, 'assets', 'images')
    dst = os.path.join(here, '..', 'site_v3', 'images')
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(src, '*.jpg')):
        t = os.path.join(dst, os.path.basename(f))
        if not os.path.exists(t):
            shutil.copy(f, t)

_seed_images()
from gen.oauth import main

if __name__ == '__main__':
    main()

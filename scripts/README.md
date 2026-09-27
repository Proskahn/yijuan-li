## Updating the illustration gallery

Rename, reorder, add, or remove the original files in `illustration/`. The leading
number sets the order and the rest of the filename becomes the title. Keep a
space between the number and title, for example `07 Dar Cat.png`.
To move an existing work, change its leading number and keep its title attached
to the same image.

Netlify regenerates `_data/illustrations.json` and the optimized images before
building the website. Do not edit the JSON separately: its captions and image
paths must refer to the same source file.

To update and preview locally:

```sh
python3 -m pip install -r requirements.txt
python3 scripts/prepare_illustrations.py
bundle exec jekyll serve
```

The preparation command preserves the originals and removes obsolete generated
image sizes. Run it again after renaming files while a local preview is running.

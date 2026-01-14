# Dashboard_export_agent.py  (replace existing)
import os
import tempfile
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = 'outputs'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def render_dashboard_image(saved_charts) -> str:
    """
    Generate a 2x2 dashboard image from saved charts.
    Accepts:
     - list of dicts with 'saved_path' and 'explanation'
     - or list of strings (paths)
    Returns: path to saved PNG image
    """
    if not saved_charts:
        raise ValueError("No saved charts provided to create dashboard.")

    # normalize to list of tuples (PIL.Image, explanation)
    imgs = []
    for item in saved_charts:
        if isinstance(item, dict):
            path = item.get("saved_path") or item.get("path")
            expl = item.get("explanation", "")
        else:
            path = item
            expl = ""
        if path and os.path.exists(path):
            try:
                img = Image.open(path).convert("RGB")
                imgs.append((img, expl))
            except Exception:
                continue

    if not imgs:
        raise ValueError("No valid chart images found.")

    # Use up to 4
    imgs = imgs[:4]
    # compute grid cell size (use max width/height among charts)
    widths, heights = zip(*[(im.size[0], im.size[1]) for im, _ in imgs])
    cell_w = max(widths)
    cell_h = max(heights)
    text_space = 40
    total_w = cell_w * 2
    total_h = (cell_h + text_space) * 2

    dashboard = Image.new("RGB", (total_w, total_h), color="white")
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font = ImageFont.load_default()
    draw = ImageDraw.Draw(dashboard)
    positions = [(0,0), (cell_w,0), (0,cell_h+text_space), (cell_w,cell_h+text_space)]

    for (img, expl), (x,y) in zip(imgs, positions):
        # resize preserving aspect ratio to fit cell
        ratio = min(cell_w / img.width, cell_h / img.height)
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        resized = img.resize((new_w, new_h))
        dashboard.paste(resized, (x + (cell_w-new_w)//2, y + (text_space//2)))
        # write explanation below
        draw.text((x + 8, y + (text_space//2) + new_h + 4), expl[:160], fill="black", font=font)

    fd, path = tempfile.mkstemp(suffix=".png", dir=OUTPUT_DIR)
    os.close(fd)
    dashboard.save(path)
    # also save as standardized dashboard.png for PDF exporter
    try:
        dashboard.save(os.path.join(OUTPUT_DIR, "dashboard.png"))
    except Exception:
        pass
    return path

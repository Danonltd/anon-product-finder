"""Sync public catalog and precompute lightweight visual descriptors.
Requires: google-api-python-client google-auth Pillow
"""
import datetime
import io
import json
import os
import pathlib
import re
from PIL import Image, ImageOps
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

ROOT = pathlib.Path(__file__).resolve().parent
CAT = ROOT / 'catalog'
IMAGES = CAT / 'images'
FOLDER_ID = os.environ['DRIVE_FOLDER_ID']
creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/drive.readonly'])
api = build('drive', 'v3', credentials=creds, cache_discovery=False)
IMAGES.mkdir(parents=True, exist_ok=True)


def descriptor(path):
    """Same 16x16 foreground-weighted RGB representation as browser code."""
    with Image.open(path) as source:
        im = ImageOps.exif_transpose(source).convert('RGBA')
        im.thumbnail((256, 256))
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        rgb = bg.convert('RGB')
        # Crop broad near-white margins only; retain small padding around the item.
        pix = rgb.load()
        w, h = rgb.size
        coords = [(x, y) for y in range(h) for x in range(w)
                  if max(pix[x, y]) - min(pix[x, y]) > 22 or min(pix[x, y]) < 195]
        if coords:
            x0 = min(x for x, _ in coords); x1 = max(x for x, _ in coords)
            y0 = min(y for _, y in coords); y1 = max(y for _, y in coords)
            if (x1-x0+1)*(y1-y0+1) > w*h*0.015:
                pad = int(max(x1-x0, y1-y0)*0.09)
                rgb = rgb.crop((max(0,x0-pad),max(0,y0-pad),min(w,x1+pad+1),min(h,y1+pad+1)))
        thumb = ImageOps.contain(rgb, (16, 16), method=Image.Resampling.BILINEAR)
        canvas = Image.new('RGB', (16, 16), (255, 255, 255))
        canvas.paste(thumb, ((16-thumb.width)//2, (16-thumb.height)//2))
        return [round(c/255, 3) for pixel in canvas.getdata() for c in pixel]

entries = []
page = None
while True:
    response = api.files().list(
        q=f"'{FOLDER_ID}' in parents and trashed = false",
        fields='nextPageToken,files(id,name,mimeType,size)',
        pageSize=1000, pageToken=page).execute()
    for f in response.get('files', []):
        if f.get('mimeType') not in ('image/jpeg', 'image/png', 'image/webp'):
            continue
        sku = pathlib.Path(f['name']).stem
        if not re.fullmatch(r'[A-Za-z0-9_-]{3,80}', sku):
            continue
        ext = pathlib.Path(f['name']).suffix.lower()
        target = IMAGES / (f['id'] + ext)
        if not target.exists():
            stream = io.BytesIO()
            downloader = MediaIoBaseDownload(stream, api.files().get_media(fileId=f['id']))
            done = False
            while not done:
                _, done = downloader.next_chunk()
            target.write_bytes(stream.getvalue())
        try:
            features = descriptor(target)
        except Exception as exc:
            print(f"Skipping unreadable image {f['name']}: {exc}")
            continue
        entries.append({'sku': sku, 'path': 'catalog/images/' + target.name, 'features': features})
    page = response.get('nextPageToken')
    if not page:
        break

# Only prune after successfully listing the full folder.
keep = {x['path'].split('/')[-1] for x in entries}
for p in IMAGES.iterdir():
    if p.is_file() and p.name not in keep:
        p.unlink()
entries.sort(key=lambda x: x['sku'])
(CAT / 'manifest.json').write_text(json.dumps({
    'version': 2,
    'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
    'images': entries
}, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(f'Synced {len(entries)} images with precomputed descriptors')

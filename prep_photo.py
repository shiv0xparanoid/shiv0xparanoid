"""Prep a portrait for ASCII conversion.
Usage: python scripts/prep_photo.py photo.jpg [x0 y0 x1 y1]   (optional crop box)
Steps: crop -> grabCut background removal (offline, no rembg needed)
       -> CLAHE local contrast -> composite on pure black (black = blank ASCII)
"""
import sys, cv2, numpy as np

src = sys.argv[1]
img = cv2.imread(src)
h, w = img.shape[:2]
if len(sys.argv) == 6:
    x0, y0, x1, y1 = map(int, sys.argv[2:6])
else:                                   # default: centred head-and-shoulders crop
    x0, y0, x1, y1 = int(w*.07), int(h*.14), int(w*.86), int(h*.72)
img = img[y0:y1, x0:x1]
h, w = img.shape[:2]

# --- background removal with grabCut -------------------------------------
mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
mask[int(h*.04):, int(w*.06):int(w*.94)] = cv2.GC_PR_FGD
mask[int(h*.25):int(h*.9), int(w*.22):int(w*.78)] = cv2.GC_FGD   # face = sure fg
mask[:int(h*.02), :] = cv2.GC_BGD
bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(img, mask, None, bgd, fgd, 8, cv2.GC_INIT_WITH_MASK)
fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
# fill interior holes (e.g. the cap patch)
ff = fg.copy(); m2 = np.zeros((h+2, w+2), np.uint8)
cv2.floodFill(ff, m2, (0, 0), 255)
fg = fg | cv2.bitwise_not(ff)
fg = cv2.GaussianBlur(fg, (9, 9), 0)

# --- contrast -------------------------------------------------------------
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
m = (fg / 255.0).astype(np.float32)
# flatten uneven lighting: divide by a heavily blurred, mask-weighted copy
illum = cv2.GaussianBlur(gray * m, (0, 0), 45) / np.maximum(cv2.GaussianBlur(m, (0, 0), 45), 1e-3)
flat = np.clip(gray / np.maximum(illum, 1) * 120, 0, 255).astype(np.uint8)
flat = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(flat)
# unsharp mask so eyes / brows / nose / moustache pop
blur = cv2.GaussianBlur(flat, (0, 0), 4)
gray = np.clip(cv2.addWeighted(flat, 1.9, blur, -0.9, 0), 0, 255).astype(np.uint8)
fade = np.clip((0.97 - np.arange(h) / h) / 0.17, 0, 1)[:, None]   # shoulders fade out
out = (gray * (fg / 255.0) * fade).astype(np.uint8)
cv2.imwrite("source-prepped.png", out)
cv2.imwrite("source-mask-debug.png", fg)
print("wrote source-prepped.png", out.shape)

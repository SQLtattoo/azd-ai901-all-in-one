"""
make_assets.py — generate offline sample files for Demos 5 and 6.

Produces (pure standard library, no Pillow needed):
  * demos/05-computer-vision/assets/sample.png   — a simple shapes scene for the
    multimodal vision demo.
  * demos/06-information-extraction/assets/sample-invoice.pdf — a small, valid
    single-page invoice PDF for the Content Understanding demo.

Run:
    python make_assets.py
"""
import os
import struct
import zlib

ROOT = os.path.dirname(__file__)
VISION_ASSETS = os.path.join(ROOT, "demos", "05-computer-vision", "assets")
CU_ASSETS = os.path.join(ROOT, "demos", "06-information-extraction", "assets")


# ---------------------------------------------------------------- PNG (vision)
def _png_chunk(tag, data):
    payload = tag + data
    return struct.pack(">I", len(data)) + payload + struct.pack(
        ">I", zlib.crc32(payload) & 0xFFFFFFFF
    )


def write_png(path, width, height, rgb):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter type 0 (None) per scanline
        raw.extend(rgb[y * stride:(y + 1) * stride])
    with open(path, "wb") as handle:
        handle.write(b"\x89PNG\r\n\x1a\n")
        handle.write(_png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
        handle.write(_png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        handle.write(_png_chunk(b"IEND", b""))


def make_vision_png():
    width, height = 480, 300
    buf = bytearray([255]) * (width * height * 3)  # white background

    def put(x, y, color):
        if 0 <= x < width and 0 <= y < height:
            i = (y * width + x) * 3
            buf[i:i + 3] = bytes(color)

    # Red square (left)
    for y in range(100, 200):
        for x in range(40, 140):
            put(x, y, (220, 50, 50))

    # Blue circle (center)
    cx, cy, r = 240, 150, 55
    for y in range(cy - r, cy + r):
        for x in range(cx - r, cx + r):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(x, y, (50, 90, 220))

    # Green triangle (right): (330,200),(430,200),(380,90)
    ax, ay, bx, by, cx2, cy2 = 330, 200, 430, 200, 380, 90

    def sign(px, py, qx, qy, rx, ry):
        return (px - rx) * (qy - ry) - (qx - rx) * (py - ry)

    for y in range(90, 201):
        for x in range(330, 431):
            d1 = sign(x, y, ax, ay, bx, by)
            d2 = sign(x, y, bx, by, cx2, cy2)
            d3 = sign(x, y, cx2, cy2, ax, ay)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            if not (has_neg and has_pos):
                put(x, y, (60, 170, 80))

    os.makedirs(VISION_ASSETS, exist_ok=True)
    out = os.path.join(VISION_ASSETS, "sample.png")
    write_png(out, width, height, buf)
    print(f"wrote {out}")


# ------------------------------------------------------------- PDF (invoice)
def _escape_pdf(text):
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def make_invoice_pdf():
    lines = [
        "Contoso Ltd.",
        "123 Cloud Way, Redmond, WA 98052",
        "",
        "INVOICE",
        "",
        "Invoice Number: INV-2026-0742",
        "Invoice Date: 2026-07-15",
        "Bill To: Northwind Traders",
        "",
        "Description                 Qty   Unit Price     Amount",
        "Azure AI Foundry setup       1     1200.00      1200.00",
        "Content Understanding pack   3      150.00       450.00",
        "Speech add-on                2      100.00       200.00",
        "",
        "Subtotal:  1850.00",
        "Tax (10%):  185.00",
        "Total:     2035.00",
    ]

    content = "BT /F1 11 Tf 72 720 Td 14 TL\n"
    for line in lines:
        content += f"({_escape_pdf(line)}) Tj T*\n"
    content += "ET"
    content_bytes = content.encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
        b"<< /Length "
        + str(len(content_bytes)).encode()
        + b" >>\nstream\n"
        + content_bytes
        + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += (
        b"trailer\n<< /Size "
        + str(len(objects) + 1).encode()
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_pos).encode()
        + b"\n%%EOF"
    )

    os.makedirs(CU_ASSETS, exist_ok=True)
    out = os.path.join(CU_ASSETS, "sample-invoice.pdf")
    with open(out, "wb") as handle:
        handle.write(pdf)
    print(f"wrote {out}")


if __name__ == "__main__":
    make_vision_png()
    make_invoice_pdf()

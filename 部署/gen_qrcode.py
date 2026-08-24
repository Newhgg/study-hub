#!/usr/bin/env python3
"""生成双库二维码
部署完成后，替换下面的URL为实际域名，然后运行: python gen_qrcode.py
"""
import qrcode
from qrcode.constants import ERROR_CORRECT_H
import os

# ===== 部署完成后替换为实际URL =====
BASE_URL = "https://替换为实际域名"

LINKS = {
    "政策库二维码": f"{BASE_URL}/政策库/index.html",
    "影音库二维码": f"{BASE_URL}/影音库/index.html",
    "双库总入口二维码": f"{BASE_URL}/",
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "二维码")

def gen_qr(name, url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#6366f1", back_color="white")
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    img.save(path)
    print(f"✓ 生成: {name}.png  ->  {url}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if "替换为实际域名" in BASE_URL:
        print("⚠️  请先编辑本文件，将 BASE_URL 替换为部署后的实际域名！")
        print("   当前值:", BASE_URL)
        exit(1)
    for name, url in LINKS.items():
        gen_qr(name, url)
    print(f"\n完成！二维码已保存到: {OUTPUT_DIR}")

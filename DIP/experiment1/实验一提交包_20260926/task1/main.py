"""任务一：从一对原始 DICOM 读取 HU，统一肺窗并保存纯灰度图。"""
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from task2_1.denoise_dicom import (
    FDCT_PATH, LDCT_PATH, read_dicom_hu, window_to_uint8, save_grayscale,
)
from plot_common import image_plate


def main():
    output = Path(__file__).resolve().parent / "output"
    output.mkdir(parents=True, exist_ok=True)
    panels = []
    for name, path in (("LDCT", LDCT_PATH), ("FDCT", FDCT_PATH)):
        hu, _ = read_dicom_hu(path)
        assert hu.shape == (512, 512) and np.isfinite(hu).all()
        gray = window_to_uint8(hu)
        save_grayscale(output / f"{name.lower()}.png", gray)
        panels.append((name, gray))
    image_plate(panels, output / "paired_ct.png",
                "L067 paired CT | lung window [-1350, 150] HU", width=7, height=3.8)
    print("任务一：原始 DICOM 读取和统一预处理完成。")


if __name__ == "__main__":
    main()

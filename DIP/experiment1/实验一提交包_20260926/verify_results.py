"""从已保存的纯像素图独立复算表格，并核查数据来源、尺寸与成图。"""
from pathlib import Path
import ast
import csv
import hashlib
import json
import math
import cv2
import numpy as np
from PIL import Image
import SimpleITK as sitk
from skimage.metrics import structural_similarity

ROOT = Path(__file__).resolve().parent


def read_gray(path):
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    assert image is not None and image.ndim == 2 and image.dtype == np.uint8, path
    return image


def main():
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    manifest = json.loads((ROOT / "task2_1/results/reproducibility.json").read_text())
    for key, filename in (("fdct", "fdct_ground_truth.png"), ("ldct", "ldct_input.png")):
        path = ROOT / manifest["inputs"][key]["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["inputs"][key]["sha256"]
        array = np.squeeze(sitk.GetArrayFromImage(sitk.ReadImage(str(path)))).astype(np.float32)
        expected = np.rint((np.clip(array, -1350, 150) + 1350) / 1500 * 255).astype(np.uint8)
        assert np.array_equal(expected, read_gray(ROOT / "task2_1/images" / filename))
    gt = read_gray(ROOT / "task2_1/images/fdct_ground_truth.png")
    candidates = {
        "LDCT": "task2_1/images/ldct_input.png", "Mean": "task2_1/images/mean.png",
        "Gaussian": "task2_1/images/gaussian.png", "Adaptive Median": "task2_1/images/adaptive_median.png",
        "NLM": "task2_1/images/nlm.png", "Wavelet": "task2_1/images/wavelet.png",
        "NLM + Nearest": "task3/output/nearest_image.png",
        "NLM + Bilinear": "task3/output/bilinear_image.png",
        "NLM + Bicubic": "task3/output/bicubic_image.png",
    }

    def check(row, image, ref):
        assert image.shape == ref.shape
        mse = np.mean((image.astype(np.float64) - ref.astype(np.float64)) ** 2)
        psnr = 10 * math.log10(255 ** 2 / mse)
        ssim = structural_similarity(ref, image, data_range=255)
        assert abs(psnr - float(row["PSNR_dB"])) < 0.000051, row
        assert abs(ssim - float(row["SSIM"])) < 0.0000051, row

    with (ROOT / "task4/results/metrics.csv").open(encoding="utf-8-sig") as f:
        rows = [r for r in csv.DictReader(f) if r["Category"] != "Reference"]
    assert len(rows) == 9 and {r["Method"] for r in rows} == set(candidates)
    for row in rows:
        check(row, read_gray(ROOT / candidates[row["Method"]]), gt)
    with (ROOT / "task5/results/order_metrics.csv").open(encoding="utf-8-sig") as f:
        order_rows = list(csv.DictReader(f))
    assert len(order_rows) == 4
    for row in order_rows:
        ref = gt if row["Reference"] == "FDCT_512" else cv2.resize(gt, (2048, 2048), interpolation=cv2.INTER_CUBIC)
        path = ROOT / "task5/results" / f"{row['Reference']}_{row['Method']}.png"
        check(row, read_gray(path), ref)
    for name in ("nearest", "bilinear", "bicubic"):
        assert read_gray(ROOT / f"task3/direct4x/{name}_2048.png").shape == (2048, 2048)
    figures = sorted((ROOT / "提交材料/对比图").glob("*.png"))
    assert len(figures) == 7
    for path in figures:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            assert min(image.info["dpi"]) > 299
        assert path.with_suffix(".svg").is_file()
    report = {
        "status": "PASS", "source_dicom_count": 2,
        "fdct_metric_rows_verified": len(rows), "order_metric_rows_verified": len(order_rows),
        "direct4x_images": 3, "delivery_figure_pairs": len(figures),
        "checks": ["Python syntax", "input hashes", "DICOM/PNG exact pixels", "saved-image metrics", "figure dimensions and DPI"],
    }
    (ROOT / "verification/results_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

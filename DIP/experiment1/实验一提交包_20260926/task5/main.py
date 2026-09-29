"""任务五：固定 NLM 参数，比较去噪与双三次插值的处理顺序。

主评价：同一个 LDCT 128×128 输入，输出512，与原始FDCT比较。
补充评价：LDCT 512×512 输入，输出2048，与插值FDCT比较。
后一参考是人工插值结果，不能称为真实2048高分辨率真值。
"""
from pathlib import Path
import csv
import sys
import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from plot_common import image_plate


def nlm(image):
    """h=4，模板7×7，搜索21×21；两条路径使用相同像素参数。"""
    return cv2.fastNlMeansDenoising(image, None, 4, 7, 21)


def upscale(image):
    return cv2.resize(image, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)


def main():
    output = Path(__file__).resolve().parent / "results"
    output.mkdir(parents=True, exist_ok=True)
    images = [cv2.imread(str(ROOT / "task2_1/images" / name), 0)
              for name in ("ldct_input.png", "fdct_ground_truth.png")]
    if any(im is None or im.shape != (512, 512) for im in images):
        raise ValueError("任务二的 LDCT/FDCT 纯灰度图缺失或尺寸错误。")
    ldct, fdct = images
    low = cv2.resize(ldct, (128, 128), interpolation=cv2.INTER_AREA)
    experiments = [
        ("FDCT_512", low, fdct),
        ("Interpolated_FDCT_2048", ldct, upscale(fdct)),
    ]
    rows = []
    for reference_name, source, reference in experiments:
        results = {
            "A_denoise_then_bicubic": upscale(nlm(source)),
            "B_bicubic_then_denoise": nlm(upscale(source)),
        }
        panels = [("FDCT reference" if reference.shape[0] == 512 else "Interpolated FDCT reference", reference)]
        for method, result in results.items():
            assert result.shape == reference.shape and np.isfinite(result).all()
            p = float(peak_signal_noise_ratio(reference, result, data_range=255))
            s = float(structural_similarity(reference, result, data_range=255))
            rows.append({"Reference": reference_name, "Method": method,
                         "PSNR_dB": p, "SSIM": s})
            assert cv2.imwrite(str(output / f"{reference_name}_{method}.png"), result)
            label = "A: denoise then bicubic" if method.startswith("A_") else "B: bicubic then denoise"
            panels.append((f"{label}\nPSNR {p:.3f} dB | SSIM {s:.5f}", result))
        image_plate(panels, output / f"comparison_{reference_name}.png",
                    f"Order comparison | reference: {reference_name} | fixed h=4",
                    width=11, height=4)
    with (output / "order_metrics.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print("任务五顺序实验完成：")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()

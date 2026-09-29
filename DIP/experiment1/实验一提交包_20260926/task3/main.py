"""任务三：三种直接 4 倍插值放大，并保留 128→512 的模拟评价分支。"""
from pathlib import Path
import sys
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from plot_common import image_plate

TASK = Path(__file__).resolve().parent
METHODS = {"nearest": cv2.INTER_NEAREST, "bilinear": cv2.INTER_LINEAR,
           "bicubic": cv2.INTER_CUBIC}


def main():
    image = cv2.imread(str(ROOT / "task2_1/images/nlm.png"), cv2.IMREAD_GRAYSCALE)
    if image is None or image.shape != (512, 512):
        raise ValueError("请先运行任务二，生成 512×512 的 NLM 结果。")
    output = TASK / "output"
    direct = TASK / "direct4x"
    output.mkdir(parents=True, exist_ok=True)
    direct.mkdir(parents=True, exist_ok=True)
    # 模拟评价：统一输入，恢复到 FDCT 的原始大小以便逐像素评价。
    low = cv2.resize(image, (128, 128), interpolation=cv2.INTER_AREA)
    assert cv2.imwrite(str(output / "low_resolution_128.png"), low)
    direct_panels, detail_panels = [], []
    for name, method in METHODS.items():
        reconstruction = cv2.resize(low, (512, 512), interpolation=method)
        enlargement = cv2.resize(image, (2048, 2048), interpolation=method)
        assert reconstruction.dtype == np.uint8
        assert cv2.imwrite(str(output / f"{name}_image.png"), reconstruction)
        assert cv2.imwrite(str(direct / f"{name}_2048.png"), enlargement)
        direct_panels.append((name.capitalize(), enlargement))
        # 相同原始坐标区域 x=[80,208), y=[160,288)，直接放大后坐标乘4。
        detail_panels.append((name.capitalize(), enlargement[640:1152, 320:832]))
    image_plate(direct_panels, direct / "comparison_direct4x.png",
                "Direct 4x enlargement | NLM 512 to 2048", width=11, height=4)
    image_plate(detail_panels, direct / "comparison_direct4x_detail.png",
                "Same local region | direct 4x enlargement", width=11, height=4)
    print("任务三：三种 2048×2048 放大图及 512×512 模拟重建图完成。")


if __name__ == "__main__":
    main()

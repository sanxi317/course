"""把真实运行产生的图、表和分析汇集到提交材料目录。"""
from pathlib import Path
import csv
import json
import shutil
import importlib.metadata

ROOT = Path(__file__).resolve().parent


def load_rows(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    delivery = ROOT / "提交材料"
    figures = delivery / "对比图"
    figures.mkdir(parents=True, exist_ok=True)
    metrics = load_rows(ROOT / "task4/results/metrics.csv")
    orders = load_rows(ROOT / "task5/results/order_metrics.csv")
    measurements = {r["Method"]: r for r in metrics if r["Category"] != "Reference"}
    order_values = {(r["Reference"], r["Method"]): r for r in orders}
    for suffix in ("csv", "txt"):
        shutil.copy2(ROOT / f"task4/results/metrics.{suffix}",
                     delivery / f"PSNR_SSIM汇总表_FDCT512.{suffix}")
    shutil.copy2(ROOT / "task5/results/order_metrics.csv", delivery / "处理顺序指标_分参考图.csv")
    # 这些图以同一灰度窗展示，带标题的画布不参与数值评价。
    names = {
        "task4/results/comparison_denoising": "01_五种去噪对比",
        "task3/direct4x/comparison_direct4x": "02_三种插值直接放大4倍",
        "task3/direct4x/comparison_direct4x_detail": "03_三种插值边缘局部对比",
        "task4/results/comparison_sr": "04_模拟重建与FDCT对比",
        "task5/results/comparison_FDCT_512": "05_处理顺序_原始FDCT评价",
        "task5/results/comparison_Interpolated_FDCT_2048": "06_处理顺序_插值FDCT参考",
        "task4/results/comparison_all": "07_全部方法总览",
    }
    for source, target in names.items():
        for suffix in ("png", "svg"):
            shutil.copy2(ROOT / f"{source}.{suffix}", figures / f"{target}.{suffix}")

    def score(method):
        row = measurements[method]
        return f"PSNR={float(row['PSNR_dB']):.4f} dB，SSIM={float(row['SSIM']):.5f}"

    order_text = []
    for reference in ("FDCT_512", "Interpolated_FDCT_2048"):
        a = order_values[(reference, "A_denoise_then_bicubic")]
        b = order_values[(reference, "B_bicubic_then_denoise")]
        p_a, p_b = float(a["PSNR_dB"]), float(b["PSNR_dB"])
        s_a, s_b = float(a["SSIM"]), float(b["SSIM"])
        conclusion = ("A 的两项指标均较高。" if p_a > p_b and s_a > s_b else
                      "B 的两项指标均较高。" if p_b > p_a and s_b > s_a else
                      "两项指标未给出一致排序，不能单凭一个指标判定全面胜出。")
        order_text.extend([
            f"参考：{reference}",
            f"A 先NLM后双三次：PSNR={p_a:.4f} dB，SSIM={s_a:.5f}",
            f"B 先双三次后NLM：PSNR={p_b:.4f} dB，SSIM={s_b:.5f}",
            conclusion, "",
        ])
    best_denoise = max((r for r in metrics if r["Category"] == "Denoising"),
                       key=lambda r: (float(r["SSIM"]), float(r["PSNR_dB"])))
    best_sr = max((r for r in metrics if r["Category"] == "Super Resolution"),
                  key=lambda r: (float(r["SSIM"]), float(r["PSNR_dB"])))
    report = f'''低剂量 CT 图像去噪与传统插值放大：结果对比分析

一、实验数据与统一处理
使用 AAPM 2016 Mayo 数据中 L067 的第1张配对切片，512×512，层厚3 mm，重建核B30f。
原始输入为包内 full_3mm 与 quarter_3mm 目录中的两张 DICOM/IMA。
SimpleITK 读取后得到 HU，统一截断为[-1350,150] HU，再四舍五入映射到 uint8 的0～255。
去噪及指标均在纯像素数组上进行；比较图中的标题、坐标和画布不进入指标计算。
FDCT 作为本课程参考图，仍可能含有噪声，并非理想无噪声真值。

二、任务二：五种去噪方法
比较均值、高斯、自适应中值、非局部均值NLM和小波软阈值方法。
共搜索30组候选参数，按 SSIM 优先、PSNR 同分决胜选择各方法参数。
原始LDCT：{score('LDCT')}。
NLM：{score('NLM')}。
本切片最优去噪方法为 {best_denoise['Method']}。
均值和高斯平滑可以提高SSIM，但本次PSNR低于原始LDCT，说明平滑带来了像素误差与细节损失的权衡。
完整五种方法数值见同目录的 PSNR_SSIM汇总表_FDCT512.txt。

三、任务三：三种插值的边缘重建效果
题目要求的直接放大：NLM 512×512 → 最近邻/双线性/双三次 → 2048×2048。
三张纯2048图在 task3/direct4x；主对比图为02，统一局部边缘图为03。
最近邻直接复制像素，曲线和斜向边缘出现阶梯状锯齿与4×4块状外观。
双线性利用2×2邻域加权，使轮廓较连续，但细小结构边缘偏软。
双三次利用4×4邻域估计，通常在连续性和清晰度之间取得较好平衡；强边缘可能有过冲，不能把它解释为真实新增细节。

四、任务四：以原始FDCT统一评价
本实验没有真实2048×2048 FDCT，因此额外构造模拟重建分支：
NLM 512×512 → INTER_AREA降采样到128×128 → 三种插值恢复512×512。
此分支三张结果才与原始512×512 FDCT逐像素比较，不能把2048图直接拿来与512图计算指标。
NLM＋最近邻（模拟重建）：{score('NLM + Nearest')}。
NLM＋双线性（模拟重建）：{score('NLM + Bilinear')}。
NLM＋双三次（模拟重建）：{score('NLM + Bicubic')}。
三种模拟重建中，{best_sr['Method']} 的SSIM最高。
模拟重建包含一次明显的信息丢失；它的指标低于仅NLM去噪，不能声称插值提高了原始采样率下的真实分辨率。
PSNR采用 data_range=255，单位dB；SSIM使用scikit-image默认7×7窗口及 data_range=255。
全部指标在整张图上计算，包括人体外背景；没有肺部掩膜，也没有结节区域单独评分。

五、任务五：处理顺序是否影响结果
主对照的两条路线从完全相同的 LDCT 128×128 输入出发：
A：原始LDCT512 → INTER_AREA128 → NLM → 双三次512。
B：原始LDCT512 → INTER_AREA128 → 双三次512 → NLM。
两者均与原始FDCT512比较。这一对照的起点与任务三不同：任务三先在512尺度去噪再降采样，不能把二者当作完全相同的路径。
另保留直接放大对照：A为LDCT512 → NLM → 双三次2048，B为LDCT512 → 双三次2048 → NLM。
直接放大对照仅使用双三次放大的FDCT2048作人工参考，结果不与原始FDCT512的指标直接排名。

{chr(10).join(order_text)}
两种尺度均固定NLM参数 h=4、模板7×7、搜索21×21。放大前后同样大小的像素窗口覆盖的物理区域不同；本实验说明固定参数下顺序会影响结果，不证明一种顺序对所有图像或参数都最优。

六、综合结论与局限
在这张配对切片和所搜索参数范围内，{best_denoise['Method']} 是五种去噪方法中的最优项。
在固定NLM结果的三种模拟插值重建中，{best_sr['Method']} 最优；它并未超过仅NLM去噪的原始尺寸保真度。
没有穷举五种去噪与三种插值的15种组合，因此不能声称找到所有组合的全局最优。
传统插值依靠已有像素估计新像素，无法恢复降采样丢失的真实高频信息。
本次仅有一个切片，且参数在同一FDCT参考上选择和评价，属于课堂示例的样本内比较，没有独立测试集和统计显著性结论。
本切片无经过确认的肺结节标注，局部图只用于边缘和纹理展示；题目中的“含肺结节切片”要求尚未由标注验证。
'''
    (delivery / "结果对比分析.txt").write_text(report, encoding="utf-8")
    (delivery / "处理顺序分析.txt").write_text("\n".join(order_text), encoding="utf-8")
    contract = {
        "sample_count": 1,
        "metric_rows_fdct": len(measurements), "metric_rows_order": len(orders),
        "figure_type": "paired grayscale image panels; fixed display 0..255",
        "figure_purpose": names,
        "direct_detail_roi_original_xyxy": [80, 160, 208, 288],
        "export": "PNG 300 DPI and SVG with embedded CT pixels and editable labels",
        "statistics": "single-slice values; no error bars or significance claims",
        "versions": {name: importlib.metadata.version(name) for name in
                     ["numpy", "opencv-python", "SimpleITK", "matplotlib", "PyWavelets", "scikit-image", "Pillow"]},
    }
    (ROOT / "verification/experiment_manifest.json").write_text(
        json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")
    print("提交材料汇总完成：代码、7组PNG/SVG图、FDCT指标表、顺序指标和中文分析。")


if __name__ == "__main__":
    main()

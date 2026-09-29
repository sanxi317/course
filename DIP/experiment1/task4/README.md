# Task4：定性与定量结果评价

## 任务说明

本模块以同一实验切片的全剂量 CT（FDCT）为 Ground Truth，统一评价原始低剂量 CT（LDCT）、五种传统去噪结果，以及 NLM 去噪后采用三种传统插值方法得到的 4 倍重建结果。评价包含并排可视化、PSNR 和 SSIM，不修改 `task1`、`task2`、`task3` 的任何文件。

## 实际输入

输入来自项目内已有结果：

- `task2/images/fdct_ground_truth.png`
- `task2/images/ldct_input.png`
- `task2/images/mean.png`
- `task2/images/gaussian.png`
- `task2/images/adaptive_median.png`
- `task2/images/nlm.png`
- `task2/images/wavelet.png`
- `task3/output/nearest_image.png`
- `task3/output/bilinear_image.png`
- `task3/output/bicubic_image.png`

程序逐一检查路径、二维 shape、dtype、最小值和最大值。评价输入必须是单通道 `uint8` 灰度图。若去噪结果与 FDCT 尺寸不同，程序会明确报错，不会为了消除异常而静默缩放。

## FDCT Ground Truth 与统一预处理

程序优先使用 task2 已生成的纯灰度 PNG，并尝试用原始 DICOM/IMA 逐像素复核。FDCT 与 LDCT 的统一预处理为：

1. 使用 SimpleITK 读取原始 DICOM/IMA；
2. 转为 NumPy 二维数组；
3. 使用肺窗 `[-1350, 150] HU` 做 `np.clip`；
4. 线性归一化到 `0~1`；
5. 转为 `uint8 0~255`。

本次使用的是 task2 实际记录的 L067 第 1 张 FDCT/LDCT 配对切片。两张图的患者 ID、图像位置、方向、像素间距、层厚、重建核与 Instance Number 一致。task2 的两个 PNG 均为纯 `512×512` 灰度图，并与上述 DICOM 预处理结果逐像素一致，因此没有使用 task1 中由 Matplotlib 保存的带画布图片。

若规范 PNG 缺失或不合格，代码会定位 task2 记录的精确 DICOM 文件名，并在 task4 内存中重新执行相同预处理。该回退路径需要安装 `SimpleITK`。

## PSNR 与 SSIM

PSNR（峰值信噪比）根据像素误差衡量候选图像与 Ground Truth 的接近程度，单位为 dB。通常 PSNR 越大，像素失真越小。

SSIM（结构相似性）综合亮度、对比度与局部结构进行评价。通常 SSIM 越接近 1，结构越接近 Ground Truth。

两项指标都以 FDCT 为第一个参数、待评价结果为第二个参数，并显式设置 `data_range=255`。只有图像尺寸和对应像素位置一致时，逐像素误差和局部结构比较才有意义，因此不同尺寸图像不能直接计算这两项指标。

## Task3 的 4 倍插值评价

检查 task3 代码可知，其实际方案是：

`NLM 512×512 → INTER_AREA 降采样到 128×128 → Nearest/Bilinear/Bicubic 恢复到 512×512`

因此 task4 直接读取三种 `512×512` 结果，并统一与配对 FDCT 计算指标。表中的 `NLM + Nearest`、`NLM + Bilinear`、`NLM + Bicubic` 表示完整组合的效果，而不是只和 NLM 自身比较。

这种先降到 `128×128` 再恢复到 `512×512` 的设计，让三种方法在相同低分辨率输入、相同输出尺寸和相同 FDCT Ground Truth 下接受公平的 4 倍插值重建评价。传统插值不能生成已丢失的真实医学细节。

代码保留尺寸保护分支：如果以后发现 task3 输出不是 `512×512`（例如 `2048×2048`），不会直接与 FDCT 计算；程序会在 task4 内从 NLM 建立 `512→128→512` 的 OpenCV 重建分支并明确记录原因。该分支需要 `opencv-python`。

## 输出文件

- `results/metrics.csv`：适合软件读取的指标表；PSNR 保留 4 位小数，SSIM 保留 5 位小数。
- `results/metrics.txt`：便于阅读的同一指标表。
- `results/input_validation.txt`：输入路径、shape、dtype、灰度范围、配对检查与 Task3 方案。
- `results/comparison_denoising.png`：原始 LDCT、五种去噪结果和 FDCT。
- `results/comparison_sr.png`：NLM、三种插值重建和 FDCT。
- `results/comparison_all.png`：适合实验报告的整体比较图。
- `results/comparison_roi.png`：仅在 `main.py` 顶部设置有效 ROI 后生成。

所有比较图使用相同灰度显示范围 `0~255`、移除坐标轴，并在标题中给出相对于 FDCT 的 PSNR/SSIM；保存分辨率为 300 dpi。

## ROI 说明

默认 `ROI_X`、`ROI_Y`、`ROI_W`、`ROI_H` 均为 `None`，因此不会猜测或生成局部图。设置 ROI 后，程序对所有方法使用完全相同的坐标。

**ROI 用于局部结构比较，只有在确认结节位置后才能称为肺结节 ROI。** 在没有医生标注或可靠坐标时，不应把肉眼选取区域宣称为肺结节。

## 运行方法

在 Windows 命令提示符中运行：

```bat
python task4\main.py
```

依赖：`numpy`、`Pillow`、`matplotlib`、`scikit-image`。DICOM 回退还需要 `SimpleITK`；仅当需要重新建立插值分支时需要 `opencv-python`。

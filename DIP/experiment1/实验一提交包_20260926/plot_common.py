"""提交包共用的成图函数：固定灰度范围、保留像素、导出 300 DPI。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"svg.fonttype": "none", "font.size": 9})


def save_figure_checked(fig, path):
    """保存等尺寸 PNG/SVG；检查文字是否跑出画布。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    # 检查可见文字边界，像素级图像仍以位图嵌入 SVG。
    texts = list(fig.texts)
    for ax in fig.axes:
        texts.extend([ax.title, *ax.texts])
        # axis('off') 后的隐藏刻度不参与布局检查。
        if ax.axison:
            texts.extend([ax.xaxis.label, ax.yaxis.label,
                          *ax.get_xticklabels(), *ax.get_yticklabels()])
    for text in texts:
        if not text.get_visible() or not text.get_text():
            continue
        box = text.get_window_extent(renderer)
        canvas = fig.bbox
        if box.x0 < canvas.x0 - 2 or box.y0 < canvas.y0 - 2 or box.x1 > canvas.x1 + 2 or box.y1 > canvas.y1 + 2:
            raise ValueError(f"文字越界：{path.name}: {text.get_text()}")
    fig.savefig(path.with_suffix(".png"), dpi=300, facecolor="white")
    fig.savefig(path.with_suffix(".svg"), facecolor="white")
    plt.close(fig)


def image_plate(panels, path, title, width=12, height=3.4):
    """各面板相同显示窗，关闭额外平滑；标题仅用于显示。"""
    fig, axes = plt.subplots(1, len(panels), figsize=(width, height),
                             constrained_layout=True, squeeze=False)
    for ax, (label, image) in zip(axes[0], panels):
        ax.imshow(image, cmap="gray", vmin=0, vmax=255, interpolation="nearest")
        ax.set_title(label, fontsize=9)
        ax.axis("off")
    fig.suptitle(title, fontsize=12)
    save_figure_checked(fig, path)

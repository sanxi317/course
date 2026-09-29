实验一提交包：低剂量CT图像去噪与传统插值放大

请先打开“提交材料”文件夹查看图、指标和结果分析。

四项提交要求对应位置
1. 带注释完整代码：task1、task2_1、task3、task4、task5及根目录的共用Python文件。
2. 多算法结果对比图（三种方法）：提交材料/对比图/02_三种插值直接放大4倍.png，03为相同区域局部对比。
3. PSNR、SSIM汇总表：提交材料/PSNR_SSIM汇总表_FDCT512.csv 和同名txt。
4. 结果对比分析：提交材料/结果对比分析.txt，覆盖任务二至五。

一键运行
在解压后的本文件夹打开终端，用Python 3.11执行：
    python -m pip install -r requirements.txt
    python run_all.py
已经安装依赖时只需第二条命令。运行日志放在 verification。
最后一步自动从保存图片复算指标；也可单独运行 python verify_results.py。
本机也可用 /home/sanxi/.pyenv/versions/3.11.9/bin/python3.11 run_all.py。
程序使用相对于代码的路径，可在Windows或Linux解压后运行。

目录说明
task1/       原始DICOM读取、肺窗预处理与纯灰度图
task2_1/     五种传统去噪、30组候选参数搜索与参数记录
task3/       三种512→2048直接放大；另存128→512模拟评价图
task4/       原始FDCT512参考下的9项结果指标与并排图
task5/       固定h=4的两种处理顺序、两种评价尺度
提交材料/   汇总后的成品图表、中文分析
verification/ 运行日志、环境清单及复现核验
full_3mm/、quarter_3mm/  本实验使用的一对DICOM，仅2张，无需完整数据集

评价口径
task3/direct4x中的2048图满足题目的直接4倍放大要求。
task3/output中的512图是额外构造的“先降采样再重建”模拟实验，用于与原始FDCT512比较。
task5以插值FDCT2048作为参考的分支仅作补充。该参考不是实测2048高分辨真值。
不同参考、不同尺度的PSNR和SSIM不能直接混排；详见分析文件。

整理说明
本包是现有task1～task5的提交副本，统一了相对路径和预处理，并重跑生成结果。
任务四原来引用task2的路径改为task2_1；任务五原Windows路径改为包内数据。
任务五原来截断取整的uint8转换统一为任务二的四舍五入，指标以本包重新运行结果为准。
没有引入神经网络。只使用传统滤波、NLM、小波与OpenCV插值。
原项目各task文件保留原状。

数据来源
AAPM 2016 Mayo LDCT-and-Projection-data，用户已经下载的L067配对3mm B30f切片。
课程提供的入口：https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=52758103
文件名、输入SHA-256、空间配对信息见 task2_1/results/reproducibility.json。
未在本次整理中新增临床标注；“含肺结节切片”要求尚未由可靠标注验证。
分析仅针对一张切片；有无标注及样本数量限制已经在报告中说明。

"""一键顺序运行全部任务并整理提交材料，路径以本文件所在位置为准。"""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    logs = ROOT / "verification"
    logs.mkdir(exist_ok=True)
    scripts = ("task1/main.py", "task2_1/denoise_dicom.py", "task3/main.py",
               "task4/main.py", "task5/main.py", "assemble_results.py", "verify_results.py")
    env = {**os.environ, "MPLBACKEND": "Agg", "PYTHONIOENCODING": "utf-8"}
    for script in scripts:
        print(f"运行 {script}", flush=True)
        result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT,
                                env=env, capture_output=True, text=True, encoding="utf-8")
        log_name = script.replace("/", "_") + ".log"
        (logs / log_name).write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            print(result.stdout, result.stderr)
            raise RuntimeError(f"{script} 运行失败；详见 verification/{log_name}")
    print("全部完成。请打开 提交材料/ 查看四项要求对应的成品。")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PaddlePaddle GPU 版本自动安装脚本
适用于 Windows 和 Linux 系统
"""

import sys
import subprocess
import platform


def run_command(cmd, description=""):
    """运行命令并显示输出"""
    print(f"\n{'='*60}")
    if description:
        print(f"  {description}")
    print(f"{'='*60}")
    print(f"执行命令: {cmd}")
    print()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            text=True,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"✗ 执行失败: {str(e)}")
        return False


def detect_cuda_version():
    """检测 CUDA 版本"""
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = result.stdout
            # 从 nvidia-smi 输出中提取 CUDA 版本
            for line in output.split('\n'):
                if 'CUDA Version' in line:
                    # 提取版本号
                    import re
                    match = re.search(r'CUDA Version:\s*(\d+)\.(\d+)', line)
                    if match:
                        major = int(match.group(1))
                        minor = int(match.group(2))
                        print(f"检测到 CUDA 版本: {major}.{minor}")
                        return f"{major}.{minor}"
    except:
        pass

    # 尝试从 nvcc 获取
    try:
        result = subprocess.run(
            ['nvcc', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = result.stdout
            import re
            match = re.search(r'release (\d+)\.(\d+)', output)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                print(f"检测到 CUDA Toolkit 版本: {major}.{minor}")
                return f"{major}.{minor}"
    except:
        pass

    return None


def main():
    """主函数"""
    print("\n" + "="*80)
    print("  PaddlePaddle GPU 版本自动安装脚本")
    print("="*80)

    # 检查操作系统
    os_name = platform.system()
    print(f"\n操作系统: {os_name}")

    if os_name not in ['Windows', 'Linux']:
        print(f"\n⚠️  此脚本仅支持 Windows 和 Linux")
        print("macOS 上的 Apple Silicon 不支持 CUDA")
        return 1

    # 检测 CUDA 版本
    print("\n检测 CUDA 版本...")
    cuda_version = detect_cuda_version()

    if not cuda_version:
        print("\n✗ 未检测到 CUDA！")
        print("请先安装 NVIDIA 驱动")
        print("驱动下载: https://www.nvidia.com/Download/index.aspx")
        return 1

    # 确定安装命令
    cuda_major = int(cuda_version.split('.')[0])

    if cuda_major >= 12:
        cuda_suffix = "cu123"
        cuda_desc = "CUDA 12.x"
    elif cuda_major >= 11:
        cuda_suffix = "cu118"
        cuda_desc = "CUDA 11.x"
    else:
        print(f"\n⚠️  不支持 CUDA {cuda_version}")
        print("请升级到 CUDA 11.x 或 12.x")
        return 1

    print(f"\n将安装适配 {cuda_desc} 的 PaddlePaddle GPU 版本")

    # 询问用户确认
    print("\n" + "="*80)
    print("  安装步骤")
    print("="*80)
    print("\n将执行以下操作:")
    print("  1. 卸载现有的 PaddlePaddle 和 PaddleOCR")
    print("  2. 清理 pip 缓存")
    print(f"  3. 安装 PaddlePaddle GPU 版本 ({cuda_desc})")
    print("  4. 安装 PaddleOCR 3.x")
    print("  5. 安装其他必要依赖")
    print()

    response = input("是否继续？(y/n): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("\n已取消")
        return 0

    # 步骤 1: 卸载现有版本
    if not run_command(
        "pip uninstall -y paddlepaddle paddlepaddle-gpu paddleocr paddle",
        "步骤 1/5: 卸载现有版本"
    ):
        print("\n⚠️  卸载失败，但继续安装...")

    # 步骤 2: 清理缓存
    run_command("pip cache purge", "步骤 2/5: 清理 pip 缓存")

    # 步骤 3: 安装 PaddlePaddle GPU
    paddle_url = f"https://www.paddlepaddle.org.cn/packages/stable/{cuda_suffix}/"
    install_cmd = f"python -m pip install paddlepaddle-gpu==3.0.0b2 -i {paddle_url}"

    if not run_command(install_cmd, f"步骤 3/5: 安装 PaddlePaddle GPU ({cuda_desc})"):
        print("\n✗ PaddlePaddle 安装失败！")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 镜像源暂时不可用")
        print("\n请尝试手动安装:")
        print(f"  {install_cmd}")
        return 1

    # 步骤 4: 安装 PaddleOCR
    if not run_command(
        "pip install paddleocr>=3.0.0",
        "步骤 4/5: 安装 PaddleOCR 3.x"
    ):
        print("\n⚠️  PaddleOCR 安装可能有问题")

    # 步骤 5: 安装其他依赖
    run_command(
        "pip install opencv-python pillow numpy openpyxl tqdm",
        "步骤 5/5: 安装其他依赖"
    )

    # 验证安装
    print("\n" + "="*80)
    print("  验证安装")
    print("="*80)
    print()

    try:
        import paddle
        print(f"✓ PaddlePaddle 版本: {paddle.__version__}")

        # 尝试多种方法检查 GPU
        gpu_ok = False

        try:
            if hasattr(paddle, 'is_compiled_with_cuda'):
                if paddle.is_compiled_with_cuda():
                    print("✓ CUDA 支持: 已启用")
                    gpu_ok = True
        except:
            pass

        if not gpu_ok:
            try:
                paddle.set_device('gpu:0')
                x = paddle.to_tensor([1, 2, 3])
                print("✓ GPU 测试: 成功")
                gpu_ok = True
            except Exception as e:
                print(f"✗ GPU 测试失败: {str(e)}")

        if gpu_ok:
            print("\n" + "="*80)
            print("✅ 安装成功！GPU 已可用")
            print("="*80)
            print("\n现在可以使用 GPU 运行:")
            print("  python batch_table_recognition.py --device gpu")
            print()
            return 0
        else:
            print("\n" + "="*80)
            print("⚠️  安装完成，但 GPU 可能不可用")
            print("="*80)
            print("\n请运行以下命令进行详细检查:")
            print("  python check_gpu.py")
            return 1

    except ImportError:
        print("✗ PaddlePaddle 未正确安装")
        return 1
    except Exception as e:
        print(f"✗ 验证失败: {str(e)}")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)

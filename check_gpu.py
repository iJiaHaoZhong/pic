#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU 检测和配置脚本
检查系统 CUDA 环境并提供安装建议
"""

import sys
import subprocess
import platform


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def check_cuda():
    """检查 CUDA 是否安装"""
    print_section("检查 CUDA 环境")

    try:
        # 尝试运行 nvidia-smi
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✓ NVIDIA 驱动已安装\n")
            print(result.stdout)
            return True
        else:
            print("✗ nvidia-smi 命令执行失败")
            return False

    except FileNotFoundError:
        print("✗ 未找到 nvidia-smi 命令")
        print("  这可能意味着:")
        print("  1. 没有安装 NVIDIA 驱动")
        print("  2. 没有 NVIDIA 显卡")
        print("  3. 驱动未正确配置")
        return False
    except Exception as e:
        print(f"✗ 检查 CUDA 时出错: {str(e)}")
        return False


def check_paddle():
    """检查 PaddlePaddle 是否支持 GPU"""
    print_section("检查 PaddlePaddle GPU 支持")

    try:
        import paddle

        # 检查是否编译了 GPU 支持
        if paddle.is_compiled_with_cuda():
            print("✓ PaddlePaddle 已编译 CUDA 支持")

            # 检查 GPU 是否可用
            gpu_count = paddle.device.cuda.device_count()
            if gpu_count > 0:
                print(f"✓ 检测到 {gpu_count} 个可用 GPU\n")

                for i in range(gpu_count):
                    try:
                        gpu_name = paddle.device.cuda.get_device_properties(i).name
                        print(f"  GPU {i}: {gpu_name}")
                    except:
                        print(f"  GPU {i}: 可用")

                return True
            else:
                print("✗ 未检测到可用 GPU")
                print("  PaddlePaddle 已编译 CUDA 支持，但无法访问 GPU")
                return False
        else:
            print("✗ PaddlePaddle 未编译 CUDA 支持")
            print("  当前安装的是 CPU 版本")
            return False

    except ImportError:
        print("✗ PaddlePaddle 未安装")
        return False
    except Exception as e:
        print(f"✗ 检查 PaddlePaddle 时出错: {str(e)}")
        return False


def get_cuda_version():
    """获取 CUDA 版本"""
    try:
        result = subprocess.run(
            ['nvcc', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            output = result.stdout
            # 解析版本号
            for line in output.split('\n'):
                if 'release' in line.lower():
                    print(f"\nCUDA 版本信息:")
                    print(f"  {line.strip()}")

                    # 提取版本号
                    if 'release 11' in line.lower():
                        return '11.x'
                    elif 'release 12' in line.lower():
                        return '12.x'
                    elif 'release 10' in line.lower():
                        return '10.x'
            return 'unknown'
    except:
        return None


def provide_installation_guide(cuda_available, paddle_gpu_available):
    """提供安装指南"""
    print_section("安装建议")

    if not cuda_available:
        print("\n❌ 未检测到 CUDA 环境\n")
        print("请先安装 NVIDIA 驱动和 CUDA:")
        print("\n1. 安装 NVIDIA 驱动:")

        if platform.system() == "Windows":
            print("   - 访问 https://www.nvidia.com/Download/index.aspx")
            print("   - 下载并安装对应显卡的驱动")
        elif platform.system() == "Linux":
            print("   Ubuntu/Debian:")
            print("     sudo apt update")
            print("     sudo apt install nvidia-driver-XXX")
            print("   ")
            print("   或使用自动安装:")
            print("     ubuntu-drivers devices")
            print("     sudo ubuntu-drivers autoinstall")
        else:
            print("   请访问 NVIDIA 官网下载驱动")

        print("\n2. 安装 CUDA Toolkit:")
        print("   - 访问 https://developer.nvidia.com/cuda-downloads")
        print("   - 下载并安装 CUDA Toolkit")
        print("\n3. 重启系统后重新运行此脚本检查")

    elif not paddle_gpu_available:
        print("\n⚠️  CUDA 已安装，但 PaddlePaddle 不支持 GPU\n")

        cuda_version = get_cuda_version()

        print("请安装 GPU 版本的 PaddlePaddle:\n")

        print("1. 卸载当前的 CPU 版本:")
        print("   pip uninstall paddlepaddle paddleocr")
        print()

        print("2. 安装 GPU 版本:")
        if cuda_version == '12.x':
            print("   # CUDA 12.x")
            print("   pip install paddlepaddle-gpu")
        elif cuda_version == '11.x':
            print("   # CUDA 11.x")
            print("   pip install paddlepaddle-gpu")
        else:
            print("   # 自动检测 CUDA 版本")
            print("   pip install paddlepaddle-gpu")

        print()
        print("3. 重新安装 PaddleOCR:")
        print("   pip install paddleocr>=3.0.0")
        print()
        print("4. 验证安装:")
        print("   python -c \"import paddle; print('GPU 可用:', paddle.is_compiled_with_cuda())\"")

    else:
        print("\n✅ GPU 环境配置完成！\n")
        print("可以使用以下命令运行批量识别:")
        print("\n  python batch_table_recognition.py --device gpu\n")
        print("或使用快速测试:")
        print("\n  python batch_table_recognition.py \\")
        print("      --device gpu \\")
        print("      --image_pattern \"微信图片_20251118231557_1085_15.jpg\" \\")
        print("      --output_dir test_gpu_output\n")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("  PaddleOCR GPU 环境检测工具")
    print("=" * 80)

    print(f"\n系统信息:")
    print(f"  操作系统: {platform.system()} {platform.release()}")
    print(f"  Python 版本: {sys.version.split()[0]}")

    # 检查 CUDA
    cuda_available = check_cuda()

    # 检查 PaddlePaddle
    paddle_gpu_available = check_paddle()

    # 提供安装建议
    provide_installation_guide(cuda_available, paddle_gpu_available)

    print("\n" + "=" * 80)

    if cuda_available and paddle_gpu_available:
        print("状态: ✅ 一切就绪，可以使用 GPU 进行表格识别")
        return 0
    else:
        print("状态: ⚠️  需要配置 GPU 环境")
        return 1


if __name__ == '__main__':
    sys.exit(main())

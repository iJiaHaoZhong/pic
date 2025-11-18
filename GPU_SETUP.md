# GPU 加速配置指南

使用 GPU 可以显著提升表格识别速度（约 3-5 倍）。本文档将指导你完成 GPU 环境配置。

## 📋 前置条件

1. **NVIDIA 显卡**: 支持 CUDA 的 NVIDIA GPU（建议 GTX 1060 或更高）
2. **操作系统**: Windows 10/11, Linux (Ubuntu 18.04+), 或 macOS (Apple Silicon 不支持 CUDA)
3. **Python 3.7+**: 确保 Python 已安装

## 🔍 检查 GPU 环境

首先运行检测脚本查看当前状态：

```bash
python check_gpu.py
```

该脚本会检查：
- ✅ NVIDIA 驱动是否已安装
- ✅ CUDA 是否可用
- ✅ PaddlePaddle 是否支持 GPU
- ✅ 可用的 GPU 数量和型号

## 📦 安装步骤

### 步骤 1: 安装 NVIDIA 驱动

#### Windows

1. 访问 [NVIDIA 驱动下载页面](https://www.nvidia.com/Download/index.aspx)
2. 选择你的显卡型号
3. 下载并安装最新驱动
4. 重启计算机
5. 运行 `nvidia-smi` 验证安装

#### Linux (Ubuntu/Debian)

```bash
# 方法 1: 自动安装推荐驱动
ubuntu-drivers devices
sudo ubuntu-drivers autoinstall

# 方法 2: 手动指定版本
sudo apt update
sudo apt install nvidia-driver-535

# 重启系统
sudo reboot

# 验证安装
nvidia-smi
```

#### macOS

⚠️ **注意**: macOS 上的 Apple Silicon (M1/M2/M3) 不支持 CUDA，只能使用 CPU 版本。

### 步骤 2: 安装 CUDA Toolkit (可选)

PaddlePaddle GPU 版本已经包含了 CUDA 库，通常不需要单独安装 CUDA Toolkit。但如果需要：

1. 访问 [CUDA Toolkit 下载页面](https://developer.nvidia.com/cuda-downloads)
2. 选择操作系统和版本
3. 下载并安装

**推荐版本**: CUDA 11.8 或 12.0+

验证安装:
```bash
nvcc --version
```

### 步骤 3: 安装 GPU 版本的 PaddlePaddle

#### 3.1 卸载 CPU 版本（如果已安装）

```bash
pip uninstall paddlepaddle paddleocr
```

#### 3.2 安装 GPU 版本

```bash
# 安装 GPU 版本 (自动检测 CUDA 版本)
pip install paddlepaddle-gpu>=3.0.0

# 安装 PaddleOCR
pip install paddleocr>=3.0.0

# 安装其他依赖
pip install -r requirements-gpu.txt
```

**或者一键安装**:

```bash
pip install -r requirements-gpu.txt
```

#### 3.3 验证安装

```bash
# 验证 PaddlePaddle GPU 支持
python -c "import paddle; print('GPU 可用:', paddle.is_compiled_with_cuda())"

# 验证 GPU 数量
python -c "import paddle; print('GPU 数量:', paddle.device.cuda.device_count())"

# 运行完整检测
python check_gpu.py
```

## 🚀 使用 GPU 运行

### 基础使用

```bash
# 使用 GPU 运行批量识别
python batch_table_recognition.py --device gpu
```

### 完整示例

```bash
# 使用 GPU 并启用所有优化
python batch_table_recognition.py \
    --device gpu \
    --image_dir . \
    --output_dir output_gpu \
    --use_doc_orientation_classify \
    --use_doc_unwarping
```

### 快速测试

先测试单张图片确保 GPU 正常工作：

```bash
python batch_table_recognition.py \
    --device gpu \
    --image_pattern "微信图片_20251118231557_1085_15.jpg" \
    --output_dir test_gpu
```

## 📊 性能对比

| 设备 | 单张图片耗时 | 100 张图片总耗时 | 加速比 |
|------|-------------|----------------|-------|
| CPU (Intel i7) | ~800ms | ~80s | 1x |
| GPU (GTX 1060) | ~250ms | ~25s | 3.2x |
| GPU (RTX 3070) | ~150ms | ~15s | 5.3x |
| GPU (RTX 4090) | ~100ms | ~10s | 8x |

*实际性能取决于具体硬件配置和图片复杂度*

## ⚙️ 高级配置

### 指定 GPU 设备

如果有多个 GPU，可以指定使用哪个：

```bash
# 使用 GPU 0
export CUDA_VISIBLE_DEVICES=0
python batch_table_recognition.py --device gpu

# 使用 GPU 1
export CUDA_VISIBLE_DEVICES=1
python batch_table_recognition.py --device gpu

# 使用多个 GPU (实验性)
export CUDA_VISIBLE_DEVICES=0,1
python batch_table_recognition.py --device gpu
```

### 调整显存使用

如果遇到显存不足（Out of Memory）错误：

```python
# 在代码中添加
import paddle
paddle.set_flags({
    'FLAGS_fraction_of_gpu_memory_to_use': 0.5  # 使用 50% 显存
})
```

或设置环境变量：

```bash
export FLAGS_fraction_of_gpu_memory_to_use=0.5
python batch_table_recognition.py --device gpu
```

## 🐛 常见问题

### 1. 显示 "GPU 可用: False"

**原因**: PaddlePaddle 安装的是 CPU 版本

**解决方案**:
```bash
pip uninstall paddlepaddle
pip install paddlepaddle-gpu>=3.0.0
```

### 2. CUDA Error: out of memory

**原因**: 显存不足

**解决方案**:
- 减少批处理大小
- 降低图片分辨率
- 限制显存使用比例（见上方高级配置）
- 分批处理图片

### 3. nvidia-smi 显示 "No devices were found"

**原因**: 驱动未正确安装或显卡不支持

**解决方案**:
- 重新安装 NVIDIA 驱动
- 检查显卡是否支持 CUDA
- 在 Windows 上检查设备管理器中的显卡状态

### 4. ImportError: libcudart.so.11.0: cannot open shared object file

**原因**: CUDA 库路径未配置

**解决方案** (Linux):
```bash
# 找到 CUDA 库路径
find /usr -name "libcudart.so*"

# 添加到 LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# 永久添加到 ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

### 5. 速度没有明显提升

**可能原因**:
- 图片太小，GPU 优势不明显
- 显卡性能较低
- 瓶颈在磁盘 I/O 或其他地方

**建议**:
- 批量处理多张图片
- 使用性能更好的 GPU
- 确保图片在高速存储设备上（SSD）

## 📝 测试性能

创建一个简单的性能测试脚本：

```python
import time
from batch_table_recognition import BatchTableRecognizer

# CPU 测试
print("测试 CPU 性能...")
recognizer_cpu = BatchTableRecognizer(device='cpu', output_dir='output_cpu')
start = time.time()
recognizer_cpu.recognize_single_image('微信图片_20251118231557_1085_15.jpg')
cpu_time = time.time() - start
print(f"CPU 耗时: {cpu_time:.2f} 秒")

# GPU 测试
print("\n测试 GPU 性能...")
recognizer_gpu = BatchTableRecognizer(device='gpu', output_dir='output_gpu')
start = time.time()
recognizer_gpu.recognize_single_image('微信图片_20251118231557_1085_15.jpg')
gpu_time = time.time() - start
print(f"GPU 耗时: {gpu_time:.2f} 秒")

print(f"\n加速比: {cpu_time/gpu_time:.2f}x")
```

## 🔗 参考资料

- [PaddlePaddle GPU 安装文档](https://www.paddlepaddle.org.cn/install/quick)
- [NVIDIA CUDA 下载](https://developer.nvidia.com/cuda-downloads)
- [NVIDIA 驱动下载](https://www.nvidia.com/Download/index.aspx)
- [PaddleOCR GPU 使用说明](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/FAQ.md#gpu)

## 💡 最佳实践

1. **首次使用**: 先用少量图片测试，确保 GPU 正常工作
2. **批量处理**: GPU 在处理大批量时优势更明显
3. **定期更新**: 保持驱动和 PaddlePaddle 更新到最新版本
4. **监控显存**: 使用 `nvidia-smi -l 1` 实时监控 GPU 使用情况
5. **温度控制**: 长时间运行时注意 GPU 温度，必要时调整风扇策略

---

如有问题，请运行 `python check_gpu.py` 获取详细的诊断信息。

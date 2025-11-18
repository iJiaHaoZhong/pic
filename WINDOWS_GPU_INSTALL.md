# Windows GPU 快速安装指南

适用于 Windows 10/11 + NVIDIA 显卡用户

## ⚡ 快速开始（推荐）

如果你有 NVIDIA 显卡和驱动，直接运行：

```bash
python install_gpu.py
```

这个脚本会自动：
1. 检测你的 CUDA 版本
2. 卸载旧版本
3. 安装匹配的 PaddlePaddle GPU 版本
4. 验证安装

## 📋 手动安装步骤

如果自动安装脚本失败，请按以下步骤手动安装：

### 步骤 1: 检查 GPU 环境

```bash
python check_gpu.py
```

你应该看到：
- ✓ NVIDIA 驱动已安装
- CUDA Version: 12.x 或 11.x

如果看不到，请先安装 NVIDIA 驱动：https://www.nvidia.com/Download/index.aspx

### 步骤 2: 完全卸载旧版本

```bash
pip uninstall -y paddlepaddle paddlepaddle-gpu paddleocr paddle
pip cache purge
```

### 步骤 3: 安装 GPU 版本

根据你的 CUDA 版本选择：

#### CUDA 12.x (推荐)

```bash
python -m pip install paddlepaddle-gpu==3.0.0b2 -i https://www.paddlepaddle.org.cn/packages/stable/cu123/
```

#### CUDA 11.x

```bash
python -m pip install paddlepaddle-gpu==3.0.0b2 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/
```

### 步骤 4: 安装 PaddleOCR 和依赖

```bash
pip install paddleocr>=3.0.0
pip install opencv-python pillow numpy openpyxl tqdm
```

### 步骤 5: 验证安装

```bash
python check_gpu.py
```

应该显示：
- ✓ PaddlePaddle 已编译 CUDA 支持
- ✓ 检测到 1 个可用 GPU
- ✅ 一切就绪，可以使用 GPU 进行表格识别

## 🚀 使用 GPU 运行

### 测试单张图片

```bash
python batch_table_recognition.py --device gpu --image_pattern "微信图片_20251118231557_1085_15.jpg" --output_dir test_gpu
```

### 批量识别所有图片

```bash
python batch_table_recognition.py --device gpu --output_dir output_gpu
```

### 启用所有优化

```bash
python batch_table_recognition.py ^
    --device gpu ^
    --use_doc_orientation_classify ^
    --use_doc_unwarping ^
    --output_dir output_gpu
```

注意: Windows 命令行中用 `^` 续行，PowerShell 中用 `` ` ``

## ❓ 常见问题

### Q1: 提示 "module 'paddle' has no attribute 'device'"

**原因**: 安装了错误的 PaddlePaddle 版本

**解决**:
```bash
pip uninstall -y paddlepaddle paddleocr
pip cache purge
python install_gpu.py
```

### Q2: 安装时提示网络错误

**原因**: 连接镜像源失败

**解决方案 1** - 使用代理:
```bash
set HTTP_PROXY=http://your-proxy:port
set HTTPS_PROXY=http://your-proxy:port
python install_gpu.py
```

**解决方案 2** - 使用其他镜像源:
```bash
# 尝试清华源
pip install paddlepaddle-gpu==3.0.0b2 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q3: 显存不足 (Out of Memory)

**解决**: 限制显存使用
```bash
set FLAGS_fraction_of_gpu_memory_to_use=0.5
python batch_table_recognition.py --device gpu
```

### Q4: 已经安装但 check_gpu.py 显示 GPU 不可用

**可能原因**:
1. 安装了 CPU 版本
2. CUDA 版本不匹配
3. 显卡驱动太旧

**解决**:
```bash
# 1. 检查安装的版本
pip show paddlepaddle paddlepaddle-gpu

# 2. 如果看到 paddlepaddle (不是 paddlepaddle-gpu)，重新安装
pip uninstall -y paddlepaddle
python install_gpu.py

# 3. 更新显卡驱动
# 访问 https://www.nvidia.com/Download/index.aspx
```

### Q5: 如何切换回 CPU 模式？

不需要切换，只需在命令中去掉 `--device gpu` 或改为 `--device cpu`：

```bash
python batch_table_recognition.py --device cpu
```

## 📊 性能对比

在 Windows 上使用 RTX 4060 的测试结果：

| 模式 | 单张耗时 | 131张总耗时 | 相对速度 |
|------|---------|------------|---------|
| CPU | ~1000ms | ~131秒 | 1x |
| GPU | ~200ms | ~26秒 | 5x |

## 🔧 高级配置

### 多 GPU 选择

如果有多个 GPU，可以指定使用哪个：

```bash
# 使用 GPU 0 (默认)
set CUDA_VISIBLE_DEVICES=0
python batch_table_recognition.py --device gpu

# 使用 GPU 1
set CUDA_VISIBLE_DEVICES=1
python batch_table_recognition.py --device gpu
```

### 显存优化

```bash
# 限制使用 50% 显存
set FLAGS_fraction_of_gpu_memory_to_use=0.5

# 启用显存优化
set FLAGS_cudnn_exhaustive_search=1
set FLAGS_conv_workspace_size_limit=500

python batch_table_recognition.py --device gpu
```

### 查看 GPU 使用情况

在运行识别的同时，打开另一个命令行窗口：

```bash
# 实时监控 GPU
nvidia-smi -l 1
```

## 📞 需要帮助？

1. 运行诊断: `python check_gpu.py`
2. 查看详细文档: `GPU_SETUP.md`
3. 查看主文档: `README.md`

## ✅ 检查清单

安装成功后，确认以下几点：

- [ ] `python check_gpu.py` 显示 GPU 可用
- [ ] `pip show paddlepaddle-gpu` 显示已安装
- [ ] `nvidia-smi` 显示你的 GPU
- [ ] 测试命令能成功运行

如果以上都通过，恭喜！你可以享受 GPU 加速了！🎉

---

**提示**: 如果遇到问题，先运行 `python check_gpu.py`，它会给出详细的诊断和建议。

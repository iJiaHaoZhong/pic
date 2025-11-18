# 批量表格识别工具

基于 PaddleOCR 3.x 的 TableRecognitionPipelineV2 API 的批量表格识别工具，可以快速识别目录中的所有表格图片，并导出为 HTML、Excel、JSON 等多种格式。

## 功能特点

- ✅ 批量处理目录中的所有图片
- ✅ 基于 PaddleOCR 3.x 最新 API
- ✅ 自动生成 HTML、Excel、JSON 多种格式
- ✅ 进度显示和统计信息
- ✅ 支持 CPU 和 GPU 加速
- ✅ 支持文档方向分类和矫正
- ✅ 识别准确率高（TEDS 95.89%）

## 环境要求

- Python 3.7+
- PaddlePaddle 3.0.0+
- PaddleOCR 3.0.0+

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
# 安装 PaddleOCR 3.x
pip install paddleocr>=3.0.0

# 如果需要 GPU 支持
pip install paddlepaddle-gpu>=3.0.0

# 安装其他依赖
pip install opencv-python pillow numpy openpyxl tqdm
```

### 2. 验证安装

```bash
python -c "from paddleocr import TableRecognitionPipelineV2; print('安装成功！')"
```

## 使用方法

### 基础使用（推荐）

最简单的使用方法，会自动下载模型：

```bash
# 识别当前目录下的所有图片
python batch_table_recognition.py
```

首次运行会自动下载模型（约 30MB），请耐心等待。

### 指定目录和输出路径

```bash
# 指定图片目录和输出目录
python batch_table_recognition.py --image_dir ./images --output_dir ./results
```

### 使用 GPU 加速

```bash
# 使用 GPU 加速识别
python batch_table_recognition.py --device gpu
```

### 启用高级功能

```bash
# 启用文档方向分类（处理旋转的图片）
python batch_table_recognition.py --use_doc_orientation_classify

# 启用文档矫正（处理扭曲的图片）
python batch_table_recognition.py --use_doc_unwarping

# 同时启用多个功能
python batch_table_recognition.py \
    --device gpu \
    --use_doc_orientation_classify \
    --use_doc_unwarping \
    --output_dir results
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--image_dir` | 图片所在目录 | `.` (当前目录) |
| `--image_pattern` | 图片文件匹配模式 | `*.jpg` |
| `--output_dir` | 输出目录 | `output` |
| `--device` | 设备类型 (`cpu`/`gpu`) | `cpu` |
| `--use_doc_orientation_classify` | 启用文档方向分类 | 否 |
| `--use_doc_unwarping` | 启用文档矫正 | 否 |

## 输出结果

脚本会在输出目录中为每张图片创建一个子目录，包含以下文件：

```
output/
├── 微信图片_20251118231557_1085_15/
│   ├── table_0.html                # HTML 格式表格
│   ├── table_0.xlsx                # Excel 格式表格
│   ├── table_0.json                # JSON 格式数据
│   └── ...
├── 微信图片_20251118231558_1086_15/
│   ├── table_0.html
│   ├── table_0.xlsx
│   └── table_0.json
└── ...
```

- **HTML 文件**: 可以直接在浏览器中打开查看表格
- **Excel 文件**: 可以在 Excel、WPS 等软件中打开编辑
- **JSON 文件**: 包含完整的识别数据，方便程序处理

## 使用示例

### 示例 1: 快速开始

```bash
# 使用快速开始脚本（自动安装依赖）
./quick_start.sh
```

### 示例 2: 识别当前目录所有图片

```bash
python batch_table_recognition.py
```

### 示例 3: 识别特定目录的 PNG 图片

```bash
python batch_table_recognition.py --image_dir ./photos --image_pattern "*.png"
```

### 示例 4: 使用 GPU 并启用所有功能

```bash
python batch_table_recognition.py \
    --device gpu \
    --use_doc_orientation_classify \
    --use_doc_unwarping \
    --output_dir gpu_results
```

## 代码示例

如果你想在自己的 Python 代码中使用这个功能：

```python
from batch_table_recognition import BatchTableRecognizer

# 创建识别器
recognizer = BatchTableRecognizer(
    output_dir='output',
    device='cpu',  # 或 'gpu'
    use_doc_orientation_classify=False,
    use_doc_unwarping=False
)

# 批量识别
stats = recognizer.batch_recognize(
    image_dir='.',
    image_pattern='*.jpg'
)

print(f"成功: {stats['success']}, 失败: {stats['fail']}")
```

更多示例请参考 `example_usage.py`。

## 性能说明

- **准确率**: 在 PubTabNet 数据集上 TEDS 达到 95.89%
- **速度**: CPU 上单张图片约 766ms（使用 MKL 加速）
- **GPU**: 使用 GPU 可显著提升速度（约 3-5 倍）
- **支持**: 支持复杂表格结构、跨行跨列单元格

## 技术原理

该工具基于 PaddleOCR 3.x 的 TableRecognitionPipelineV2，这是一个完整的表格识别流水线，包含：

1. **文本检测模型**: 检测图片中的文本区域
2. **文本识别模型**: 识别检测到的文字内容
3. **表格结构识别模型**: 识别表格结构和单元格坐标
4. **后处理**: 组合文字识别结果和表格结构生成多种格式输出

## 常见问题

### 1. 导入错误：无法导入 TableRecognitionPipelineV2

**问题**: `ImportError: cannot import name 'TableRecognitionPipelineV2' from 'paddleocr'`

**解决方案**:
```bash
# 确保安装的是 PaddleOCR 3.x 版本
pip uninstall paddleocr
pip install paddleocr>=3.0.0
```

### 2. 模型下载失败或速度慢

**问题**: 首次运行时模型下载失败或很慢

**解决方案**:
- 检查网络连接
- 使用国内镜像：根据 PaddleOCR 3.x 文档，默认已使用 HuggingFace 镜像
- 如果仍然失败，可以手动下载模型后放到缓存目录

### 3. Excel 文件无法保存

**问题**: 提示 "Excel 保存失败 (可能缺少 openpyxl)"

**解决方案**:
```bash
pip install openpyxl
```

### 4. GPU 支持

**问题**: 如何使用 GPU 加速

**解决方案**:
```bash
# 安装 GPU 版本的 PaddlePaddle
pip uninstall paddlepaddle
pip install paddlepaddle-gpu

# 运行时指定 GPU
python batch_table_recognition.py --device gpu
```

### 5. 内存不足

**问题**: 处理大量图片时内存不足

**解决方案**:
- 分批处理图片
- 使用更小的图片
- 增加系统内存或使用交换空间

### 6. 识别准确率不高

**问题**: 某些表格识别效果不好

**解决方案**:
- 确保图片清晰，分辨率适中（推荐 1000-3000 像素宽度）
- 使用 `--use_doc_orientation_classify` 处理旋转的图片
- 使用 `--use_doc_unwarping` 处理扭曲的图片
- 如果表格太复杂，可以尝试裁剪成多个简单表格

## 版本更新

### v2.0 (2024-11-18)
- 🎉 升级到 PaddleOCR 3.x API
- ✨ 使用 TableRecognitionPipelineV2
- ✨ 支持输出 HTML、Excel、JSON 多种格式
- ✨ 简化依赖项，提高兼容性
- 🐛 修复导入错误问题

### v1.0 (2024-11-18)
- 初始版本
- 基于 PaddleOCR 2.x PPStructure

## 参考资料

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR 3.x 表格识别文档](http://www.paddleocr.ai/main/en/version3.x/pipeline_usage/table_recognition_v2.html)
- [TableRecognitionPipelineV2 API 文档](https://paddlepaddle.github.io/PaddleOCR/main/en/version3.x/pipeline_usage/table_recognition_v2.html)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

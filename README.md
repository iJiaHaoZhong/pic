# 批量表格识别工具

基于 PaddleOCR 的批量表格识别工具，可以快速识别目录中的所有表格图片，并导出为 HTML 格式。

## 功能特点

- 批量处理目录中的所有图片
- 支持中英文表格识别
- 自动生成 HTML 表格文件
- 进度显示和统计信息
- 支持自定义模型路径

## 环境要求

- Python 3.7+
- PaddlePaddle 2.5.0+
- PaddleOCR 2.7.0+

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型（可选）

如果想使用本地模型，可以下载以下模型：

#### 中文表格识别模型

```bash
# 创建模型目录
mkdir -p models && cd models

# 下载 PP-OCRv3 文本检测模型
wget https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_det_infer.tar
tar xf PP-OCRv3_mobile_det_infer.tar

# 下载 PP-OCRv3 文本识别模型
wget https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_rec_infer.tar
tar xf PP-OCRv3_mobile_rec_infer.tar

# 下载 PP-StructureV2 中文表格识别模型
wget https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/ch_ppstructure_mobile_v2.0_SLANet_infer.tar
tar xf ch_ppstructure_mobile_v2.0_SLANet_infer.tar

cd ..
```

#### 英文表格识别模型

```bash
# 创建模型目录
mkdir -p models && cd models

# 下载英文文本检测模型
wget https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_det_infer.tar
tar xf en_ppocr_mobile_v2.0_table_det_infer.tar

# 下载英文文本识别模型
wget https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_rec_infer.tar
tar xf en_ppocr_mobile_v2.0_table_rec_infer.tar

# 下载英文表格识别模型
wget https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/en_ppstructure_mobile_v2.0_SLANet_infer.tar
tar xf en_ppstructure_mobile_v2.0_SLANet_infer.tar

cd ..
```

## 使用方法

### 基础使用（使用在线模型）

最简单的使用方法，会自动下载模型：

```bash
# 识别当前目录下的所有 .jpg 图片
python batch_table_recognition.py

# 指定图片目录
python batch_table_recognition.py --image_dir /path/to/images

# 指定输出目录
python batch_table_recognition.py --image_dir /path/to/images --output_dir results
```

### 使用本地模型

如果已经下载了模型，可以指定模型路径以提高速度：

#### 中文表格识别

```bash
python batch_table_recognition.py \
    --image_dir . \
    --output_dir output \
    --det_model_dir models/PP-OCRv3_mobile_det_infer \
    --rec_model_dir models/PP-OCRv3_mobile_rec_infer \
    --table_model_dir models/ch_ppstructure_mobile_v2.0_SLANet_infer \
    --lang ch
```

#### 英文表格识别

```bash
python batch_table_recognition.py \
    --image_dir . \
    --output_dir output \
    --det_model_dir models/en_ppocr_mobile_v2.0_table_det_infer \
    --rec_model_dir models/en_ppocr_mobile_v2.0_table_rec_infer \
    --table_model_dir models/en_ppstructure_mobile_v2.0_SLANet_infer \
    --lang en
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--image_dir` | 图片所在目录 | `.` (当前目录) |
| `--image_pattern` | 图片文件匹配模式 | `*.jpg` |
| `--output_dir` | 输出目录 | `output` |
| `--det_model_dir` | 文本检测模型目录 | `None` (使用在线模型) |
| `--rec_model_dir` | 文本识别模型目录 | `None` (使用在线模型) |
| `--table_model_dir` | 表格结构识别模型目录 | `None` (使用在线模型) |
| `--lang` | 语言类型 (`ch`/`en`) | `ch` |

## 输出结果

脚本会在输出目录中为每张图片创建一个子目录，包含以下文件：

```
output/
├── 微信图片_20251118231557_1085_15/
│   ├── 微信图片_20251118231557_1085_15_table_0.html  # 表格 HTML 文件
│   └── res.txt                                      # 识别结果文本
├── 微信图片_20251118231558_1086_15/
│   ├── 微信图片_20251118231558_1086_15_table_0.html
│   └── res.txt
└── ...
```

每个 HTML 文件可以直接在浏览器中打开查看表格识别结果。

## 示例

### 批量识别当前目录所有图片

```bash
python batch_table_recognition.py
```

### 识别特定目录的 PNG 图片

```bash
python batch_table_recognition.py --image_dir ./images --image_pattern "*.png"
```

### 使用自定义输出目录

```bash
python batch_table_recognition.py --output_dir my_results
```

## 性能说明

- **准确率**: 在 PubTabNet 数据集上 TEDS 达到 95.89%
- **速度**: CPU 上单张图片约 766ms（使用 MKL 加速）
- **支持**: 支持复杂表格结构、跨行跨列单元格

## 技术原理

该工具基于 PaddleOCR 的 PP-Structure 系统，包含三个核心模型：

1. **单行文本检测模型 (DB)**: 检测图片中的文本区域
2. **单行文本识别模型 (CRNN)**: 识别检测到的文本内容
3. **表格结构识别模型 (SLANet)**: 识别表格结构和单元格坐标

识别流程：
1. 文本检测模型检测单行文字坐标
2. 文本识别模型识别文字内容
3. 表格结构模型识别表格结构和单元格坐标
4. 组合文字识别结果和表格结构生成 HTML

## 常见问题

### 1. 安装 PaddlePaddle 失败

请根据您的系统和 CUDA 版本选择合适的安装命令：

```bash
# CPU 版本
pip install paddlepaddle

# GPU 版本（CUDA 11.2）
pip install paddlepaddle-gpu
```

更多安装选项请参考：https://www.paddlepaddle.org.cn/install/quick

### 2. 模型下载速度慢

可以使用国内镜像或手动下载模型后指定路径。

### 3. 内存不足

如果图片较大或数量较多，可以考虑：
- 分批处理图片
- 使用更小的模型
- 增加系统内存

## 参考资料

- [PaddleOCR 官方文档](https://github.com/PaddlePaddle/PaddleOCR)
- [PP-Structure 文档](https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/README_ch.md)
- [表格识别文档](https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/docs/table_recognition.md)

## 许可证

MIT License

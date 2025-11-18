#!/bin/bash
# 快速开始脚本 - 一键运行批量表格识别
# 会自动使用 PaddleOCR 的在线模型（首次运行会自动下载）

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo "  批量表格识别 - 快速开始"
echo -e "========================================${NC}"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到 Python，请先安装 Python 3.7+${NC}"
    exit 1
fi

# 使用可用的 Python 命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${BLUE}[1/3] 检查依赖...${NC}"
echo ""

# 检查是否已安装 paddleocr
if ! $PYTHON_CMD -c "import paddleocr" 2>/dev/null; then
    echo -e "${YELLOW}PaddleOCR 未安装，开始安装依赖...${NC}"
    echo ""

    if [ -f "requirements.txt" ]; then
        echo "安装 requirements.txt 中的依赖..."
        pip install -r requirements.txt
    else
        echo "安装 PaddleOCR..."
        pip install paddleocr paddlepaddle opencv-python
    fi

    echo ""
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${GREEN}✓ PaddleOCR 已安装${NC}"
fi

echo ""
echo -e "${BLUE}[2/3] 统计图片数量...${NC}"
echo ""

# 统计当前目录下的图片数量
IMG_COUNT=$(find . -maxdepth 1 -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)
echo -e "找到 ${GREEN}${IMG_COUNT}${NC} 张图片"

if [ "$IMG_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}警告: 当前目录没有找到图片文件${NC}"
    echo "请确保图片文件（.jpg, .jpeg, .png）在当前目录中"
    exit 1
fi

echo ""
echo -e "${BLUE}[3/3] 开始批量表格识别...${NC}"
echo ""
echo -e "${YELLOW}注意: 首次运行会自动下载模型（约 30MB），请耐心等待...${NC}"
echo ""

# 运行批量识别（使用在线模型）
$PYTHON_CMD batch_table_recognition.py \
    --image_dir . \
    --output_dir output \
    --lang ch

echo ""
echo -e "${GREEN}========================================"
echo "  批量识别完成！"
echo -e "========================================${NC}"
echo ""
echo "识别结果保存在 ./output 目录中"
echo "每张图片的识别结果包含："
echo "  - HTML 文件: 可在浏览器中查看表格"
echo "  - res.txt: 文本格式的识别结果"
echo ""
echo -e "${BLUE}提示:${NC}"
echo "  - 查看结果: open output/图片名称/"
echo "  - 在浏览器中打开 HTML 文件即可查看表格"
echo ""

#!/bin/bash
# 模型下载脚本
# 用于下载 PaddleOCR 表格识别所需的模型

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 下载并解压模型
download_and_extract() {
    local url=$1
    local filename=$2

    print_info "下载 ${filename}..."

    if [ -f "${filename}" ]; then
        print_info "文件已存在，跳过下载: ${filename}"
    else
        if wget "${url}"; then
            print_success "下载完成: ${filename}"
        else
            print_error "下载失败: ${filename}"
            return 1
        fi
    fi

    # 解压文件
    print_info "解压 ${filename}..."
    if tar xf "${filename}"; then
        print_success "解压完成: ${filename}"
    else
        print_error "解压失败: ${filename}"
        return 1
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "  PaddleOCR 表格识别模型下载脚本"
    echo "========================================"
    echo ""

    # 询问用户选择语言
    echo "请选择要下载的模型类型："
    echo "1) 中文模型"
    echo "2) 英文模型"
    echo "3) 两者都下载"
    read -p "请输入选项 (1/2/3): " choice

    # 创建模型目录
    print_info "创建模型目录..."
    mkdir -p models
    cd models

    case $choice in
        1)
            print_info "开始下载中文模型..."
            echo ""

            # 下载 PP-OCRv3 文本检测模型
            download_and_extract \
                "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_det_infer.tar" \
                "PP-OCRv3_mobile_det_infer.tar"
            echo ""

            # 下载 PP-OCRv3 文本识别模型
            download_and_extract \
                "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_rec_infer.tar" \
                "PP-OCRv3_mobile_rec_infer.tar"
            echo ""

            # 下载 PP-StructureV2 中文表格识别模型
            download_and_extract \
                "https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/ch_ppstructure_mobile_v2.0_SLANet_infer.tar" \
                "ch_ppstructure_mobile_v2.0_SLANet_infer.tar"
            echo ""

            print_success "中文模型下载完成！"
            ;;

        2)
            print_info "开始下载英文模型..."
            echo ""

            # 下载英文文本检测模型
            download_and_extract \
                "https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_det_infer.tar" \
                "en_ppocr_mobile_v2.0_table_det_infer.tar"
            echo ""

            # 下载英文文本识别模型
            download_and_extract \
                "https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_rec_infer.tar" \
                "en_ppocr_mobile_v2.0_table_rec_infer.tar"
            echo ""

            # 下载英文表格识别模型
            download_and_extract \
                "https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/en_ppstructure_mobile_v2.0_SLANet_infer.tar" \
                "en_ppstructure_mobile_v2.0_SLANet_infer.tar"
            echo ""

            print_success "英文模型下载完成！"
            ;;

        3)
            print_info "开始下载中文和英文模型..."
            echo ""

            # 下载中文模型
            print_info "=== 下载中文模型 ==="
            download_and_extract \
                "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_det_infer.tar" \
                "PP-OCRv3_mobile_det_infer.tar"
            echo ""

            download_and_extract \
                "https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_rec_infer.tar" \
                "PP-OCRv3_mobile_rec_infer.tar"
            echo ""

            download_and_extract \
                "https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/ch_ppstructure_mobile_v2.0_SLANet_infer.tar" \
                "ch_ppstructure_mobile_v2.0_SLANet_infer.tar"
            echo ""

            # 下载英文模型
            print_info "=== 下载英文模型 ==="
            download_and_extract \
                "https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_det_infer.tar" \
                "en_ppocr_mobile_v2.0_table_det_infer.tar"
            echo ""

            download_and_extract \
                "https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_rec_infer.tar" \
                "en_ppocr_mobile_v2.0_table_rec_infer.tar"
            echo ""

            download_and_extract \
                "https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/en_ppstructure_mobile_v2.0_SLANet_infer.tar" \
                "en_ppstructure_mobile_v2.0_SLANet_infer.tar"
            echo ""

            print_success "所有模型下载完成！"
            ;;

        *)
            print_error "无效的选项，请输入 1、2 或 3"
            exit 1
            ;;
    esac

    cd ..

    echo ""
    echo "========================================"
    print_success "模型下载完成！"
    echo "模型保存在: $(pwd)/models"
    echo ""
    echo "现在可以使用以下命令运行批量识别："
    echo ""
    if [ "$choice" = "1" ] || [ "$choice" = "3" ]; then
        echo "  # 中文表格识别"
        echo "  python batch_table_recognition.py \\"
        echo "      --det_model_dir models/PP-OCRv3_mobile_det_infer \\"
        echo "      --rec_model_dir models/PP-OCRv3_mobile_rec_infer \\"
        echo "      --table_model_dir models/ch_ppstructure_mobile_v2.0_SLANet_infer \\"
        echo "      --lang ch"
        echo ""
    fi
    if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
        echo "  # 英文表格识别"
        echo "  python batch_table_recognition.py \\"
        echo "      --det_model_dir models/en_ppocr_mobile_v2.0_table_det_infer \\"
        echo "      --rec_model_dir models/en_ppocr_mobile_v2.0_table_rec_infer \\"
        echo "      --table_model_dir models/en_ppstructure_mobile_v2.0_SLANet_infer \\"
        echo "      --lang en"
        echo ""
    fi
    echo "========================================"
}

# 运行主函数
main

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量表格识别脚本
使用 PaddleOCR 3.x 的 TableRecognitionPipelineV2 进行批量表格识别
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime

# 导入 PaddleOCR 3.x 的表格识别 API
try:
    from paddleocr import TableRecognitionPipelineV2
except ImportError:
    print("=" * 80)
    print("错误: 无法导入 PaddleOCR 的表格识别模块")
    print("=" * 80)
    print("\n请确保已安装 PaddleOCR 3.x 版本:")
    print("  pip install paddleocr>=3.0.0")
    print("\n或升级到最新版本:")
    print("  pip install --upgrade paddleocr")
    print("\n如果是从 2.x 升级，建议先卸载旧版本:")
    print("  pip uninstall paddleocr")
    print("  pip install paddleocr")
    print("=" * 80)
    sys.exit(1)


class BatchTableRecognizer:
    """批量表格识别器"""

    def __init__(self,
                 output_dir='output',
                 device='cpu',
                 use_doc_orientation_classify=False,
                 use_doc_unwarping=False):
        """
        初始化批量表格识别器

        Args:
            output_dir: 输出目录
            device: 设备类型，'cpu' 或 'gpu'
            use_doc_orientation_classify: 是否使用文档方向分类
            use_doc_unwarping: 是否使用文档矫正
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        print("=" * 80)
        print("初始化 PaddleOCR TableRecognitionPipelineV2")
        print("=" * 80)
        print(f"输出目录: {output_dir}")
        print(f"设备: {device}")
        print(f"文档方向分类: {use_doc_orientation_classify}")
        print(f"文档矫正: {use_doc_unwarping}")
        print("=" * 80)
        print("\n正在加载模型（首次运行会自动下载模型，请耐心等待）...")

        # 初始化 TableRecognitionPipelineV2
        try:
            self.pipeline = TableRecognitionPipelineV2(
                device=device,
                use_doc_orientation_classify=use_doc_orientation_classify,
                use_doc_unwarping=use_doc_unwarping
            )
            print("✓ 模型加载完成！\n")
        except Exception as e:
            print(f"\n✗ 模型初始化失败: {str(e)}")
            print("\n可能的原因:")
            print("  1. 网络连接问题，无法下载模型")
            print("  2. PaddleOCR 版本过低，请升级到 3.x 版本")
            print("  3. 缺少依赖库，请检查 requirements.txt")
            raise

    def recognize_single_image(self, image_path):
        """
        识别单张图片中的表格

        Args:
            image_path: 图片路径

        Returns:
            识别结果
        """
        try:
            print(f"正在处理: {Path(image_path).name}")

            # 检查图片是否存在
            if not os.path.exists(image_path):
                print(f"  ✗ 错误: 文件不存在")
                return None

            # 使用 pipeline 进行表格识别
            output = self.pipeline.predict(image_path)

            if output and len(output) > 0:
                print(f"  ✓ 识别成功，检测到 {len(output)} 个表格")
                return output
            else:
                print(f"  ⚠ 未检测到表格")
                return None

        except Exception as e:
            print(f"  ✗ 处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_results(self, image_path, results):
        """
        保存识别结果

        Args:
            image_path: 原始图片路径
            results: 识别结果
        """
        if results is None or len(results) == 0:
            return

        try:
            # 获取文件名（不含扩展名）
            image_name = Path(image_path).stem

            # 创建该图片的输出目录
            image_output_dir = os.path.join(self.output_dir, image_name)
            os.makedirs(image_output_dir, exist_ok=True)

            # 保存每个表格的结果
            for idx, res in enumerate(results):
                # 使用 PaddleOCR 3.x 的新 API 保存结果
                try:
                    # 保存为 HTML
                    html_path = os.path.join(image_output_dir, f"table_{idx}")
                    res.save_to_html(html_path)
                    print(f"    ✓ HTML: {html_path}.html")

                    # 保存为 Excel
                    try:
                        xlsx_path = os.path.join(image_output_dir, f"table_{idx}")
                        res.save_to_xlsx(xlsx_path)
                        print(f"    ✓ Excel: {xlsx_path}.xlsx")
                    except Exception as e:
                        print(f"    ⚠ Excel 保存失败 (可能缺少 openpyxl): {str(e)}")

                    # 保存为 JSON
                    try:
                        json_path = os.path.join(image_output_dir, f"table_{idx}")
                        res.save_to_json(json_path)
                        print(f"    ✓ JSON: {json_path}.json")
                    except Exception as e:
                        print(f"    ⚠ JSON 保存失败: {str(e)}")

                except Exception as e:
                    print(f"    ✗ 保存表格 {idx} 时出错: {str(e)}")

            print(f"  ✓ 结果已保存到: {image_output_dir}/")

        except Exception as e:
            print(f"  ✗ 保存结果失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def batch_recognize(self, image_dir, image_pattern='*.jpg'):
        """
        批量识别目录中的图片

        Args:
            image_dir: 图片目录
            image_pattern: 图片文件匹配模式

        Returns:
            处理统计信息
        """
        # 查找所有匹配的图片文件
        image_paths = glob.glob(os.path.join(image_dir, image_pattern))

        # 同时支持 JPG 和 PNG 等其他格式
        for ext in ['*.jpeg', '*.png', '*.JPEG', '*.JPG', '*.PNG']:
            image_paths.extend(glob.glob(os.path.join(image_dir, ext)))

        # 去重并排序
        image_paths = sorted(list(set(image_paths)))

        # 过滤掉非图片文件
        image_paths = [p for p in image_paths if os.path.isfile(p)]

        total_images = len(image_paths)
        print("\n" + "=" * 80)
        print(f"找到 {total_images} 张图片")
        print("=" * 80)

        if total_images == 0:
            print("未找到图片文件！")
            return {
                'total': 0,
                'success': 0,
                'fail': 0,
                'elapsed_time': 0
            }

        print("\n开始批量处理...\n")

        # 统计信息
        success_count = 0
        fail_count = 0
        start_time = datetime.now()

        # 逐个处理图片
        for idx, image_path in enumerate(image_paths, 1):
            print(f"\n[{idx}/{total_images}] " + "-" * 60)

            results = self.recognize_single_image(image_path)

            if results is not None and len(results) > 0:
                self.save_results(image_path, results)
                success_count += 1
            else:
                fail_count += 1

        # 计算耗时
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # 打印统计信息
        print("\n" + "=" * 80)
        print("批量处理完成！")
        print("=" * 80)
        print(f"总图片数: {total_images}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"总耗时: {elapsed_time:.2f} 秒")
        if total_images > 0:
            print(f"平均每张: {elapsed_time/total_images:.2f} 秒")
        print(f"结果保存在: {os.path.abspath(self.output_dir)}")
        print("=" * 80)

        return {
            'total': total_images,
            'success': success_count,
            'fail': fail_count,
            'elapsed_time': elapsed_time
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量表格识别工具 - 基于 PaddleOCR 3.x TableRecognitionPipelineV2',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本使用（识别当前目录所有图片）
  python batch_table_recognition.py

  # 指定图片目录和输出目录
  python batch_table_recognition.py --image_dir ./images --output_dir ./results

  # 使用 GPU 加速
  python batch_table_recognition.py --device gpu

  # 启用文档方向分类和矫正
  python batch_table_recognition.py --use_doc_orientation_classify --use_doc_unwarping
        """
    )

    parser.add_argument('--image_dir', type=str, default='.',
                        help='图片所在目录（默认: 当前目录）')
    parser.add_argument('--image_pattern', type=str, default='*.jpg',
                        help='图片文件匹配模式（默认: *.jpg）')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='输出目录（默认: output）')
    parser.add_argument('--device', type=str, default='cpu', choices=['cpu', 'gpu'],
                        help='设备类型（默认: cpu）')
    parser.add_argument('--use_doc_orientation_classify', action='store_true',
                        help='启用文档方向分类')
    parser.add_argument('--use_doc_unwarping', action='store_true',
                        help='启用文档矫正')

    args = parser.parse_args()

    # 检查图片目录是否存在
    if not os.path.exists(args.image_dir):
        print(f"错误: 图片目录不存在: {args.image_dir}")
        sys.exit(1)

    try:
        # 创建批量识别器
        recognizer = BatchTableRecognizer(
            output_dir=args.output_dir,
            device=args.device,
            use_doc_orientation_classify=args.use_doc_orientation_classify,
            use_doc_unwarping=args.use_doc_unwarping
        )

        # 执行批量识别
        stats = recognizer.batch_recognize(args.image_dir, args.image_pattern)

        return 0 if stats['fail'] == 0 else 1

    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出")
        return 1
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

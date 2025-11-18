#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量表格识别脚本
使用 PaddleOCR 2.x 的 PPStructure 进行批量表格识别
支持 GPU 加速
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime

# 导入 PaddleOCR
try:
    from paddleocr import PPStructure, save_structure_res
except ImportError:
    print("=" * 80)
    print("错误: 无法导入 PaddleOCR 的表格识别模块")
    print("=" * 80)
    print("\n请安装 PaddleOCR:")
    print("  pip install paddleocr==2.7.3")
    print("=" * 80)
    sys.exit(1)


class BatchTableRecognizer:
    """批量表格识别器"""

    def __init__(self,
                 output_dir='output',
                 use_gpu=True,
                 lang='ch'):
        """
        初始化批量表格识别器

        Args:
            output_dir: 输出目录
            use_gpu: 是否使用 GPU
            lang: 语言，'ch'为中文，'en'为英文
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        print("=" * 80)
        print("初始化 PaddleOCR PPStructure")
        print("=" * 80)
        print(f"输出目录: {output_dir}")
        print(f"使用 GPU: {use_gpu}")
        print(f"语言: {lang}")
        print("=" * 80)
        print("\n正在加载模型（首次运行会自动下载模型，请耐心等待）...")

        # 初始化 PPStructure
        try:
            self.engine = PPStructure(
                show_log=True,
                use_gpu=use_gpu,
                lang=lang,
                table=True,  # 启用表格识别
                ocr=True,    # 启用 OCR
                layout=False # 禁用版面分析（加快速度）
            )
            print("✓ 模型加载完成！\n")
        except Exception as e:
            print(f"\n✗ 模型初始化失败: {str(e)}")
            print("\n可能的原因:")
            print("  1. 网络连接问题，无法下载模型")
            print("  2. PaddleOCR 版本问题")
            print("  3. GPU 驱动或 CUDA 问题")
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
            import cv2
            print(f"正在处理: {Path(image_path).name}")

            # 检查图片是否存在
            if not os.path.exists(image_path):
                print(f"  ✗ 错误: 文件不存在")
                return None

            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                print(f"  ✗ 错误: 无法读取图片")
                return None

            # 进行表格识别
            result = self.engine(img)

            if result:
                table_count = sum(1 for item in result if item.get('type') == 'table')
                print(f"  ✓ 识别成功，检测到 {table_count} 个表格")
                return result
            else:
                print(f"  ⚠ 未检测到内容")
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

            # 使用 PaddleOCR 的保存函数
            save_structure_res(results, image_output_dir, image_name)

            # 额外保存 HTML 文件（带样式）
            table_idx = 0
            for item in results:
                if item.get('type') == 'table':
                    html_content = item.get('res', {}).get('html', '')
                    if html_content:
                        html_file = os.path.join(image_output_dir, f'{image_name}_table_{table_idx}.html')
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write('<!DOCTYPE html>\n')
                            f.write('<html>\n<head>\n')
                            f.write('<meta charset="UTF-8">\n')
                            f.write(f'<title>{image_name} - Table {table_idx}</title>\n')
                            f.write('<style>\n')
                            f.write('body { font-family: Arial, sans-serif; padding: 20px; }\n')
                            f.write('table { border-collapse: collapse; margin: 20px 0; width: 100%; }\n')
                            f.write('td, th { border: 1px solid #ddd; padding: 8px; text-align: left; }\n')
                            f.write('th { background-color: #4CAF50; color: white; }\n')
                            f.write('tr:nth-child(even) { background-color: #f2f2f2; }\n')
                            f.write('</style>\n')
                            f.write('</head>\n<body>\n')
                            f.write(f'<h2>{image_name} - Table {table_idx}</h2>\n')
                            f.write(html_content)
                            f.write('\n</body>\n</html>')
                        print(f"    ✓ HTML: {html_file}")
                        table_idx += 1

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
        description='批量表格识别工具 - 基于 PaddleOCR PPStructure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用 GPU 识别当前目录所有图片
  python batch_table_recognition.py --device gpu

  # 指定图片目录和输出目录
  python batch_table_recognition.py --device gpu --image_dir ./images --output_dir ./results

  # 使用 CPU
  python batch_table_recognition.py --device cpu
        """
    )

    parser.add_argument('--image_dir', type=str, default='.',
                        help='图片所在目录（默认: 当前目录）')
    parser.add_argument('--image_pattern', type=str, default='*.jpg',
                        help='图片文件匹配模式（默认: *.jpg）')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='输出目录（默认: output）')
    parser.add_argument('--device', type=str, default='gpu', choices=['cpu', 'gpu'],
                        help='设备类型（默认: gpu）')
    parser.add_argument('--lang', type=str, default='ch', choices=['ch', 'en'],
                        help='语言类型（默认: ch 中文）')

    args = parser.parse_args()

    # 检查图片目录是否存在
    if not os.path.exists(args.image_dir):
        print(f"错误: 图片目录不存在: {args.image_dir}")
        sys.exit(1)

    try:
        # 创建批量识别器
        recognizer = BatchTableRecognizer(
            output_dir=args.output_dir,
            use_gpu=(args.device == 'gpu'),
            lang=args.lang
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

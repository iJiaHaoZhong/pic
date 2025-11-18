#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量表格识别脚本
使用 PaddleOCR 的表格识别功能对目录中的所有图片进行表格识别
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

# 兼容新旧版本的 PaddleOCR
try:
    from paddleocr import PPStructure, save_structure_res
except ImportError:
    try:
        from paddleocr import PPStructureV3 as PPStructure, save_structure_res
    except ImportError:
        print("错误: 无法导入 PaddleOCR 的表格识别模块")
        print("请确保已安装 PaddleOCR: pip install paddleocr")
        sys.exit(1)


class BatchTableRecognizer:
    """批量表格识别器"""

    def __init__(self,
                 det_model_dir=None,
                 rec_model_dir=None,
                 table_model_dir=None,
                 rec_char_dict_path=None,
                 table_char_dict_path=None,
                 output_dir='output',
                 lang='ch'):
        """
        初始化批量表格识别器

        Args:
            det_model_dir: 文本检测模型路径
            rec_model_dir: 文本识别模型路径
            table_model_dir: 表格结构识别模型路径
            rec_char_dict_path: 文本识别字典路径
            table_char_dict_path: 表格结构识别字典路径
            output_dir: 输出目录
            lang: 语言，'ch'为中文，'en'为英文
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # 初始化 PPStructure
        table_engine_params = {
            'show_log': True,
            'output': output_dir
        }

        # 如果提供了模型路径，则使用自定义模型
        if det_model_dir:
            table_engine_params['det_model_dir'] = det_model_dir
        if rec_model_dir:
            table_engine_params['rec_model_dir'] = rec_model_dir
        if table_model_dir:
            table_engine_params['table_model_dir'] = table_model_dir
        if rec_char_dict_path:
            table_engine_params['rec_char_dict_path'] = rec_char_dict_path
        if table_char_dict_path:
            table_engine_params['table_char_dict_path'] = table_char_dict_path

        # 设置语言
        table_engine_params['lang'] = lang

        print(f"初始化 PPStructure，参数: {table_engine_params}")
        self.table_engine = PPStructure(**table_engine_params)

    def recognize_single_image(self, image_path):
        """
        识别单张图片中的表格

        Args:
            image_path: 图片路径

        Returns:
            识别结果
        """
        try:
            print(f"正在处理: {image_path}")

            # 读取图片
            img = cv2.imread(image_path)
            if img is None:
                print(f"错误: 无法读取图片 {image_path}")
                return None

            # 进行表格识别
            result = self.table_engine(img)

            return result
        except Exception as e:
            print(f"处理 {image_path} 时发生错误: {str(e)}")
            return None

    def save_results(self, image_path, result):
        """
        保存识别结果

        Args:
            image_path: 原始图片路径
            result: 识别结果
        """
        if result is None:
            return

        try:
            # 获取文件名（不含扩展名）
            image_name = Path(image_path).stem

            # 创建该图片的输出目录
            image_output_dir = os.path.join(self.output_dir, image_name)
            os.makedirs(image_output_dir, exist_ok=True)

            # 保存结果
            save_structure_res(result, image_output_dir, image_name)

            # 保存 HTML 文件
            for i, item in enumerate(result):
                if item['type'] == 'table':
                    html_content = item.get('res', {}).get('html', '')
                    if html_content:
                        html_file = os.path.join(image_output_dir, f'{image_name}_table_{i}.html')
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write('<!DOCTYPE html>\n')
                            f.write('<html>\n<head>\n')
                            f.write('<meta charset="UTF-8">\n')
                            f.write(f'<title>{image_name} - Table {i}</title>\n')
                            f.write('<style>\n')
                            f.write('table { border-collapse: collapse; margin: 20px; }\n')
                            f.write('td, th { border: 1px solid #ddd; padding: 8px; }\n')
                            f.write('</style>\n')
                            f.write('</head>\n<body>\n')
                            f.write(f'<h2>{image_name} - Table {i}</h2>\n')
                            f.write(html_content)
                            f.write('\n</body>\n</html>')
                        print(f"  已保存 HTML: {html_file}")

            print(f"  结果已保存至: {image_output_dir}")
        except Exception as e:
            print(f"保存结果时发生错误: {str(e)}")

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

        total_images = len(image_paths)
        print(f"\n找到 {total_images} 张图片")
        print(f"开始批量处理...\n")
        print("=" * 80)

        # 统计信息
        success_count = 0
        fail_count = 0
        start_time = datetime.now()

        # 逐个处理图片
        for idx, image_path in enumerate(image_paths, 1):
            print(f"\n[{idx}/{total_images}] ", end='')

            result = self.recognize_single_image(image_path)

            if result is not None:
                self.save_results(image_path, result)
                success_count += 1
            else:
                fail_count += 1

            print("-" * 80)

        # 计算耗时
        end_time = datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()

        # 打印统计信息
        print("\n" + "=" * 80)
        print("批量处理完成!")
        print(f"总图片数: {total_images}")
        print(f"成功: {success_count}")
        print(f"失败: {fail_count}")
        print(f"总耗时: {elapsed_time:.2f} 秒")
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
    parser = argparse.ArgumentParser(description='批量表格识别工具')
    parser.add_argument('--image_dir', type=str, default='.',
                        help='图片所在目录，默认为当前目录')
    parser.add_argument('--image_pattern', type=str, default='*.jpg',
                        help='图片文件匹配模式，默认为 *.jpg')
    parser.add_argument('--output_dir', type=str, default='output',
                        help='输出目录，默认为 output')
    parser.add_argument('--det_model_dir', type=str, default=None,
                        help='文本检测模型目录')
    parser.add_argument('--rec_model_dir', type=str, default=None,
                        help='文本识别模型目录')
    parser.add_argument('--table_model_dir', type=str, default=None,
                        help='表格结构识别模型目录')
    parser.add_argument('--rec_char_dict_path', type=str, default=None,
                        help='文本识别字典路径')
    parser.add_argument('--table_char_dict_path', type=str, default=None,
                        help='表格结构识别字典路径')
    parser.add_argument('--lang', type=str, default='ch', choices=['ch', 'en'],
                        help='语言类型，ch为中文（默认），en为英文')

    args = parser.parse_args()

    # 检查图片目录是否存在
    if not os.path.exists(args.image_dir):
        print(f"错误: 图片目录不存在: {args.image_dir}")
        sys.exit(1)

    # 创建批量识别器
    recognizer = BatchTableRecognizer(
        det_model_dir=args.det_model_dir,
        rec_model_dir=args.rec_model_dir,
        table_model_dir=args.table_model_dir,
        rec_char_dict_path=args.rec_char_dict_path,
        table_char_dict_path=args.table_char_dict_path,
        output_dir=args.output_dir,
        lang=args.lang
    )

    # 执行批量识别
    stats = recognizer.batch_recognize(args.image_dir, args.image_pattern)

    return 0 if stats['fail'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

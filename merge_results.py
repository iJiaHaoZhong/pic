#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并表格识别结果
将多个 HTML 表格合并成一份 Excel 文件
"""

import os
import sys
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def parse_html_table(html_file):
    """
    解析 HTML 文件中的表格

    Args:
        html_file: HTML 文件路径

    Returns:
        pandas DataFrame 或 None
    """
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table')

        if table is None:
            return None

        # 提取所有行
        rows = []
        for tr in table.find_all('tr'):
            cells = []
            for td in tr.find_all(['td', 'th']):
                # 获取单元格文本，处理换行
                text = td.get_text(strip=True)
                cells.append(text)
            if cells:
                rows.append(cells)

        if not rows:
            return None

        # 创建 DataFrame
        # 假设第一行是表头
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0] if rows[0] else None)
        else:
            df = pd.DataFrame(rows)

        return df

    except Exception as e:
        print(f"  ⚠ 解析失败 {html_file}: {str(e)}")
        return None


def merge_tables(output_dir, merged_file='merged_results.xlsx'):
    """
    合并所有表格结果

    Args:
        output_dir: 输出目录（包含各个图片的识别结果子目录）
        merged_file: 合并后的文件名
    """
    print("=" * 80)
    print("  合并表格识别结果")
    print("=" * 80)
    print(f"\n输入目录: {output_dir}")
    print(f"输出文件: {merged_file}\n")

    if not os.path.exists(output_dir):
        print(f"错误: 目录不存在 {output_dir}")
        return False

    # 查找所有 HTML 文件
    html_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))

    # 按文件名排序
    html_files.sort()

    print(f"找到 {len(html_files)} 个 HTML 文件\n")

    if not html_files:
        print("未找到任何 HTML 文件！")
        return False

    # 合并所有表格
    all_dfs = []
    success_count = 0

    for idx, html_file in enumerate(html_files, 1):
        file_name = Path(html_file).stem
        print(f"[{idx}/{len(html_files)}] 处理: {file_name}")

        df = parse_html_table(html_file)

        if df is not None and not df.empty:
            # 添加来源列（可选）
            # df['来源文件'] = file_name
            all_dfs.append(df)
            success_count += 1
            print(f"  ✓ 成功，{len(df)} 行")
        else:
            print(f"  ⚠ 跳过（空表格）")

    if not all_dfs:
        print("\n没有成功解析任何表格！")
        return False

    # 合并所有 DataFrame
    print(f"\n正在合并 {len(all_dfs)} 个表格...")

    try:
        # 尝试垂直合并（假设所有表格结构相同）
        merged_df = pd.concat(all_dfs, ignore_index=True)

        # 去除完全重复的行
        original_rows = len(merged_df)
        merged_df = merged_df.drop_duplicates()
        removed_rows = original_rows - len(merged_df)

        if removed_rows > 0:
            print(f"  移除 {removed_rows} 行重复数据")

        # 保存到 Excel
        output_path = os.path.join(output_dir, merged_file)
        merged_df.to_excel(output_path, index=False, engine='openpyxl')

        print("\n" + "=" * 80)
        print("合并完成！")
        print("=" * 80)
        print(f"成功处理: {success_count}/{len(html_files)} 个文件")
        print(f"总行数: {len(merged_df)}")
        print(f"总列数: {len(merged_df.columns)}")
        print(f"输出文件: {output_path}")
        print("=" * 80)

        return True

    except Exception as e:
        print(f"\n合并失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='合并表格识别结果 - 将多个 HTML 表格合并成一份 Excel',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 合并 output 目录的结果
  python merge_results.py --input_dir output

  # 指定输出文件名
  python merge_results.py --input_dir output --output merged.xlsx
        """
    )

    parser.add_argument('--input_dir', type=str, default='output',
                        help='识别结果目录（默认: output）')
    parser.add_argument('--output', type=str, default='merged_results.xlsx',
                        help='合并后的文件名（默认: merged_results.xlsx）')

    args = parser.parse_args()

    try:
        success = merge_tables(args.input_dir, args.output)
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n用户中断")
        return 1
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

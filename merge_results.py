#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并表格识别结果
将多个 HTML/Excel 表格合并成一份 Excel 文件
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

        # 创建 DataFrame（不使用第一行作为表头，因为 OCR 结果通常不准确）
        df = pd.DataFrame(rows)

        return df

    except Exception as e:
        print(f"  ⚠ 解析 HTML 失败 {html_file}: {str(e)}")
        return None


def parse_excel_table(excel_file):
    """
    解析 Excel 文件中的表格

    Args:
        excel_file: Excel 文件路径

    Returns:
        pandas DataFrame 或 None
    """
    try:
        # 读取 Excel，不使用第一行作为表头
        df = pd.read_excel(excel_file, header=None)
        return df
    except Exception as e:
        print(f"  ⚠ 解析 Excel 失败 {excel_file}: {str(e)}")
        return None


def merge_tables(input_dir, merged_file='merged_results.xlsx', skip_first_row=True):
    """
    合并所有表格结果

    Args:
        input_dir: 输入目录（包含各个图片的识别结果）
        merged_file: 合并后的文件名
        skip_first_row: 是否跳过每个表格的第一行（通常是 OCR 识别错误的表头）
    """
    print("=" * 80)
    print("  合并表格识别结果")
    print("=" * 80)
    print(f"\n输入目录: {input_dir}")
    print(f"输出文件: {merged_file}\n")

    if not os.path.exists(input_dir):
        print(f"错误: 目录不存在 {input_dir}")
        return False

    # 查找所有表格文件（HTML 和 Excel）
    table_files = []

    # 搜索 HTML 文件
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.html'):
                table_files.append(('html', os.path.join(root, file)))
            elif file.endswith(('.xlsx', '.xls')):
                table_files.append(('excel', os.path.join(root, file)))

    # 也检查当前目录下的 Excel 文件
    for file in os.listdir(input_dir):
        if file.endswith(('.xlsx', '.xls')):
            filepath = os.path.join(input_dir, file)
            if ('excel', filepath) not in table_files:
                table_files.append(('excel', filepath))

    # 按文件名排序
    table_files.sort(key=lambda x: x[1])

    print(f"找到 {len(table_files)} 个表格文件\n")

    if not table_files:
        print("未找到任何表格文件！")
        return False

    # 合并所有表格
    all_dfs = []
    success_count = 0

    for idx, (file_type, table_file) in enumerate(table_files, 1):
        file_name = Path(table_file).stem
        print(f"[{idx}/{len(table_files)}] 处理: {file_name}")

        if file_type == 'html':
            df = parse_html_table(table_file)
        else:
            df = parse_excel_table(table_file)

        if df is not None and not df.empty:
            # 跳过第一行（通常是 OCR 识别错误的表头）
            if skip_first_row and len(df) > 1:
                df = df.iloc[1:].reset_index(drop=True)

            # 过滤掉全空的行
            df = df.dropna(how='all')

            if not df.empty:
                all_dfs.append(df)
                success_count += 1
                print(f"  ✓ 成功，{len(df)} 行")
            else:
                print(f"  ⚠ 跳过（空表格）")
        else:
            print(f"  ⚠ 跳过（无法解析）")

    if not all_dfs:
        print("\n没有成功解析任何表格！")
        return False

    # 合并所有 DataFrame
    print(f"\n正在合并 {len(all_dfs)} 个表格...")

    try:
        # 统一列数（以最大列数为准）
        max_cols = max(len(df.columns) for df in all_dfs)

        # 对齐列数
        aligned_dfs = []
        for df in all_dfs:
            if len(df.columns) < max_cols:
                # 添加空列
                for i in range(len(df.columns), max_cols):
                    df[i] = None
            aligned_dfs.append(df)

        # 垂直合并
        merged_df = pd.concat(aligned_dfs, ignore_index=True)

        # 设置有意义的列名
        column_names = [
            '编号', 'ID信息', '分类1', '分类2', '产品名称(韩文)',
            '产品编码', '数据1', '数据2', '数据3', '数据4', '数据5', '数据6'
        ]

        # 根据实际列数调整列名
        if len(merged_df.columns) <= len(column_names):
            merged_df.columns = column_names[:len(merged_df.columns)]
        else:
            # 超出部分用默认列名
            new_cols = column_names + [f'列{i}' for i in range(len(column_names), len(merged_df.columns))]
            merged_df.columns = new_cols

        # 去除完全重复的行
        original_rows = len(merged_df)
        merged_df = merged_df.drop_duplicates()
        removed_rows = original_rows - len(merged_df)

        if removed_rows > 0:
            print(f"  移除 {removed_rows} 行重复数据")

        # 保存到 Excel
        output_path = merged_file if os.path.isabs(merged_file) else os.path.join(input_dir, merged_file)
        merged_df.to_excel(output_path, index=False, engine='openpyxl')

        print("\n" + "=" * 80)
        print("合并完成！")
        print("=" * 80)
        print(f"成功处理: {success_count}/{len(table_files)} 个文件")
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
        description='合并表格识别结果 - 将多个 HTML/Excel 表格合并成一份',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 合并 output 目录的结果
  python merge_results.py --input_dir output

  # 指定输出文件名
  python merge_results.py --input_dir output --output merged.xlsx

  # 不跳过第一行
  python merge_results.py --input_dir output --keep_header
        """
    )

    parser.add_argument('--input_dir', type=str, default='output',
                        help='识别结果目录（默认: output）')
    parser.add_argument('--output', type=str, default='merged_results.xlsx',
                        help='合并后的文件名（默认: merged_results.xlsx）')
    parser.add_argument('--keep_header', action='store_true',
                        help='保留每个表格的第一行（默认跳过，因为通常是 OCR 错误）')

    args = parser.parse_args()

    try:
        success = merge_tables(
            args.input_dir,
            args.output,
            skip_first_row=not args.keep_header
        )
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

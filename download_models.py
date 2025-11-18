#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型下载脚本（Python 版本）
用于下载 PaddleOCR 表格识别所需的模型
"""

import os
import sys
import tarfile
import urllib.request
from pathlib import Path


class ModelDownloader:
    """模型下载器"""

    # 模型 URL 配置
    MODELS = {
        'ch': {
            'det': {
                'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_det_infer.tar',
                'name': 'PP-OCRv3_mobile_det_infer'
            },
            'rec': {
                'url': 'https://paddle-model-ecology.bj.bcebos.com/paddlex/official_inference_model/paddle3.0.0/PP-OCRv3_mobile_rec_infer.tar',
                'name': 'PP-OCRv3_mobile_rec_infer'
            },
            'table': {
                'url': 'https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/ch_ppstructure_mobile_v2.0_SLANet_infer.tar',
                'name': 'ch_ppstructure_mobile_v2.0_SLANet_infer'
            }
        },
        'en': {
            'det': {
                'url': 'https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_det_infer.tar',
                'name': 'en_ppocr_mobile_v2.0_table_det_infer'
            },
            'rec': {
                'url': 'https://paddleocr.bj.bcebos.com/dygraph_v2.0/table/en_ppocr_mobile_v2.0_table_rec_infer.tar',
                'name': 'en_ppocr_mobile_v2.0_table_rec_infer'
            },
            'table': {
                'url': 'https://paddleocr.bj.bcebos.com/ppstructure/models/slanet/paddle3.0b2/en_ppstructure_mobile_v2.0_SLANet_infer.tar',
                'name': 'en_ppstructure_mobile_v2.0_SLANet_infer'
            }
        }
    }

    def __init__(self, models_dir='models'):
        """
        初始化模型下载器

        Args:
            models_dir: 模型保存目录
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)

    def download_file(self, url, filename):
        """
        下载文件（带进度显示）

        Args:
            url: 下载链接
            filename: 保存的文件名
        """
        filepath = self.models_dir / filename

        if filepath.exists():
            print(f"✓ 文件已存在，跳过下载: {filename}")
            return filepath

        print(f"开始下载: {filename}")
        print(f"URL: {url}")

        try:
            def progress_hook(block_num, block_size, total_size):
                """下载进度回调"""
                downloaded = block_num * block_size
                if total_size > 0:
                    percent = min(downloaded * 100.0 / total_size, 100)
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    print(f"\r  进度: {percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f} MB)", end='')
                else:
                    downloaded_mb = downloaded / (1024 * 1024)
                    print(f"\r  已下载: {downloaded_mb:.1f} MB", end='')

            urllib.request.urlretrieve(url, filepath, progress_hook)
            print()  # 换行
            print(f"✓ 下载完成: {filename}")
            return filepath

        except Exception as e:
            print(f"\n✗ 下载失败: {filename}")
            print(f"  错误: {str(e)}")
            if filepath.exists():
                filepath.unlink()
            return None

    def extract_tar(self, tar_path):
        """
        解压 tar 文件

        Args:
            tar_path: tar 文件路径
        """
        print(f"开始解压: {tar_path.name}")

        try:
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(self.models_dir)
            print(f"✓ 解压完成: {tar_path.name}")
            return True
        except Exception as e:
            print(f"✗ 解压失败: {tar_path.name}")
            print(f"  错误: {str(e)}")
            return False

    def download_model(self, lang, model_type):
        """
        下载指定模型

        Args:
            lang: 语言类型 ('ch' 或 'en')
            model_type: 模型类型 ('det', 'rec', 或 'table')
        """
        model_info = self.MODELS[lang][model_type]
        url = model_info['url']
        filename = os.path.basename(url)

        print(f"\n{'=' * 60}")
        print(f"下载 {lang.upper()} - {model_type.upper()} 模型")
        print(f"{'=' * 60}")

        # 下载文件
        tar_path = self.download_file(url, filename)
        if tar_path is None:
            return False

        # 解压文件
        if not self.extract_tar(tar_path):
            return False

        print()
        return True

    def download_lang_models(self, lang):
        """
        下载指定语言的所有模型

        Args:
            lang: 语言类型 ('ch' 或 'en')
        """
        lang_name = '中文' if lang == 'ch' else '英文'
        print(f"\n开始下载{lang_name}模型...")

        success = True
        for model_type in ['det', 'rec', 'table']:
            if not self.download_model(lang, model_type):
                success = False

        if success:
            print(f"\n✓ {lang_name}模型下载完成！")
        else:
            print(f"\n✗ {lang_name}模型下载过程中出现错误")

        return success

    def print_usage(self, langs):
        """
        打印使用说明

        Args:
            langs: 已下载的语言列表
        """
        print("\n" + "=" * 60)
        print("模型下载完成！")
        print(f"模型保存在: {self.models_dir.absolute()}")
        print("\n现在可以使用以下命令运行批量识别：\n")

        if 'ch' in langs:
            print("# 中文表格识别")
            print("python batch_table_recognition.py \\")
            print("    --det_model_dir models/PP-OCRv3_mobile_det_infer \\")
            print("    --rec_model_dir models/PP-OCRv3_mobile_rec_infer \\")
            print("    --table_model_dir models/ch_ppstructure_mobile_v2.0_SLANet_infer \\")
            print("    --lang ch")
            print()

        if 'en' in langs:
            print("# 英文表格识别")
            print("python batch_table_recognition.py \\")
            print("    --det_model_dir models/en_ppocr_mobile_v2.0_table_det_infer \\")
            print("    --rec_model_dir models/en_ppocr_mobile_v2.0_table_rec_infer \\")
            print("    --table_model_dir models/en_ppstructure_mobile_v2.0_SLANet_infer \\")
            print("    --lang en")
            print()

        print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("  PaddleOCR 表格识别模型下载脚本（Python 版本）")
    print("=" * 60)
    print()
    print("请选择要下载的模型类型：")
    print("1) 中文模型")
    print("2) 英文模型")
    print("3) 两者都下载")
    print()

    try:
        choice = input("请输入选项 (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n\n已取消")
        return 1

    if choice not in ['1', '2', '3']:
        print("✗ 无效的选项，请输入 1、2 或 3")
        return 1

    # 创建下载器
    downloader = ModelDownloader()

    # 根据用户选择下载模型
    downloaded_langs = []

    if choice == '1':
        if downloader.download_lang_models('ch'):
            downloaded_langs.append('ch')
    elif choice == '2':
        if downloader.download_lang_models('en'):
            downloaded_langs.append('en')
    elif choice == '3':
        if downloader.download_lang_models('ch'):
            downloaded_langs.append('ch')
        if downloader.download_lang_models('en'):
            downloaded_langs.append('en')

    # 打印使用说明
    if downloaded_langs:
        downloader.print_usage(downloaded_langs)
        return 0
    else:
        print("\n✗ 下载失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())

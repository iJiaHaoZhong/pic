#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例脚本
演示如何在代码中使用 BatchTableRecognizer
"""

from batch_table_recognition import BatchTableRecognizer


def example_1_basic_usage():
    """
    示例 1: 基本使用（使用在线模型）
    """
    print("=" * 60)
    print("示例 1: 基本使用（使用在线模型）")
    print("=" * 60)

    # 创建识别器（会自动下载模型）
    recognizer = BatchTableRecognizer(
        output_dir='output_example1',
        lang='ch'  # 中文
    )

    # 批量识别当前目录的所有图片
    stats = recognizer.batch_recognize(
        image_dir='.',
        image_pattern='*.jpg'
    )

    print(f"\n处理完成，成功: {stats['success']}, 失败: {stats['fail']}")


def example_2_custom_models():
    """
    示例 2: 使用本地模型
    """
    print("\n" + "=" * 60)
    print("示例 2: 使用本地模型")
    print("=" * 60)

    # 使用本地下载的模型
    recognizer = BatchTableRecognizer(
        det_model_dir='models/PP-OCRv3_mobile_det_infer',
        rec_model_dir='models/PP-OCRv3_mobile_rec_infer',
        table_model_dir='models/ch_ppstructure_mobile_v2.0_SLANet_infer',
        output_dir='output_example2',
        lang='ch'
    )

    # 批量识别
    stats = recognizer.batch_recognize(
        image_dir='.',
        image_pattern='*.jpg'
    )

    print(f"\n处理完成，成功: {stats['success']}, 失败: {stats['fail']}")


def example_3_single_image():
    """
    示例 3: 识别单张图片
    """
    print("\n" + "=" * 60)
    print("示例 3: 识别单张图片")
    print("=" * 60)

    # 创建识别器
    recognizer = BatchTableRecognizer(
        output_dir='output_example3',
        lang='ch'
    )

    # 识别单张图片
    result = recognizer.recognize_single_image('微信图片_20251118231557_1085_15.jpg')

    if result:
        print("\n识别成功！结果:")
        for i, item in enumerate(result):
            print(f"\n项目 {i + 1}:")
            print(f"  类型: {item.get('type', 'unknown')}")
            if item['type'] == 'table':
                res = item.get('res', {})
                print(f"  表格行数: {len(res.get('cell_bbox', []))}")
                print(f"  HTML 长度: {len(res.get('html', ''))}")

        # 保存结果
        recognizer.save_results('微信图片_20251118231557_1085_15.jpg', result)
    else:
        print("\n识别失败")


def example_4_english_table():
    """
    示例 4: 英文表格识别
    """
    print("\n" + "=" * 60)
    print("示例 4: 英文表格识别")
    print("=" * 60)

    # 创建英文识别器
    recognizer = BatchTableRecognizer(
        output_dir='output_example4',
        lang='en'  # 英文
    )

    # 批量识别
    stats = recognizer.batch_recognize(
        image_dir='.',
        image_pattern='*.png'  # 假设英文表格是 PNG 格式
    )

    print(f"\n处理完成，成功: {stats['success']}, 失败: {stats['fail']}")


def main():
    """主函数"""
    print("批量表格识别使用示例\n")
    print("请选择要运行的示例：")
    print("1) 基本使用（使用在线模型）")
    print("2) 使用本地模型")
    print("3) 识别单张图片")
    print("4) 英文表格识别")
    print("5) 运行所有示例")
    print()

    try:
        choice = input("请输入选项 (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n\n已取消")
        return 1

    examples = {
        '1': example_1_basic_usage,
        '2': example_2_custom_models,
        '3': example_3_single_image,
        '4': example_4_english_table,
    }

    if choice == '5':
        # 运行所有示例
        for func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"\n示例运行出错: {str(e)}")
                import traceback
                traceback.print_exc()
    elif choice in examples:
        # 运行选定的示例
        try:
            examples[choice]()
        except Exception as e:
            print(f"\n示例运行出错: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("无效的选项")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())

# Develped by ssYanhuo.

import math
import fitz
from tqdm import tqdm
import numpy as np
import os


def is_colour_page(page, threshold):
    pixel_map = page.get_pixmap()

    if pixel_map.n <= 1:
        return False

    pixel_matrix = np.frombuffer(pixel_map.samples, dtype=np.uint8).reshape(pixel_map.h, pixel_map.w, pixel_map.n)
    red_channel = pixel_matrix[:, :, 0]
    green_channel = pixel_matrix[:, :, 1]
    blue_channel = pixel_matrix[:, :, 2]

    return (
            (np.abs(red_channel - green_channel) > threshold).any() or
            (np.abs(red_channel - blue_channel) > threshold).any() or
            (np.abs(green_channel - blue_channel) > threshold).any()
    )


def generate_action_list(input_list):
    result = []
    current = input_list[0]
    c = 1
    for state_index in range(1, len(input_list)):
        if input_list[state_index] == current:
            c += 1
        else:
            result.append({'colour': current, 'count': c})
            current = input_list[state_index]
            c = 1
    result.append({'colour': current, 'count': c})
    return result


if __name__ == '__main__':

    print('▄▄▄▄▄▄▄ ▄▄▄▄▄▄▄ ▄▄   ▄▄ ▄▄▄▄▄▄ ▄▄    ▄ ▄▄   ▄▄ ▄▄   ▄▄ ▄▄▄▄▄▄▄   ')
    print('█       █       █  █ █  █      █  █  █ █  █ █  █  █ █  █       █ ')
    print('█  ▄▄▄▄▄█  ▄▄▄▄▄█  █▄█  █  ▄   █   █▄█ █  █▄█  █  █ █  █   ▄   █ ')
    print('█ █▄▄▄▄▄█ █▄▄▄▄▄█       █ █▄█  █       █       █  █▄█  █  █ █  █ ')
    print('█▄▄▄▄▄  █▄▄▄▄▄  █▄     ▄█      █  ▄    █   ▄   █       █  █▄█  █ ')
    print('▄▄▄▄▄█  █▄▄▄▄▄█ █ █   █ █  ▄   █ █ █   █  █ █  █       █       █ ')
    print('█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█ █▄▄▄█ █▄█ █▄▄█▄█  █▄▄█▄▄█ █▄▄█▄▄▄▄▄▄▄█▄▄▄▄▄▄▄█ ')


    print()
    print('Developed by ssYanhuo.')
    print('Star on GitHub: ' + 'https://github.com/ssYanhuo/pdf-colour-split')
    print()

    input_file_path = input('要拆分的文件路径：')
    output_file_path = input('输出文件夹路径：')

    double_page = input('单面打印 (s) OR 双面打印 (d)？').lower() != 's'
    detect_threshold = int(input('检测阈值 (10)：') or 10)

    print()
    print('开始拆分')
    print('拆分文件：' + input_file_path)
    print('输出文件夹：' + output_file_path)
    print('打印方式：' + '双面打印' if double_page else '单面打印')
    print('检测阈值：' + str(detect_threshold))

    input_pdf = fitz.open(input_file_path)
    output_grayscale_pdf = fitz.open()
    output_colour_pdf = fitz.open()

    count = {'total': input_pdf.page_count,
             'print': math.ceil(input_pdf.page_count / 2 if double_page else input_pdf.page_count),
             'grayscale': 0,
             'colour': 0}
    print('总页数：' + str(count['total']))
    print('打印张数：' + str(count['print']))

    colour_state_list = []
    colour_print_state_list = []
    print()

    for i in tqdm(range(0, count['total'], 2 if double_page else 1)):
        unit_pages = [input_pdf[i]]
        if double_page and i + 1 < input_pdf.page_count:
            unit_pages.append(input_pdf[i + 1])

        has_colour_page = False

        for page in unit_pages:
            if is_colour_page(page, detect_threshold):
                colour_state_list.append(True)
                has_colour_page = True
            else:
                colour_state_list.append(False)

        for page in unit_pages:
            if has_colour_page:
                output_colour_pdf.insert_pdf(input_pdf, from_page=page.number, to_page=page.number)
            else:
                output_grayscale_pdf.insert_pdf(input_pdf, from_page=page.number, to_page=page.number)

        if has_colour_page:
            colour_print_state_list.append(True)
            count['colour'] += 1
        else:
            colour_print_state_list.append(False)
            count['grayscale'] += 1

    print()
    output_grayscale_path = '{}{}{}.pdf'.format(
        os.path.join(output_file_path, os.path.splitext(os.path.basename(input_file_path))[0]),
        '_grayscale',
        '_double' if double_page else '_single')

    print('写入文件（黑白）：' + output_grayscale_path)
    output_grayscale_pdf.save(output_grayscale_path)

    output_colour_path = '{}{}{}.pdf'.format(
        os.path.join(output_file_path, os.path.splitext(os.path.basename(input_file_path))[0]),
        '_colour',
        '_double' if double_page else '_single')
    print('写入文件（彩色）：' + output_colour_path)
    output_colour_pdf.save(output_colour_path)

    print()
    print('拆分完成！')
    print('\033[0;33m务必检查拆分后的文件，如果拆分错误，请修改检测阈值\033[0m')

    grayscale_page_number_list = []
    colour_page_number_list = []

    for index, state in enumerate(colour_state_list):
        if state:
            colour_page_number_list.append(str(index + 1))
        else:
            grayscale_page_number_list.append(str(index + 1))

    print('黑白页（共打印 {} 张）页码：\n{}'.format(count['grayscale'], ', '.join(grayscale_page_number_list)))
    print('彩色页（共打印 {} 张）页码：\n{}'.format(count['colour'], ', '.join(colour_page_number_list)))

    action_list = generate_action_list(colour_print_state_list)

    print()
    print('按照以下方法把打印好的文稿重新组合成原文稿（可复制保存此段备用）：')
    print('将打印好的黑白与彩色文稿按页码从小到大，自上而下排序（直接拿起打印好的文稿，正面朝上即可）')
    print('组合时拿取指定张数的黑白或彩色文稿，一起翻面扣放在整理好的文稿上面')
    print()

    for index, action in enumerate(action_list):
        print('{}{}. 取 {} 张 {} 文稿，一起翻面扣放在整理好的文稿上面{}'.format(
            '\033[0;32m' if action['colour'] else '\033[0;34m',
            index + 1,
            action['count'],
            '彩色' if action['colour'] else '黑白',
            '\033[0m'
        ))

    print()
    print('整理完成！')

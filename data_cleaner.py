import chardet
import re
import csv

# エンコーディングを検出する関数
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

# ファイルを指定されたエンコーディングから UTF-8 に変換する関数
def convert_to_utf8(file_path, output_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 制御文字を除去する関数
def remove_control_chars(s):
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s)

# ダブルクォートを除去する関数
def remove_extra_quotes(s):
    return s.replace('""', '').replace('"', '').strip()

# CSVファイルをクリーンアップする関数
def clean_csv(file_path, output_path, encoding):
    with open(file_path, 'r', encoding=encoding) as f:
        lines = f.readlines()

    clean_lines = []
    for line in lines:
        clean_line = remove_control_chars(line)
        clean_line = remove_extra_quotes(clean_line)
        clean_lines.append(clean_line)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["date", "time", "weight"])
        for line in clean_lines:
            csv_writer.writerow(line.split(','))

# CSVファイルの形式を確認する関数
def check_csv_format(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f)
        for i, row in enumerate(csv_reader):
            print(f"Row {i}: {row}")

# メイン処理
def main():
    input_file_path = "./data/weight_data_utf8.csv"
    temp_file_path = "./data/weight_data_utf8_tmp.csv"
    clean_file_path = "./data/weight_data_clean.csv"

    # エンコーディングを検出
    encoding = detect_encoding(input_file_path)
    print(f"Detected encoding: {encoding}")

    # UTF-8 に変換
    convert_to_utf8(input_file_path, temp_file_path, encoding)

    # CSVファイルをクリーンアップ
    clean_csv(temp_file_path, clean_file_path, "utf-8")

    # クリーンアップされたCSVファイルの形式を確認
    check_csv_format(clean_file_path)

if __name__ == "__main__":
    main()

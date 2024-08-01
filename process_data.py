import csv
import random
import math
import re

from datetime import datetime

# 不要な文字を削除する関数
def clean_value(value):
    return re.sub(r'[^\d.]', '', value)  # 数字とピリオド以外の文字を削除

def read_csv(file_path):
    data = []
    with open(file_path, "r", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        headers = next(csv_reader)  # ヘッダー行をスキップ
        for row in csv_reader:
            print(f"Raw date string: {row[0].strip()}")  # デバッグ用プリント文
            try:
                date = datetime.strptime(row[0].strip(), "%m/%d/%y")
            except ValueError as e:
                print(f"Error parsing date: {e}")
                continue  # エラーが発生した場合、その行をスキップ
            data.append({
                "date": date,  # 日付の前後のスペースを削除
                "time": row[1].strip(),  # 時刻データを保持
                "weight": float(clean_value(row[2].strip())) if row[2].strip() else None,
                "waist": float(clean_value(row[3].strip())) if len(row) > 3 and row[3].strip() else None,
                "calorie_intake": float(clean_value(row[4].strip())) if len(row) > 4 and row[4].strip() else 1800,
                "calorie_burn": float(clean_value(row[5].strip())) if len(row) > 5 and row[5].strip() else 600
            })
    return data

# 過去の変動率を計算する関数
def calculate_rate_of_change(data, key):
    rate_of_change = []
    for i in range(1, len(data)):
        if data[i][key] is not None and data[i-1][key] is not None:
            change = (data[i][key] - data[i-1][key]) / data[i-1][key]
            rate_of_change.append(change)
    if len(rate_of_change) == 0:
        raise ValueError(f"No valid rate of change data for key: {key}")
    return rate_of_change

# 欠損データの補完関数（変動率を基に補完）
def fill_missing_data(data, key, rate_of_change):
    avg_rate = sum(rate_of_change) / len(rate_of_change)
    std_rate = math.sqrt(sum((x - avg_rate) ** 2 for x in rate_of_change) / len(rate_of_change))

    for i in range(len(data)):
        if data[i][key] is None:
            if i == 0:
                continue
            else:
                previous_value = data[i-1][key]
                random_variation = random.gauss(avg_rate, std_rate)
                data[i][key] = previous_value * (1 + random_variation)
    return data

# 週ごとの平均データを計算する関数
def calculate_weekly_averages(data):
    weekly_data = []
    current_week = []
    current_start_date = data[0]["date"]

    for entry in data:
        if (entry["date"] - current_start_date).days < 7:
            current_week.append(entry)
        else:
            weekly_data.append(calculate_average(current_week))
            current_week = [entry]
            current_start_date = entry["date"]
    if current_week:
        weekly_data.append(calculate_average(current_week))

    return weekly_data

def calculate_average(entries):
    date = entries[0]["date"]
    avg_weight = sum(entry["weight"] for entry in entries) / len(entries)
    avg_waist = sum(entry["waist"] for entry in entries) / len(entries)
    avg_calorie_intake = sum(entry["calorie_intake"] for entry in entries) / len(entries)
    avg_calorie_burn = sum(entry["calorie_burn"] for entry in entries) / len(entries)
    return {
        "date": date,
        "weight": avg_weight,
        "waist": avg_waist,
        "calorie_intake": avg_calorie_intake,
        "calorie_burn": avg_calorie_burn
    }

# CSVファイルにデータを書き出す関数
def write_to_csv(data, file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        csv_writer = csv.writer(csvfile)
        header = ["Date", "Weight(lbs)", "Waist(cm)", "Calorie Intake(kcal)", "Burn(kcal)"]
        csv_writer.writerow(header)
        for entry in data:
            row = [
                entry["date"].strftime("%d/%m/%y"),
                entry["weight"],
                entry["waist"],
                entry["calorie_intake"],
                entry["calorie_burn"]
            ]
            csv_writer.writerow(row)

# データをマージする関数
def merge_data(weight_data, waist_data):
    merged_data = []
    for weight_entry in weight_data:
        for waist_entry in waist_data:
            if weight_entry["date"] == waist_entry["date"]:
                merged_data.append({
                    "date": weight_entry["date"],
                    "weight": weight_entry["weight"],
                    "waist": waist_entry["waist"],
                    "calorie_intake": weight_entry["calorie_intake"],
                    "calorie_burn": weight_entry["calorie_burn"]
                })
    return merged_data

# メイン処理
def main():
    weight_data = read_csv("./data/weight_data_clean.csv")
    waist_data = read_csv("./data/waist_data_utf8.csv")
    
    # デバッグ用プリント文
    print("Weight Data:")
    for entry in weight_data:
        print(entry)
    
    print("Waist Data:")
    for entry in waist_data:
        print(entry)

    try:
        weight_rate_of_change = calculate_rate_of_change(weight_data, "weight")
        waist_rate_of_change = calculate_rate_of_change(waist_data, "waist")
    except ValueError as e:
        print(e)
        return

    filled_weights = fill_missing_data(weight_data, "weight", weight_rate_of_change)
    filled_waist = fill_missing_data(waist_data, "waist", waist_rate_of_change)
    
    merged_data = merge_data(filled_weights, filled_waist)
    weekly_averages = calculate_weekly_averages(merged_data)
    
    # マージされたデータの保存先ファイル
    write_to_csv(weekly_averages, "./tmp/weekly_averages.csv")
    print("Data written to CSV successfully.")

if __name__ == "__main__":
    main()

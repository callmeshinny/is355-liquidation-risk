"""
Kiểm tra dữ liệu FinSurvival - task Borrow -> Liquidated.
Chạy từ thư mục gốc của repo:  python inspect_borrow_liquidated.py
Cần cài: pip install pyreadr pandas pyarrow
"""
import glob
import os

import pandas as pd
import pyreadr

BASE = os.path.join("Data", "Survival_Data", "Borrow")


def read_rds(path):
    return next(iter(pyreadr.read_r(path).values()))


def load_parts(folder, prefix):
    files = glob.glob(os.path.join(BASE, folder, f"{prefix}_*.rds"))
    files.sort(key=lambda p: int(p.rsplit("_", 1)[1].split(".")[0]))
    parts = []
    for f in files:
        df = read_rds(f)
        print(f"  {f}: {df.shape}")
        parts.append(df)
    return pd.concat(parts, ignore_index=True)


# 1. Tìm thư mục nhãn liquidated
subdirs = sorted(d for d in os.listdir(BASE) if os.path.isdir(os.path.join(BASE, d)))
print("Các thư mục trong Borrow:", subdirs)
liq = [d for d in subdirs if "iquidat" in d.lower()]
if not liq:
    raise SystemExit("Không thấy thư mục liquidated -> kiểm tra lại đã sparse-checkout đủ chưa.")
LIQ = liq[0]
print("Dùng thư mục nhãn:", LIQ)

# 2. Load X (ghép các phần) và y
print("\nĐang load X_train...")
X_train = load_parts("X_train", "X_train")
print("Đang load X_test...")
X_test = load_parts("X_test", "X_test")
y_train = read_rds(os.path.join(BASE, LIQ, "y_train.rds"))
y_test = read_rds(os.path.join(BASE, LIQ, "y_test.rds"))

# 3. In cấu trúc
print("\n=== KÍCH THƯỚC ===")
print("X_train:", X_train.shape, "| y_train:", y_train.shape)
print("X_test :", X_test.shape, "| y_test :", y_test.shape)

print("\n=== CỘT CỦA y ===")
print(y_train.dtypes)
print(y_train.head())
print(y_train.describe(include="all").T)

print(f"\n=== CỘT CỦA X ({X_train.shape[1]} cột) ===")
print(X_train.columns.tolist())
print(X_train.dtypes.value_counts())

# 4. Kiểm tra X và y có khớp hàng không
print("\n=== KHỚP HÀNG X - y ===")
print("Số dòng train khớp:", len(X_train) == len(y_train))
print("Số dòng test  khớp:", len(X_test) == len(y_test))
common = set(X_train.columns) & set(y_train.columns)
print("Cột chung giữa X và y (có thể là khóa nối):", common or "không có")

# 5. Lưu sang parquet để lần sau load nhanh
try:
    os.makedirs("processed", exist_ok=True)
    X_train.to_parquet("processed/X_train.parquet")
    X_test.to_parquet("processed/X_test.parquet")
    y_train.to_parquet("processed/y_train_liquidated.parquet")
    y_test.to_parquet("processed/y_test_liquidated.parquet")
    print("\nĐã lưu bản parquet vào thư mục processed/")
except Exception as e:
    print("\nKhông lưu được parquet (cài pyarrow nếu muốn):", e)
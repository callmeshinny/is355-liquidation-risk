"""
Tạo Hình 2 và Hình 3 cho báo cáo Tuần 3: 5 bản ghi mẫu + biểu đồ phân bố nhãn của mỗi dataset.

Chạy trong thư mục D:\\BlockChain\\DMLR_DeFi_Survival_Benchmark (cần đã chạy notebook EDA, và có file Taiwan trong taiwan\\):
    python make_dataset_figures.py
Kết quả: figures\\fig2_dataset1.png, figures\\fig3_dataset2.png  -> chèn vào ô hình trong file Word.
"""
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

os.makedirs("figures", exist_ok=True)
DAY = 86400


def make_figure(sample, split_names, counts, rates, title, ylab, color, out):
    fig = plt.figure(figsize=(10, 6.2), dpi=200)
    ax_t = fig.add_axes([0.02, 0.56, 0.96, 0.40]); ax_t.axis("off")
    ax_t.set_title("(a) Sample records", loc="left", fontsize=11)
    tb = ax_t.table(cellText=sample.values, colLabels=sample.columns, loc="center", cellLoc="center")
    tb.auto_set_font_size(False); tb.set_fontsize(8); tb.scale(1, 1.5)
    for (r, _), cell in tb.get_celld().items():
        if r == 0:
            cell.set_facecolor("#0D172C"); cell.set_text_props(color="white", weight="bold")

    ax = fig.add_axes([0.08, 0.08, 0.88, 0.38])
    bars = ax.bar(split_names, rates, color=color, width=0.5)
    for b, n, p in zip(bars, counts, rates):
        ax.text(b.get_x() + b.get_width() / 2, p, f"{p:.2f}%  (n = {n:,})", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, max(rates) * 1.3)
    ax.set_ylabel(ylab)
    ax.set_title("(b) " + title, loc="left", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    print("Saved", out)


# ---------------- Dataset 1: FinSurvival ----------------
tr = pd.read_parquet("processed/train_labeled.parquet")
te = pd.read_parquet("processed/test_labeled.parquet")
both = pd.concat([tr, te])

s = pd.concat([both[both.label == 1].sample(2, random_state=1), both[both.label == 0].sample(3, random_state=1)])
sample1 = pd.DataFrame({
    "date": pd.to_datetime(s["timestamp"], unit="s").dt.strftime("%Y-%m-%d"),
    "coin": s["reserve"].astype(str),
    "amount (USD)": s["amountUSD"].map("{:,.0f}".format),
    "coin type": s["coinType"].astype(str),
    "past liquidations": s["userLiquidationCount"].astype(int),
    "past borrows": s["userBorrowCount"].fillna(0).astype(int),
    "days to event": (s["timeDiff"] / DAY).map("{:.1f}".format),
    "label": s["label"].astype(int),
})
make_figure(sample1, ["train\n(before 1 Jul 2022)", "test\n(from 1 Jul 2022)"],
            [len(tr), len(te)], [100 * tr.label.mean(), 100 * te.label.mean()],
            "Share of loans liquidated within 17.43 days", "liquidated (%)", "#3b6fb6",
            "figures/fig2_dataset1.png")

# ---------------- Dataset 2: Taiwan ----------------
f = (glob.glob("taiwan/*.xls") + glob.glob("taiwan/*.xlsx"))[0]
tw = pd.read_excel(f, header=1).rename(columns={"default payment next month": "label"})
s = pd.concat([tw[tw.label == 1].sample(2, random_state=1), tw[tw.label == 0].sample(3, random_state=1)])
sample2 = s[["LIMIT_BAL", "EDUCATION", "AGE", "PAY_0", "BILL_AMT1", "PAY_AMT1", "label"]].copy()
for c in ["LIMIT_BAL", "BILL_AMT1", "PAY_AMT1"]:
    sample2[c] = sample2[c].map("{:,.0f}".format)
counts = tw["label"].value_counts().sort_index()
make_figure(sample2, ["no default (0)", "default (1)"], counts.tolist(), (100 * counts / len(tw)).tolist(),
            "Class distribution (30,000 clients)", "share of clients (%)", "#d9822b",
            "figures/fig3_dataset2.png")

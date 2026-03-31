# BunDataAnalysis

BunDataAnalysis la ung dung Streamlit tong quat de kham pha va phan tich tep CSV cho nhieu nganh khac nhau.

## Ung dung nay lam duoc gi

- Doc bo du lieu mau di kem hoac bat ky tep CSV nao duoc tai len
- Tu dong lam sach cac cot so, tien te, phan tram va cot giong kieu ngay gio
- Hien thi tong quan bo du lieu, bao cao cot va thong ke cot so
- Cho phep tu tao phan tich theo nhom va bieu do tu cac cot ban chon
- Huan luyen cac mo hinh hoi quy co ban voi cot muc tieu dang so

## Cau truc project

```text
.
├── sample_dataset.csv
├── app.py
├── main.py
├── bun_data_analysis
│   ├── data.py
│   ├── charts.py
│   ├── modeling.py
│   └── ui.py
├── tests
│   └── test_data_processing.py
└── requirements.txt
```

## Cach chay

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Dua len Streamlit Community Cloud

Theo tai lieu chinh thuc cua Streamlit Community Cloud, ban can mot repo GitHub va chon repo, branch, file entrypoint khi deploy. Cau hinh khuyen dung cho project nay la:

- Repository: `BunDataAnalysis`
- Branch: `main`
- Main file path: `app.py`
- Python version: `3.12` trong `Advanced settings`

Tai lieu tham khao:

- [Deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [App dependencies for your Community Cloud app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

## Nhung gi da thay doi so voi ban cu

- Ung dung da tro thanh ban tong quat, khong con bi hardcode cho mot bo du lieu ban le cu the
- Giao dien da doi ten thanh `BunDataAnalysis`
- Khu vuc bieu do da tro thanh bo tao bieu do tong quat
- Tab phan tich da ho tro phan tich theo nhom cho nhieu bo du lieu khac nhau
- Tab mo hinh da tu dong chon bien dau vao thay vi phu thuoc vao cot doanh so co dinh

## Cach hoc project nay

1. Doc `bun_data_analysis/data.py` truoc.
2. Doc `bun_data_analysis/charts.py` tiep theo.
3. Doc `bun_data_analysis/modeling.py` sau do.
4. Doc `bun_data_analysis/ui.py` cuoi cung.

## Kiem thu

```bash
pytest
```

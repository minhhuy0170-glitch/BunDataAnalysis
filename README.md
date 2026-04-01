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
├── start.sh
├── render.yaml
├── bun_data_analysis
│   ├── data.py
│   ├── charts.py
│   ├── modeling.py
│   └── ui.py
├── scripts
│   └── ensure_streamlit_assets.py
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

## Dua len Render de lay link co dinh

Neu ban muon link co dinh de test va chia se, Render la cach don gian cho project nay.

Render yeu cau web service phai bind vao host `0.0.0.0` va port tu bien moi truong `PORT`. Project nay da co san:

- `start.sh` de chay Streamlit dung port cua Render
- `render.yaml` de luu cau hinh deploy
- `.python-version` de khoa phien ban Python on dinh

Theo tai lieu chinh thuc cua Render, ban co the deploy tu repo GitHub lien ket hoac tu URL cua public repo. Cau hinh tuong ung cho project nay la:

- Service type: `Web Service`
- Runtime/Language: `Python`
- Build command: `pip install -r requirements.txt`
- Start command: `./start.sh`
- Branch: `main`
- Environment Variables: khong can them gi

### Cach tao web co dinh tren Render

1. Vao `dashboard.render.com` va bam `New` -> `Web Service`.
2. Chon `Public Git Repository`.
3. Dan repo URL: `https://github.com/minhhuy0170-glitch/BunDataAnalysis`
4. Dien:
   `Name`: `bundataanalysis`
   `Branch`: `main`
   `Language`: `Python`
   `Build Command`: `pip install -r requirements.txt`
   `Start Command`: `./start.sh`
   `Instance Type`: `Free`
5. De trong `Environment Variables`.
6. Bam `Create Web Service`.

Sau khi deploy xong, ban se co link co dinh dang `https://ten-app.onrender.com`.

Link hien tai cua project:

- `https://bundataanalysis.onrender.com/`

Tai lieu tham khao:

- [Render Web Services](https://render.com/docs/web-services)
- [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec)
- [Setting Your Python Version on Render](https://render.com/docs/python-version)

## Dua len Streamlit Community Cloud

Ban van co the deploy len Streamlit Community Cloud neu muon:

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

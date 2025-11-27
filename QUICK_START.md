# Quick Start Guide - Deploy Crypto Tax MVP

## 🚀 Deploy nhanh lên Streamlit Cloud (5 phút)

### Bước 1: Chuẩn bị code
```bash
# Đảm bảo code đã sẵn sàng
git status
git add .
git commit -m "Ready for deployment"
```

### Bước 2: Push lên GitHub
```bash
# Tạo repository trên GitHub (nếu chưa có)
# Sau đó:
git remote add origin https://github.com/yourusername/tax_project.git
git push -u origin main
```

### Bước 3: Deploy lên Streamlit Cloud
1. Truy cập: https://streamlit.io/cloud
2. Đăng nhập bằng GitHub
3. Click **"New app"**
4. Chọn repository: `yourusername/tax_project`
5. Branch: `main`
6. Main file: `app.py`
7. Click **"Deploy"**

### Bước 4: Chờ deploy (2-3 phút)
- Streamlit Cloud tự động:
  - Install dependencies từ `requirements.txt`
  - Build app
  - Deploy

### Bước 5: Test
- Truy cập URL được cung cấp (ví dụ: `https://your-app.streamlit.app`)
- Test các tính năng cơ bản

## ✅ Checklist trước khi deploy

- [ ] Code đã test local: `streamlit run app.py`
- [ ] File `requirements.txt` đầy đủ
- [ ] File `app.py` ở root directory
- [ ] `.gitignore` đã cấu hình (không commit .env, *.db)
- [ ] Code đã push lên GitHub

## 🔧 Test local trước

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Mở browser: http://localhost:8501
# Test:
# - Import wallet
# - Import Binance API
# - Tính thuế
# - Xuất PDF
```

## 📝 Lưu ý quan trọng

1. **Dữ liệu tạm thời**: Session state mất khi refresh
2. **API Keys**: User tự nhập trong app (an toàn)
3. **PDF files**: Tạo tạm thời, user download ngay

## 🆘 Nếu gặp lỗi

### Lỗi import
- Kiểm tra `requirements.txt` có đủ packages
- Check Python version (3.8+)

### Lỗi deploy
- Check logs trên Streamlit Cloud
- Đảm bảo `app.py` ở root
- Kiểm tra syntax errors

## 🎯 Sau khi deploy

1. Share URL với users
2. Test tất cả tính năng
3. Monitor errors (nếu có)
4. Thu thập feedback

---

**Xem thêm**: `DEPLOYMENT.md` cho các phương án deploy khác


# Hướng dẫn Deploy Crypto Tax MVP

Ứng dụng có thể deploy lên nhiều nền tảng. Dưới đây là các phương án phổ biến:

## 🚀 Phương án 1: Streamlit Cloud (Khuyến nghị - Miễn phí)

**Ưu điểm**: Miễn phí, dễ deploy, tự động update khi push code

### Bước 1: Chuẩn bị
1. Đẩy code lên GitHub repository
2. Đảm bảo có file `requirements.txt`
3. File `app.py` ở root directory

### Bước 2: Deploy
1. Truy cập [streamlit.io/cloud](https://streamlit.io/cloud)
2. Đăng nhập bằng GitHub
3. Click **"New app"**
4. Chọn repository và branch
5. Main file path: `app.py`
6. Click **"Deploy"**

### Bước 3: Cấu hình (nếu cần)
- Streamlit Cloud tự động detect `requirements.txt`
- Không cần cấu hình thêm cho MVP

**Lưu ý**: 
- Dữ liệu lưu trong session state (mất khi refresh)
- Để lưu dữ liệu lâu dài, cần tích hợp database (PostgreSQL, MongoDB, etc.)

---

## 🐳 Phương án 2: Docker

### Tạo Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build và chạy
```bash
# Build image
docker build -t crypto-tax-mvp .

# Run container
docker run -p 8501:8501 crypto-tax-mvp
```

### Deploy lên cloud với Docker
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **DigitalOcean App Platform**

---

## ☁️ Phương án 3: Heroku

### Tạo các file cần thiết

**Procfile**:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt** (optional):
```
python-3.11.0
```

### Deploy
```bash
# Login Heroku
heroku login

# Create app
heroku create crypto-tax-mvp

# Deploy
git push heroku main
```

---

## 🔧 Các vấn đề cần xử lý trước khi deploy

### 1. Session State (Dữ liệu tạm thời)
**Vấn đề**: Dữ liệu trong `st.session_state` mất khi refresh hoặc restart

**Giải pháp**:
- ✅ **MVP**: Chấp nhận dữ liệu tạm thời (user import lại khi cần)
- 🔄 **Production**: Tích hợp database (PostgreSQL, MongoDB, Firebase)

### 2. File Storage
**Vấn đề**: SQLite/CSV files không persistent trên cloud

**Giải pháp**:
- Sử dụng cloud storage (AWS S3, Google Cloud Storage)
- Hoặc database cloud (PostgreSQL, MongoDB Atlas)

### 3. API Keys
**Vấn đề**: User cần nhập API keys mỗi lần

**Giải pháp hiện tại**: User tự nhập trong app (an toàn)
**Giải pháp tương lai**: Encrypt và lưu trong database

### 4. PDF Generation
**Vấn đề**: PDF files tạm thời

**Giải pháp**: 
- Lưu PDF vào cloud storage
- Hoặc chỉ generate khi user download

---

## 📋 Checklist trước khi deploy

- [x] File `requirements.txt` đầy đủ
- [x] File `app.py` ở root
- [x] `.gitignore` đã cấu hình
- [ ] Test local: `streamlit run app.py`
- [ ] Kiểm tra imports không bị lỗi
- [ ] Kiểm tra API calls có error handling
- [ ] Đọc file `DEPLOYMENT.md` này

---

## 🧪 Test local trước khi deploy

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Test các tính năng:
# 1. Import wallet address
# 2. Import Binance API
# 3. Tính thuế
# 4. Xuất PDF
```

---

## 🔒 Bảo mật khi deploy

1. **Không commit API keys** vào code
2. **Sử dụng environment variables** cho sensitive data
3. **HTTPS only** (Streamlit Cloud tự động có)
4. **Rate limiting** cho API calls (có thể cần thêm)

---

## 📊 Monitoring (Tùy chọn)

Sau khi deploy, có thể thêm:
- Error tracking (Sentry)
- Analytics (Google Analytics)
- Logging (CloudWatch, etc.)

---

## 🆘 Troubleshooting

### Lỗi import
- Kiểm tra `requirements.txt` có đủ packages
- Kiểm tra Python version (3.8+)

### Lỗi API calls
- Kiểm tra network connectivity
- Kiểm tra API rate limits

### App không chạy
- Check logs trên platform
- Test local trước

---

## 🎯 Khuyến nghị cho MVP

**Streamlit Cloud** là lựa chọn tốt nhất vì:
- ✅ Miễn phí
- ✅ Dễ deploy (5 phút)
- ✅ Tự động update
- ✅ HTTPS tự động
- ✅ Không cần cấu hình server

**Lưu ý**: Dữ liệu sẽ mất khi session hết hạn. Đây là OK cho MVP.


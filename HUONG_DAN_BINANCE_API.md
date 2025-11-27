# Hướng dẫn lấy Binance API Key

## Tại sao cần Binance API Key?

Để ứng dụng có thể lấy lịch sử giao dịch từ tài khoản Binance của bạn một cách tự động, bạn cần tạo API Key với quyền **Read Only** (chỉ đọc).

## Các bước lấy API Key

### Bước 1: Đăng nhập Binance

1. Truy cập [binance.com](https://www.binance.com)
2. Đăng nhập vào tài khoản của bạn
3. Nếu chưa có tài khoản, đăng ký tại [đây](https://accounts.binance.com/register)

### Bước 2: Vào phần API Management

1. Click vào **icon profile** (góc trên bên phải màn hình)
2. Chọn **"API Management"** hoặc **"Quản lý API"**
3. Nếu lần đầu, Binance sẽ yêu cầu xác thực bảo mật

### Bước 3: Tạo API mới

1. Click nút **"Create API"** hoặc **"Tạo API"**
2. Chọn **"System generated"** (hệ thống tự tạo API key)
3. Đặt tên cho API (ví dụ: "Crypto Tax App" hoặc "Tax Declaration")
4. Click **"Next"** hoặc **"Tiếp theo"**

### Bước 4: Cấp quyền (QUAN TRỌNG!)

**⚠️ CHỈ CHỌN QUYỀN READ ONLY ĐỂ BẢO MẬT**

✅ **CHỌN**:
- ✅ **Read Only** - Quyền đọc dữ liệu (BẮT BUỘC)

❌ **KHÔNG CHỌN**:
- ❌ Enable Withdrawals (Cho phép rút tiền)
- ❌ Enable Futures (Cho phép giao dịch futures)
- ❌ Enable Spot & Margin Trading (Cho phép giao dịch spot/margin)
- ❌ Enable Internal Transfer (Cho phép chuyển nội bộ)

**Lý do**: Ứng dụng chỉ cần **đọc** lịch sử giao dịch để tính thuế, không cần quyền giao dịch hay rút tiền.

### Bước 5: Xác thực bảo mật

Binance sẽ yêu cầu xác thực qua nhiều lớp:

1. **Email**: Kiểm tra email và nhập mã xác thực
2. **Google Authenticator / 2FA**: Nhập mã từ ứng dụng xác thực
3. **SMS** (nếu có): Nhập mã từ tin nhắn SMS

### Bước 6: Lưu API Key và Secret Key

**⚠️ QUAN TRỌNG: Secret Key chỉ hiển thị 1 LẦN DUY NHẤT**

Sau khi tạo thành công, Binance sẽ hiển thị:
- **API Key**: Dãy ký tự dài (ví dụ: `abc123xyz...`)
- **Secret Key**: Dãy ký tự dài (ví dụ: `def456uvw...`)

**HÀNH ĐỘNG NGAY**:
1. Copy **API Key** và lưu vào nơi an toàn
2. Copy **Secret Key** và lưu vào nơi an toàn
3. ⚠️ **KHÔNG BAO GIỜ** chia sẻ 2 key này với ai
4. Nếu quên Secret Key, bạn phải xóa API cũ và tạo lại

### Bước 7: Sử dụng trong ứng dụng

1. Mở ứng dụng Crypto Tax MVP
2. Vào trang **"Nhập dữ liệu"** → Tab **"Sàn giao dịch (Exchange)"**
3. Dán **API Key** vào ô "Binance API Key"
4. Dán **Secret Key** vào ô "Binance API Secret"
5. Click **"Test kết nối"** để kiểm tra
6. Nếu thành công, click **"Lấy giao dịch từ Binance"**

## Bảo mật API Key

### ✅ Nên làm:
- Chỉ tạo API key với quyền **Read Only**
- Lưu API key ở nơi an toàn (password manager)
- Xóa API key cũ nếu không dùng nữa
- Kiểm tra danh sách API keys định kỳ

### ❌ Không nên:
- Không chia sẻ API key với ai
- Không cấp quyền Withdrawals hoặc Trading
- Không lưu API key trên máy tính công cộng
- Không screenshot API key

## Xử lý sự cố

### Lỗi "Invalid API Key"
- Kiểm tra lại API Key và Secret Key đã copy đúng chưa
- Đảm bảo không có khoảng trắng thừa
- Thử tạo API key mới

### Lỗi "API key does not have permission"
- Kiểm tra API key có quyền **Read Only** không
- Nếu không, xóa API key cũ và tạo lại với quyền Read Only

### Lỗi "IP address not whitelisted"
- Vào API Management → Edit API
- Thêm IP address hiện tại vào whitelist (hoặc bỏ whitelist nếu không cần)

### Không thấy giao dịch
- Kiểm tra khoảng thời gian đã chọn
- Đảm bảo tài khoản Binance có giao dịch trong khoảng thời gian đó
- Thử mở rộng khoảng thời gian

## Câu hỏi thường gặp

**Q: API key có an toàn không?**
A: Có, nếu bạn chỉ cấp quyền Read Only. API key chỉ có thể đọc dữ liệu, không thể giao dịch hay rút tiền.

**Q: Có thể dùng chung API key cho nhiều ứng dụng không?**
A: Có thể, nhưng không khuyến khích. Nên tạo API key riêng cho mỗi ứng dụng để dễ quản lý.

**Q: Làm sao xóa API key?**
A: Vào API Management → Chọn API key → Click "Delete" hoặc "Xóa"

**Q: API key có hết hạn không?**
A: Không, API key không hết hạn. Nhưng bạn nên xóa nếu không dùng nữa.

## Liên kết hữu ích

- [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
- [Binance API Management](https://www.binance.com/en/my/settings/api-management)
- [Binance Security Tips](https://www.binance.com/en/support/faq/360033525031)


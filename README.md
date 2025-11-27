# Crypto Tax MVP - Vietnam

Ứng dụng web Streamlit hỗ trợ cá nhân khai thuế thu nhập từ giao dịch cryptocurrency tại Việt Nam.

## Tính năng

- **Kết nối Ví**: Nhập địa chỉ ví (MetaMask, Phantom) hoặc upload CSV để lấy lịch sử giao dịch
- **Kết nối Sàn**: Kết nối với Binance API để lấy lịch sử giao dịch tự động
- **Tính Thuế**: Tính toán thuế theo quy định Việt Nam (Nghị quyết 05/2025)
  - Chuyển nhượng: 0.1% trên giá trị giao dịch
  - Thu nhập khác: 10% trên tổng thu nhập
- **Dashboard**: Xem tổng quan giao dịch, lãi/lỗ, và thuế phải nộp
- **Báo cáo PDF**: Xuất báo cáo thuế theo mẫu Việt Nam

## Cài đặt

### Local Development

1. Clone repository:
```bash
git clone <repository-url>
cd tax_project
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
streamlit run app.py
```

4. Mở browser: http://localhost:8501

### Deploy lên Streamlit Cloud

Xem hướng dẫn chi tiết trong:
- **QUICK_START.md** - Hướng dẫn deploy nhanh (5 phút)
- **DEPLOYMENT.md** - Hướng dẫn deploy chi tiết (nhiều phương án)

## Cấu hình

Tạo file `.env` (optional) hoặc cấu hình trong `config.py`:
- API keys cho Etherscan, BSCScan, PolygonScan (optional, có thể dùng free tier)
- CoinGecko API key (optional)

## Sử dụng

1. **Import dữ liệu**:
   - Wallet: Nhập địa chỉ ví hoặc upload CSV
   - Exchange: Nhập Binance API keys (read-only) hoặc upload CSV

2. **Xem giao dịch**: Dashboard hiển thị tất cả giao dịch từ wallet và exchange

3. **Tính thuế**: Hệ thống tự động tính thuế theo phương pháp FIFO

4. **Xuất báo cáo**: Tải PDF báo cáo thuế để khai báo

## Quy định Thuế

Theo Nghị quyết 05/2025:
- **Thuế chuyển nhượng**: 0.1% trên giá trị mỗi lần giao dịch
- **Thuế thu nhập khác**: 10% trên tổng thu nhập (staking, airdrop, farming)

## Lưu ý

- API keys được lưu local, user tự quản lý bảo mật
- Chỉ hỗ trợ read-only API keys cho exchange
- Dữ liệu được lưu local (SQLite hoặc CSV)

## Tech Stack

- Streamlit
- Python 3.8+
- pandas, numpy
- web3.py (blockchain)
- python-binance, ccxt (exchange)
- reportlab (PDF)


# Crypto Tax Vietnam - Business Logic

## Tổng quan

Ứng dụng tính thuế giao dịch tiền mã hóa (cryptocurrency) theo quy định pháp luật Việt Nam, dựa trên Nghị quyết 05/2025.

## Quy định thuế

### 1. Thuế chuyển nhượng (Transfer Tax) - 0.1%

Áp dụng cho các giao dịch:
- **BUY**: Mua crypto bằng fiat
- **SELL**: Bán crypto lấy fiat
- **SWAP**: Đổi crypto này sang crypto khác

**Công thức:**
```
Thuế = Giá trị bán (VND) × 0.1%
```

**Lưu ý quan trọng:**
- Thuế tính trên **giá trị BÁN**, không phải giá trị mua
- Với SWAP: tính thuế trên giá trị token đầu ra (token nhận được)

### 2. Thuế thu nhập khác (Other Income Tax) - 10%

Áp dụng cho các khoản thu nhập:
- **STAKING**: Phần thưởng staking
- **AIRDROP**: Token nhận được miễn phí
- **FARMING**: Phần thưởng yield farming
- **REWARD**: Các phần thưởng khác

**Công thức:**
```
Thuế = Giá trị nhận (VND) × 10%
```

### 3. Không tính thuế

- **TRANSFER_IN**: Chuyển crypto vào ví (từ ví khác của mình)
- **TRANSFER_OUT**: Chuyển crypto ra ví khác
- **DEPOSIT**: Nạp tiền fiat
- **WITHDRAW**: Rút tiền fiat

## Tính giá vốn (Cost Basis) - Phương pháp FIFO

### FIFO là gì?

**FIFO = First In, First Out** (Vào trước, Ra trước)

Khi bán crypto, giá vốn được tính từ các lần mua **sớm nhất** trước.

### Ví dụ minh họa

**Lịch sử mua BTC:**
| Ngày | Số lượng | Giá (VND) |
|------|----------|-----------|
| 01/01 | 1 BTC | 500,000,000 |
| 15/01 | 1 BTC | 600,000,000 |
| 01/02 | 1 BTC | 550,000,000 |

**Bán 1.5 BTC vào ngày 15/02:**

Theo FIFO:
- 1 BTC đầu tiên (01/01): giá vốn = 500,000,000
- 0.5 BTC tiếp theo (15/01): giá vốn = 300,000,000

**Tổng giá vốn = 800,000,000 VND**

### Tại sao dùng FIFO?

1. **Phổ biến**: Được chấp nhận rộng rãi trong kế toán
2. **Đơn giản**: Dễ hiểu và theo dõi
3. **Nhất quán**: Kết quả có thể tái tạo

## Xử lý SWAP

SWAP là giao dịch đặc biệt - đổi token A lấy token B.

### Logic xử lý:

1. **Tính giá vốn token bán** (token_in):
   - Sử dụng FIFO để tính cost basis

2. **Tính giá trị token nhận** (token_out):
   - Lấy giá USD tại thời điểm giao dịch
   - Quy đổi sang VND

3. **Tính thuế**:
   - Thuế = Giá trị token nhận × 0.1%

4. **Cập nhật FIFO**:
   - Trừ token_in khỏi inventory
   - Thêm token_out vào inventory (giá = giá trị VND / số lượng)

### Ví dụ SWAP

**SWAP 1 ETH → 0.05 BTC** (khi 1 BTC = 1,000,000,000 VND)

- Token bán: 1 ETH
- Token nhận: 0.05 BTC
- Giá trị nhận: 50,000,000 VND
- **Thuế = 50,000,000 × 0.1% = 50,000 VND**

## Quy đổi tỷ giá

### USD → VND

Tất cả giao dịch được quy đổi sang VND để tính thuế.

**Nguồn tỷ giá:**
1. **Mặc định**: 25,450 VND/USD (config)
2. **API**: Lấy từ exchangerate-api.com (realtime)
3. **Manual**: Người dùng tự nhập

### Giá crypto

**Nguồn giá:**
- CoinGecko API (miễn phí)
- Hỗ trợ giá historical (theo ngày giao dịch)

## Các loại giao dịch

| Type | Mô tả | Thuế |
|------|-------|------|
| BUY | Mua crypto | 0.1% giá trị |
| SELL | Bán crypto | 0.1% giá trị |
| SWAP | Đổi crypto | 0.1% giá trị nhận |
| STAKING | Phần thưởng stake | 10% giá trị |
| AIRDROP | Token miễn phí | 10% giá trị |
| FARMING | Phần thưởng farm | 10% giá trị |
| REWARD | Phần thưởng khác | 10% giá trị |
| TRANSFER_IN | Chuyển vào | 0% |
| TRANSFER_OUT | Chuyển ra | 0% |
| DEPOSIT | Nạp fiat | 0% |
| WITHDRAW | Rút fiat | 0% |
| FEE | Phí giao dịch | 0% |
| OTHER | Khác | 0% |

## Nguồn dữ liệu

### 1. Blockchain (On-chain)
- **Ethereum**: Etherscan API
- **BSC**: BSCScan API
- **Polygon**: PolygonScan API

### 2. Sàn giao dịch (CEX)
- **Binance**: Binance API (spot trades)

### 3. File upload
- **CSV**: Binance export, custom format
- **JSON**: Custom format

## Báo cáo thuế

### Tổng hợp
- Tổng số giao dịch
- Tổng thuế chuyển nhượng (0.1%)
- Tổng thuế thu nhập khác (10%)
- Tổng lãi/lỗ

### Theo thời gian
- Theo tháng
- Theo quý
- Theo năm

### Export
- PDF report với thông tin cá nhân
- Chi tiết từng giao dịch

## Lưu ý pháp lý

1. Ứng dụng chỉ mang tính **tham khảo**
2. Người dùng tự chịu trách nhiệm về kê khai thuế
3. Nên tham khảo chuyên gia thuế khi cần
4. Quy định có thể thay đổi - cập nhật theo văn bản mới nhất

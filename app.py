"""
Main Streamlit application for Crypto Tax MVP
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import os
import json
from typing import List, Optional

# Import services
from models.transaction import Transaction, TransactionType, TransactionSource
from services.wallet_service import WalletService
from services.exchange_service import ExchangeService
from services.tax_calculator import TaxCalculator
from services.pdf_generator import PDFGenerator
from utils.transaction_normalizer import TransactionNormalizer
from utils.formatters import format_vnd, format_date, format_crypto
import config

# Page configuration
st.set_page_config(
    page_title="Crypto Tax MVP - Vietnam",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}


def main():
    """Main application"""
    st.title("💰 Crypto Tax MVP - Vietnam")
    st.markdown("Ứng dụng hỗ trợ khai thuế giao dịch tiền điện tử tại Việt Nam")
    
    # Sidebar navigation
    st.sidebar.title("📋 Menu")
    page = st.sidebar.radio(
        "Chọn trang:",
        ["🏠 Trang chủ", "📥 Nhập dữ liệu", "📊 Giao dịch", "📄 Báo cáo thuế", "📈 Phân tích"]
    )
    
    if page == "🏠 Trang chủ":
        show_home()
    elif page == "📥 Nhập dữ liệu":
        show_data_import()
    elif page == "📊 Giao dịch":
        show_transactions()
    elif page == "📄 Báo cáo thuế":
        show_tax_report()
    elif page == "📈 Phân tích":
        show_analytics()


def show_home():
    """Home page with overview"""
    st.header("🏠 Trang chủ")
    
    # Personal info section
    with st.expander("📝 Thông tin cá nhân", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Họ và tên", value=st.session_state.personal_info.get("name", ""))
            id_number = st.text_input("CMND/CCCD", value=st.session_state.personal_info.get("id_number", ""))
        with col2:
            address = st.text_area("Địa chỉ", value=st.session_state.personal_info.get("address", ""))
            phone = st.text_input("Số điện thoại", value=st.session_state.personal_info.get("phone", ""))
        
        if st.button("Lưu thông tin"):
            st.session_state.personal_info = {
                "name": name,
                "id_number": id_number,
                "address": address,
                "phone": phone,
            }
            st.success("Đã lưu thông tin cá nhân!")
    
    # Statistics
    transactions = st.session_state.transactions
    if transactions:
        tax_calculator = TaxCalculator()
        tax_summary = tax_calculator.get_tax_summary(transactions)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tổng số giao dịch", len(transactions))
        
        with col2:
            st.metric("Tổng thuế phải nộp", format_vnd(tax_summary["total_tax"]))
        
        with col3:
            st.metric("Thuế chuyển nhượng", format_vnd(tax_summary["total_transfer_tax"]))
        
        with col4:
            st.metric("Thuế thu nhập khác", format_vnd(tax_summary["total_other_income_tax"]))
        
        st.markdown("---")
        
        # Quick stats
        st.subheader("📊 Thống kê nhanh")
        df = pd.DataFrame([tx.to_dict() for tx in transactions])
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Giao dịch theo nguồn:**")
                source_counts = df["source"].value_counts()
                st.bar_chart(source_counts)
            
            with col2:
                st.write("**Giao dịch theo token:**")
                token_counts = df["token"].value_counts().head(10)
                st.bar_chart(token_counts)
    else:
        st.info("👆 Vui lòng nhập dữ liệu giao dịch từ trang 'Nhập dữ liệu'")


def show_data_import():
    """Data import page"""
    st.header("📥 Nhập dữ liệu")
    
    tab1, tab2, tab3 = st.tabs(["🔗 Ví (Wallet)", "🏦 Sàn giao dịch (Exchange)", "📁 Upload file"])
    
    with tab1:
        st.subheader("Kết nối ví")
        
        col1, col2 = st.columns(2)
        with col1:
            chain = st.selectbox(
                "Chọn blockchain:",
                ["Ethereum", "BSC", "Polygon", "Solana"]
            )
            wallet_address = st.text_input("Địa chỉ ví:", placeholder="0x...")
        
        with col2:
            api_key = st.text_input(
                "API Key (tùy chọn):",
                type="password",
                help="API key từ Etherscan, BSCScan, etc. (có thể dùng free tier)"
            )
            date_range = st.date_input(
                "Khoảng thời gian:",
                value=(date(2024, 1, 1), date.today()),
                help="Chọn khoảng thời gian để lấy giao dịch"
            )
        
        if st.button("🔍 Lấy giao dịch từ ví", type="primary"):
            if wallet_address:
                with st.spinner("Đang lấy giao dịch..."):
                    wallet_service = WalletService()
                    start_date = datetime.combine(date_range[0], datetime.min.time()) if len(date_range) > 0 else None
                    end_date = datetime.combine(date_range[1], datetime.max.time()) if len(date_range) > 1 else None
                    
                    transactions = wallet_service.fetch_transactions(
                        wallet_address,
                        chain.lower(),
                        api_key if api_key else None,
                        start_date,
                        end_date
                    )
                    
                    if transactions:
                        st.session_state.transactions.extend(transactions)
                        st.success(f"✅ Đã lấy {len(transactions)} giao dịch từ ví!")
                    else:
                        st.warning("Không tìm thấy giao dịch nào")
            else:
                st.error("Vui lòng nhập địa chỉ ví")
    
    with tab2:
        st.subheader("Kết nối sàn giao dịch")
        
        exchange = st.selectbox("Chọn sàn:", ["Binance"])
        
        if exchange == "Binance":
            # Hướng dẫn lấy API key
            with st.expander("📖 Hướng dẫn lấy Binance API Key (Click để xem)", expanded=False):
                st.markdown("""
                **Các bước lấy API Key từ Binance:**
                
                1. **Đăng nhập Binance**: Truy cập [binance.com](https://www.binance.com) và đăng nhập tài khoản
                
                2. **Vào phần API Management**:
                   - Click vào icon profile (góc trên bên phải)
                   - Chọn **"API Management"** hoặc **"Quản lý API"**
                
                3. **Tạo API mới**:
                   - Click **"Create API"** hoặc **"Tạo API"**
                   - Chọn **"System generated"** (hệ thống tự tạo)
                   - Đặt tên cho API (ví dụ: "Crypto Tax App")
                
                4. **Cấp quyền**:
                   - ✅ **BẮT BUỘC**: Chọn **"Read Only"** để bảo mật
                   - ❌ **KHÔNG CHỌN**: Enable Withdrawals, Enable Futures, Enable Spot & Margin Trading
                   - Chỉ cần quyền đọc dữ liệu là đủ
                
                5. **Xác thực bảo mật**:
                   - Nhập mã từ email
                   - Nhập mã từ Google Authenticator/2FA
                   - Xác nhận qua SMS (nếu có)
                
                6. **Lưu API Key và Secret Key**:
                   - ⚠️ **QUAN TRỌNG**: Secret Key chỉ hiển thị **1 LẦN DUY NHẤT**
                   - Copy và lưu vào nơi an toàn
                   - Dán vào form bên dưới
                
                **Lưu ý bảo mật:**
                - Chỉ dùng API key với quyền Read Only
                - Không chia sẻ API key với ai
                - Nếu nghi ngờ bị lộ, hãy xóa và tạo API key mới ngay
                """)
            
            col1, col2 = st.columns(2)
            with col1:
                api_key = st.text_input(
                    "Binance API Key:",
                    type="password",
                    placeholder="Nhập API Key của bạn",
                    help="API Key từ Binance (bắt đầu bằng các ký tự ngẫu nhiên)"
                )
            with col2:
                api_secret = st.text_input(
                    "Binance API Secret:",
                    type="password",
                    placeholder="Nhập Secret Key của bạn",
                    help="Secret Key từ Binance (chỉ hiển thị 1 lần khi tạo)"
                )
            
            # Test connection button
            if api_key and api_secret:
                if st.button("🔌 Test kết nối", help="Kiểm tra API key có hoạt động không"):
                    with st.spinner("Đang kiểm tra kết nối..."):
                        try:
                            from utils.exchange_clients import create_binance_client
                            client = create_binance_client(api_key, api_secret)
                            # Test by getting account info
                            account = client.client.get_account()
                            st.success("✅ Kết nối thành công! API key hợp lệ.")
                            st.info(f"Tài khoản: {account.get('accountType', 'N/A')}")
                        except Exception as e:
                            st.error(f"❌ Lỗi kết nối: {str(e)}")
                            st.info("💡 Kiểm tra lại API Key và Secret Key. Đảm bảo đã cấp quyền Read Only.")
            
            st.info("💡 **Quan trọng**: Chỉ tạo API key với quyền **Read Only** để bảo mật. Ứng dụng chỉ cần đọc dữ liệu giao dịch.")
            
            date_range = st.date_input(
                "Khoảng thời gian:",
                value=(date(2024, 1, 1), date.today()),
                key="exchange_date_range"
            )
            
            if st.button("🔍 Lấy giao dịch từ Binance", type="primary"):
                if api_key and api_secret:
                    with st.spinner("Đang lấy giao dịch từ Binance..."):
                        exchange_service = ExchangeService()
                        start_date = datetime.combine(date_range[0], datetime.min.time()) if len(date_range) > 0 else None
                        end_date = datetime.combine(date_range[1], datetime.max.time()) if len(date_range) > 1 else None
                        
                        transactions = exchange_service.fetch_binance_transactions(
                            api_key,
                            api_secret,
                            start_date,
                            end_date
                        )
                        
                        if transactions:
                            st.session_state.transactions.extend(transactions)
                            st.success(f"✅ Đã lấy {len(transactions)} giao dịch từ Binance!")
                        else:
                            st.warning("Không tìm thấy giao dịch nào")
                else:
                    st.error("Vui lòng nhập API Key và Secret")
    
    with tab3:
        st.subheader("Upload file CSV/JSON")
        
        uploaded_file = st.file_uploader(
            "Chọn file giao dịch:",
            type=["csv", "json"],
            help="Upload file CSV hoặc JSON chứa lịch sử giao dịch"
        )
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                    st.write("Preview:", df.head())
                    # TODO: Parse CSV to transactions
                    st.info("Tính năng parse CSV đang được phát triển")
                elif uploaded_file.name.endswith('.json'):
                    data = json.load(uploaded_file)
                    st.json(data)
                    # TODO: Parse JSON to transactions
                    st.info("Tính năng parse JSON đang được phát triển")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")


def show_transactions():
    """Transactions page"""
    st.header("📊 Giao dịch")
    
    transactions = st.session_state.transactions
    
    if not transactions:
        st.info("Chưa có giao dịch nào. Vui lòng nhập dữ liệu từ trang 'Nhập dữ liệu'")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_source = st.selectbox("Lọc theo nguồn:", ["Tất cả", "Wallet", "Exchange"])
    with col2:
        filter_token = st.selectbox("Lọc theo token:", ["Tất cả"] + list(set(tx.token for tx in transactions)))
    with col3:
        filter_type = st.selectbox("Lọc theo loại:", ["Tất cả"] + list(set(tx.type.value for tx in transactions)))
    
    # Filter transactions
    filtered = transactions
    if filter_source != "Tất cả":
        source = TransactionSource.WALLET if filter_source == "Wallet" else TransactionSource.EXCHANGE
        filtered = [tx for tx in filtered if tx.source == source]
    if filter_token != "Tất cả":
        filtered = [tx for tx in filtered if tx.token == filter_token]
    if filter_type != "Tất cả":
        filtered = [tx for tx in filtered if tx.type.value == filter_type]
    
    # Display table
    if filtered:
        df = pd.DataFrame([tx.to_dict() for tx in filtered])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=False)
        
        # Format for display
        display_df = df[[
            "date", "type", "token", "amount", "value_vnd", "source", "chain"
        ]].copy()
        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y %H:%M")
        display_df["value_vnd"] = display_df["value_vnd"].apply(lambda x: format_vnd(x))
        display_df.columns = ["Ngày", "Loại", "Token", "Số lượng", "Giá trị (VND)", "Nguồn", "Chain"]
        
        st.dataframe(display_df, use_container_width=True, height=400)
        st.write(f"Tổng cộng: {len(filtered)} giao dịch")
    else:
        st.warning("Không có giao dịch nào khớp với bộ lọc")


def show_tax_report():
    """Tax report page"""
    st.header("📄 Báo cáo thuế")
    
    transactions = st.session_state.transactions
    
    if not transactions:
        st.info("Chưa có giao dịch nào. Vui lòng nhập dữ liệu từ trang 'Nhập dữ liệu'")
        return
    
    tax_calculator = TaxCalculator()
    tax_summary = tax_calculator.get_tax_summary(transactions)
    
    # Summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng thuế phải nộp", format_vnd(tax_summary["total_tax"]))
        st.metric("Thuế chuyển nhượng (0.1%)", format_vnd(tax_summary["total_transfer_tax"]))
    with col2:
        st.metric("Thuế thu nhập khác (10%)", format_vnd(tax_summary["total_other_income_tax"]))
        st.metric("Tổng lãi/lỗ", format_vnd(tax_summary["total_profit_loss"]))
    
    st.markdown("---")
    
    # Tax by period
    st.subheader("Thuế theo từng tháng")
    tax_by_month = tax_calculator.get_tax_by_period(transactions, "month")
    if not tax_by_month.empty:
        st.dataframe(tax_by_month, use_container_width=True)
    
    # Generate PDF
    st.markdown("---")
    st.subheader("Xuất báo cáo PDF")
    
    if st.button("📥 Tạo và tải báo cáo PDF", type="primary"):
        with st.spinner("Đang tạo PDF..."):
            pdf_generator = PDFGenerator()
            output_path = "tax_report.pdf"
            
            try:
                pdf_generator.generate_tax_report(
                    transactions,
                    output_path,
                    st.session_state.personal_info
                )
                
                with open(output_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Tải PDF",
                        data=pdf_file,
                        file_name=f"tax_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                
                st.success("✅ Đã tạo báo cáo PDF!")
            except Exception as e:
                st.error(f"Lỗi tạo PDF: {e}")


def show_analytics():
    """Analytics page"""
    st.header("📈 Phân tích")
    
    transactions = st.session_state.transactions
    
    if not transactions:
        st.info("Chưa có giao dịch nào. Vui lòng nhập dữ liệu từ trang 'Nhập dữ liệu'")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([tx.to_dict() for tx in transactions])
    df["date"] = pd.to_datetime(df["date"])
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Giao dịch theo thời gian")
        daily_counts = df.groupby(df["date"].dt.date).size()
        st.line_chart(daily_counts)
    
    with col2:
        st.subheader("Giá trị giao dịch theo thời gian")
        daily_value = df.groupby(df["date"].dt.date)["value_vnd"].sum()
        st.line_chart(daily_value)
    
    # Tax calculator for profit/loss over time
    tax_calculator = TaxCalculator()
    tax_df = tax_calculator.calculate_taxes(transactions)
    
    if not tax_df.empty:
        st.subheader("Lãi/Lỗ theo thời gian")
        tax_df["date"] = tax_df["transaction"].apply(lambda x: x.date)
        tax_df["date"] = pd.to_datetime(tax_df["date"])
        daily_pnl = tax_df.groupby(tax_df["date"].dt.date)["profit_loss"].sum()
        st.line_chart(daily_pnl)
        
        st.subheader("Thuế theo thời gian")
        daily_tax = tax_df.groupby(tax_df["date"].dt.date)["tax_amount"].sum()
        st.line_chart(daily_tax)


if __name__ == "__main__":
    main()


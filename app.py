"""
Streamlit Application for Crypto Tax MVP
Uses API layer for all business logic
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

# API Layer
from api import get_container

# Formatters
from utils.formatters import format_vnd

# Page configuration
st.set_page_config(
    page_title="Crypto Tax MVP - Vietnam",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Get API container
api = get_container()


def main():
    """Main application"""
    st.title("💰 Crypto Tax MVP - Vietnam")
    st.markdown("Ứng dụng hỗ trợ khai thuế giao dịch tiền điện tử tại Việt Nam")

    # Sidebar
    render_sidebar()

    # Page navigation
    page = st.session_state.get("current_page", "🏠 Trang chủ")

    if page == "🏠 Trang chủ":
        render_home()
    elif page == "📥 Nhập dữ liệu":
        render_data_import()
    elif page == "📊 Giao dịch":
        render_transactions()
    elif page == "📄 Báo cáo thuế":
        render_tax_report()
    elif page == "📈 Phân tích":
        render_analytics()


def render_sidebar():
    """Render sidebar with navigation and settings"""
    st.sidebar.title("📋 Menu")

    # Navigation
    page = st.sidebar.radio(
        "Chọn trang:",
        [
            "🏠 Trang chủ",
            "📥 Nhập dữ liệu",
            "📊 Giao dịch",
            "📄 Báo cáo thuế",
            "📈 Phân tích",
        ],
    )
    st.session_state.current_page = page

    # Exchange rate section
    st.sidebar.markdown("---")
    st.sidebar.subheader("💱 Tỷ giá USD/VND")

    rate_info = api.exchange_rate.get_current()
    if rate_info.success:
        st.sidebar.text(f"Tỷ giá hiện tại: {rate_info.data.current_rate:,.0f} VND")

        manual_rate = st.sidebar.number_input(
            "Nhập tỷ giá thủ công:",
            min_value=20000.0,
            max_value=30000.0,
            value=rate_info.data.current_rate,
            step=100.0,
            format="%.0f",
        )

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("💾 Lưu", key="save_rate"):
                result = api.exchange_rate.set_manual(manual_rate)
                if result.success:
                    st.sidebar.success(f"Đã lưu: {manual_rate:,.0f}")
                    st.rerun()
                else:
                    st.sidebar.error(result.message)

        with col2:
            if st.button("🔄 API", key="refresh_rate"):
                with st.spinner("Đang lấy tỷ giá..."):
                    result = api.exchange_rate.refresh_from_api()
                    if result.success:
                        st.sidebar.success(result.message)
                        st.rerun()
                    else:
                        st.sidebar.warning(result.message)

    # Data management section
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Quản lý dữ liệu")
    st.sidebar.text(f"Số giao dịch: {api.transactions.get_count()}")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("💾 Lưu", key="save_data"):
            result = api.transactions.save()
            if result.success:
                st.sidebar.success("Đã lưu!")
            else:
                st.sidebar.error(result.message)

    with col2:
        if st.button("🗑️ Xóa", key="clear_data"):
            result = api.transactions.clear_all()
            if result.success:
                st.sidebar.success("Đã xóa!")
                st.rerun()


def render_home():
    """Render home page"""
    st.header("🏠 Trang chủ")

    # Personal info
    if "personal_info" not in st.session_state:
        st.session_state.personal_info = {}

    with st.expander("📝 Thông tin cá nhân", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Họ và tên", value=st.session_state.personal_info.get("name", "")
            )
            id_number = st.text_input(
                "CMND/CCCD", value=st.session_state.personal_info.get("id_number", "")
            )
        with col2:
            address = st.text_area(
                "Địa chỉ", value=st.session_state.personal_info.get("address", "")
            )
            phone = st.text_input(
                "Số điện thoại", value=st.session_state.personal_info.get("phone", "")
            )

        if st.button("Lưu thông tin"):
            st.session_state.personal_info = {
                "name": name,
                "id_number": id_number,
                "address": address,
                "phone": phone,
            }
            st.success("Đã lưu thông tin cá nhân!")

    # Statistics
    stats_result = api.transactions.get_stats()
    if stats_result.success and stats_result.data.total_count > 0:
        stats = stats_result.data

        # Tax summary
        tax_result = api.tax.calculate_summary()
        if tax_result.success:
            tax = tax_result.data

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Tổng số giao dịch", stats.total_count)
            with col2:
                st.metric("Tổng thuế phải nộp", format_vnd(tax.total_tax))
            with col3:
                st.metric("Thuế chuyển nhượng", format_vnd(tax.total_transfer_tax))
            with col4:
                st.metric("Thuế thu nhập khác", format_vnd(tax.total_other_income_tax))

        st.markdown("---")
        st.subheader("📊 Thống kê nhanh")

        col1, col2 = st.columns(2)
        with col1:
            st.write("**Giao dịch theo nguồn:**")
            if stats.by_source:
                st.bar_chart(pd.Series(stats.by_source))

        with col2:
            st.write("**Giao dịch theo token:**")
            if stats.by_token:
                top_tokens = dict(
                    sorted(stats.by_token.items(), key=lambda x: x[1], reverse=True)[
                        :10
                    ]
                )
                st.bar_chart(pd.Series(top_tokens))
    else:
        st.info("👆 Vui lòng nhập dữ liệu giao dịch từ trang 'Nhập dữ liệu'")


def render_data_import():
    """Render data import page"""
    st.header("📥 Nhập dữ liệu")

    tab1, tab2, tab3 = st.tabs(["🔗 Ví (Wallet)", "🏦 Sàn giao dịch", "📁 Upload file"])

    with tab1:
        render_wallet_import()

    with tab2:
        render_exchange_import()

    with tab3:
        render_file_import()


def render_wallet_import():
    """Render wallet import section"""
    st.subheader("Kết nối ví")

    col1, col2 = st.columns(2)
    with col1:
        chains = api.data_import.get_supported_chains()
        chain = st.selectbox("Chọn blockchain:", chains)
        wallet_address = st.text_input("Địa chỉ ví:", placeholder="0x...")

    with col2:
        wallet_api_key = st.text_input(
            "API Key (tùy chọn):",
            type="password",
            help="API key từ Etherscan, BSCScan, etc.",
        )
        date_range = st.date_input(
            "Khoảng thời gian:", value=(date(2024, 1, 1), date.today())
        )

    if st.button("🔍 Lấy giao dịch từ ví", type="primary"):
        start_date = (
            datetime.combine(date_range[0], datetime.min.time())
            if len(date_range) > 0
            else None
        )
        end_date = (
            datetime.combine(date_range[1], datetime.max.time())
            if len(date_range) > 1
            else None
        )

        with st.spinner("Đang lấy giao dịch..."):
            result = api.data_import.import_from_wallet(
                wallet_address,
                chain,
                wallet_api_key if wallet_api_key else None,
                start_date,
                end_date,
            )

            if result.success:
                if result.data.count > 0:
                    st.success(result.message)
                else:
                    st.warning(
                        result.data.warnings[0]
                        if result.data.warnings
                        else "Không tìm thấy giao dịch"
                    )
            else:
                st.error(result.message)


def render_exchange_import():
    """Render exchange import section"""
    st.subheader("Kết nối sàn giao dịch")

    exchanges = api.data_import.get_supported_exchanges()
    exchange = st.selectbox("Chọn sàn:", exchanges)

    if exchange == "Binance":
        with st.expander("📖 Hướng dẫn lấy Binance API Key", expanded=False):
            st.markdown(
                """
            **Các bước lấy API Key từ Binance:**
            1. Đăng nhập Binance → API Management
            2. Tạo API mới với quyền **Read Only**
            3. Copy API Key và Secret Key
            """
            )

        col1, col2 = st.columns(2)
        with col1:
            binance_api_key = st.text_input("Binance API Key:", type="password")
        with col2:
            binance_api_secret = st.text_input("Binance API Secret:", type="password")

        if binance_api_key and binance_api_secret:
            if st.button("🔌 Test kết nối"):
                with st.spinner("Đang kiểm tra..."):
                    result = api.data_import.test_binance_connection(
                        binance_api_key, binance_api_secret
                    )
                    if result.success:
                        st.success(result.message)

                        info = result.data or {}

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Loại tài khoản", info.get("account_type", "N/A"))
                        with col2:
                            st.metric(
                                "Có thể giao dịch",
                                "Có" if info.get("can_trade") else "Không",
                            )
                        with col3:
                            st.metric(
                                "Có thể rút",
                                "Có" if info.get("can_withdraw") else "Không",
                            )

                        with st.expander("Chi tiết kết nối (debug)"):
                            st.write(
                                f"Server time (UTC): {info.get('server_time_utc', '')}"
                            )
                            st.write(
                                f"Local time (UTC): {info.get('local_time_utc', '')}"
                            )
                            st.write(
                                f"Timestamp offset (ms): {info.get('timestamp_offset_ms', '')}"
                            )
                            st.json(info)
                    else:
                        st.error(result.message)

        exchange_date_range = st.date_input(
            "Khoảng thời gian:",
            value=(date(2024, 1, 1), date.today()),
            key="exchange_date_range",
        )

        if st.button("🔍 Lấy giao dịch từ Binance", type="primary"):
            if binance_api_key and binance_api_secret:
                start_date = datetime.combine(
                    exchange_date_range[0], datetime.min.time()
                )
                end_date = datetime.combine(exchange_date_range[1], datetime.max.time())

                with st.spinner("Đang lấy giao dịch từ Binance..."):
                    result = api.data_import.import_from_binance(
                        binance_api_key, binance_api_secret, start_date, end_date
                    )

                    if result.success:
                        if result.data.count > 0:
                            st.success(result.message)
                        else:
                            st.warning("Không tìm thấy giao dịch")
                    else:
                        st.error(result.message)
            else:
                st.error("Vui lòng nhập API Key và Secret")


def render_file_import():
    """Render file import section"""
    st.subheader("Upload file CSV/JSON")

    with st.expander("📋 Xem định dạng file mẫu", expanded=False):
        st.markdown("**Định dạng CSV:**")
        st.code(api.data_import.get_sample_csv_format(), language="csv")
        st.markdown("**Định dạng JSON:**")
        st.code(api.data_import.get_sample_json_format(), language="json")

    uploaded_file = st.file_uploader("Chọn file giao dịch:", type=["csv", "json"])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
                st.write(f"**Preview ({len(df)} dòng):**")
                st.dataframe(df.head(10), use_container_width=True)
                uploaded_file.seek(0)

                if st.button("📥 Import từ CSV", type="primary"):
                    with st.spinner("Đang xử lý..."):
                        result = api.data_import.import_from_csv(
                            uploaded_file, uploaded_file.name
                        )
                        if result.success and result.data.count > 0:
                            st.success(result.message)
                        else:
                            st.warning(
                                result.data.warnings[0]
                                if result.data.warnings
                                else "Không tìm thấy giao dịch"
                            )

            elif uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)
                st.write("**Preview:**")
                st.json(data[:5] if isinstance(data, list) else data)
                uploaded_file.seek(0)

                if st.button("📥 Import từ JSON", type="primary"):
                    with st.spinner("Đang xử lý..."):
                        result = api.data_import.import_from_json(uploaded_file)
                        if result.success and result.data.count > 0:
                            st.success(result.message)
                        else:
                            st.warning(
                                result.data.warnings[0]
                                if result.data.warnings
                                else "Không tìm thấy giao dịch"
                            )

        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")


def render_transactions():
    """Render transactions page"""
    st.header("📊 Giao dịch")

    result = api.transactions.get_all()
    if not result.success or not result.data:
        st.info("Chưa có giao dịch nào")
        return

    transactions = result.data

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_source = st.selectbox(
            "Lọc theo nguồn:", ["Tất cả", "Wallet", "Exchange"]
        )
    with col2:
        tokens = ["Tất cả"] + api.transactions.get_unique_tokens()
        filter_token = st.selectbox("Lọc theo token:", tokens)
    with col3:
        types = ["Tất cả"] + api.transactions.get_unique_types()
        filter_type = st.selectbox("Lọc theo loại:", types)

    # Apply filters
    from api.transactions import TransactionFilter
    from models.transaction import TransactionSource, TransactionType

    tx_filter = TransactionFilter()
    if filter_source != "Tất cả":
        tx_filter.source = (
            TransactionSource.WALLET
            if filter_source == "Wallet"
            else TransactionSource.EXCHANGE
        )
    if filter_token != "Tất cả":
        tx_filter.token = filter_token
    if filter_type != "Tất cả":
        tx_filter.tx_type = TransactionType(filter_type)

    filtered_result = api.transactions.get_filtered(tx_filter)
    if filtered_result.success and filtered_result.data:
        df = pd.DataFrame([tx.to_dict() for tx in filtered_result.data])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=False)

        display_df = df[
            ["date", "type", "token", "amount", "value_vnd", "source", "chain"]
        ].copy()
        display_df["date"] = display_df["date"].dt.strftime("%d/%m/%Y %H:%M")
        display_df["value_vnd"] = display_df["value_vnd"].apply(lambda x: format_vnd(x))
        display_df.columns = [
            "Ngày",
            "Loại",
            "Token",
            "Số lượng",
            "Giá trị (VND)",
            "Nguồn",
            "Chain",
        ]

        st.dataframe(display_df, use_container_width=True, height=400)
        st.write(f"Tổng cộng: {len(filtered_result.data)} giao dịch")
    else:
        st.warning("Không có giao dịch khớp với bộ lọc")


def render_tax_report():
    """Render tax report page"""
    st.header("📄 Báo cáo thuế")

    if api.transactions.get_count() == 0:
        st.info("Chưa có giao dịch nào")
        return

    # Summary
    tax_result = api.tax.calculate_summary()
    if tax_result.success:
        tax = tax_result.data

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tổng thuế phải nộp", format_vnd(tax.total_tax))
            st.metric("Thuế chuyển nhượng (0.1%)", format_vnd(tax.total_transfer_tax))
        with col2:
            st.metric(
                "Thuế thu nhập khác (10%)", format_vnd(tax.total_other_income_tax)
            )
            st.metric("Tổng lãi/lỗ", format_vnd(tax.total_profit_loss))

    st.markdown("---")

    # Tax by period
    st.subheader("Thuế theo từng tháng")
    period_result = api.tax.calculate_by_period(period="month")
    if period_result.success and period_result.data:
        period_df = pd.DataFrame(
            [
                {"Tháng": p.period, "Thuế": p.tax_amount, "Lãi/Lỗ": p.profit_loss}
                for p in period_result.data
            ]
        )
        st.dataframe(period_df, use_container_width=True)

    # Generate PDF
    st.markdown("---")
    st.subheader("Xuất báo cáo PDF")

    if st.button("📥 Tạo và tải báo cáo PDF", type="primary"):
        with st.spinner("Đang tạo PDF..."):
            result = api.tax.generate_pdf_report(
                output_path="tax_report.pdf",
                personal_info=st.session_state.get("personal_info", {}),
            )

            if result.success:
                with open(result.data, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Tải PDF",
                        data=pdf_file,
                        file_name=f"tax_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                    )
                st.success("✅ Đã tạo báo cáo PDF!")
            else:
                st.error(result.message)


def render_analytics():
    """Render analytics page"""
    st.header("📈 Phân tích")

    result = api.transactions.get_all()
    if not result.success or not result.data:
        st.info("Chưa có giao dịch nào")
        return

    transactions = result.data
    df = pd.DataFrame([tx.to_dict() for tx in transactions])
    df["date"] = pd.to_datetime(df["date"])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Giao dịch theo thời gian")
        daily_counts = df.groupby(df["date"].dt.date).size()
        st.line_chart(daily_counts)

    with col2:
        st.subheader("Giá trị giao dịch theo thời gian")
        daily_value = df.groupby(df["date"].dt.date)["value_vnd"].sum()
        st.line_chart(daily_value)

    # Tax over time
    tax_detail_result = api.tax.calculate_detailed()
    if tax_detail_result.success and not tax_detail_result.data.empty:
        tax_df = tax_detail_result.data
        tax_df["date"] = tax_df["transaction"].apply(lambda x: x.date)
        tax_df["date"] = pd.to_datetime(tax_df["date"])

        st.subheader("Lãi/Lỗ theo thời gian")
        daily_pnl = tax_df.groupby(tax_df["date"].dt.date)["profit_loss"].sum()
        st.line_chart(daily_pnl)

        st.subheader("Thuế theo thời gian")
        daily_tax = tax_df.groupby(tax_df["date"].dt.date)["tax_amount"].sum()
        st.line_chart(daily_tax)


if __name__ == "__main__":
    main()

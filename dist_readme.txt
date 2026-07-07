ACRA HELPER — HƯỚNG DẪN SỬ DỤNG
================================

CÀI ĐẶT
-------
1. Giải nén toàn bộ thư mục này ra một nơi bất kỳ trên máy tính (ví dụ Desktop).
2. Không cần cài Python hay bất kỳ phần mềm nào khác.
3. Đảm bảo file "ACRA-Helper.exe" và thư mục "companies" nằm CÙNG một thư mục
   (không tách rời chúng ra).

CHẠY CHƯƠNG TRÌNH
------------------
1. Double-click vào "ACRA-Helper.exe".
2. Nếu Windows hiện cảnh báo "Windows protected your PC" (SmartScreen):
   bấm "More info" → "Run anyway". Đây là cảnh báo bình thường với ứng
   dụng chưa mua chứng chỉ ký số thương mại, không phải virus.
3. Chờ khoảng 3-5 giây, trình duyệt mặc định sẽ tự động mở ra giao diện.
   Nếu không tự mở, hãy mở trình duyệt và vào địa chỉ: http://localhost:5000

SỬ DỤNG
-------
- Bấm "Run Demo" ở góc dưới bên trái để thử ngay với dữ liệu mẫu có sẵn.
- Để xử lý công ty thật: chọn công ty ở cột trái, upload file Word/Excel
  báo cáo tài chính, chọn chế độ (Pre-fill hoặc Full XBRL Package), bấm Run.
- Sau khi chạy xong, bấm "Download ZIP" để tải gói kết quả, dùng để mở
  trong BizFinx Preparation Tool và nộp lên ACRA.
- Xem thêm hướng dẫn chi tiết ngay trong giao diện, mục "How to use —
  filing workflow" ở đầu trang.

LƯU Ý
-----
- Kết quả xử lý (thư mục "output") và file đã upload (thư mục "inputs")
  sẽ được lưu ngay cạnh file .exe — không bị mất khi tắt chương trình.
- Để tắt chương trình: đóng cửa sổ trình duyệt, sau đó vào Task Manager
  tắt tiến trình "ACRA-Helper.exe" (chương trình chạy nền không có cửa
  sổ riêng).
- Phần "Full set of financial statements" trong gói XBRL sẽ giữ nguyên
  bảng biểu, định dạng đậm/nghiêng như file Word gốc CHỈ KHI máy có cài
  LibreOffice (miễn phí — tải tại https://www.libreoffice.org/download/).
  Nếu chưa cài, chương trình vẫn chạy bình thường nhưng phần văn bản đó
  sẽ hiển thị dạng chữ chạy liền (không có bảng).

Có vấn đề gì xin liên hệ lại để được hỗ trợ.

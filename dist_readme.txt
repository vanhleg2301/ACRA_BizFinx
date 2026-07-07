===============================================================
  ACRA HELPER — HƯỚNG DẪN SỬ DỤNG
===============================================================

Công cụ này giúp tạo gói hồ sơ XBRL từ báo cáo tài chính (Word/Excel)
để nộp lên ACRA qua BizFinx. Chạy hoàn toàn trên máy của bạn, không
cần cài Python hay gửi dữ liệu ra ngoài.


BƯỚC 1 — GIẢI NÉN
-----------------
Giải nén toàn bộ file .zip ra một thư mục bất kỳ, ví dụ:
   Desktop\ACRA-Helper\

Sau khi giải nén, thư mục phải có đúng cấu trúc này:

   ACRA-Helper\
   ├── ACRA-Helper.exe      ← chương trình chính
   ├── companies\           ← dữ liệu công ty (BẮT BUỘC để cạnh .exe)
   └── HUONG_DAN_SU_DUNG.txt   ← file này

   ⚠ Không tách rời "companies" khỏi "ACRA-Helper.exe" — nếu để ở
     hai chỗ khác nhau chương trình sẽ không tìm thấy dữ liệu công ty.


BƯỚC 2 — CHẠY CHƯƠNG TRÌNH
---------------------------
1. Double-click vào "ACRA-Helper.exe".

2. Nếu Windows hiện màn hình xanh "Windows protected your PC":
      → Bấm chữ "More info"
      → Bấm nút "Run anyway"
   Đây là cảnh báo mặc định của Windows với mọi phần mềm mới chưa
   mua chứng chỉ ký số thương mại (chi phí hàng trăm USD/năm) —
   KHÔNG phải virus. Phần mềm chỉ chạy trên máy bạn, không kết nối
   ra ngoài để phát tán bất cứ thứ gì.

3. Windows Defender Firewall có thể hỏi "cho phép ứng dụng này truy
   cập mạng riêng/công cộng" — bấm "Allow access" (chương trình chỉ
   dùng mạng nội bộ máy bạn, không ra Internet).

4. Chờ khoảng 3-5 giây. Trình duyệt mặc định (Chrome/Edge/Firefox)
   sẽ TỰ ĐỘNG MỞ ra giao diện.

   Nếu sau 10 giây vẫn chưa thấy gì tự mở, hãy tự mở trình duyệt
   và gõ vào thanh địa chỉ:
        http://localhost:5000


BƯỚC 3 — DÙNG THỬ NGAY VỚI DỮ LIỆU MẪU
----------------------------------------
Bấm nút "Run Demo" ở góc dưới bên trái. Chương trình sẽ tự chạy với
dữ liệu mẫu có sẵn (công ty "EVX Ventures") và cho phép tải về file
ZIP kết quả để xem thử toàn bộ quy trình hoạt động ra sao.


BƯỚC 4 — XỬ LÝ BÁO CÁO TÀI CHÍNH THẬT
----------------------------------------
1. Chọn công ty ở cột bên trái (nếu đã có sẵn danh sách).
2. Kéo-thả (hoặc bấm chọn) file Word (.docx) và/hoặc Excel (.xlsx)
   báo cáo tài chính vào 2 ô "Input Files".
3. Chọn chế độ ở "Run Options":
      • Pre-fill (Excel + JSON)  → xuất file Excel/JSON để rà soát
      • Full XBRL Package        → xuất gói ZIP để nộp ACRA
4. Bấm nút "Run" (màu tím).
5. Đọc kết quả hiển thị: chấm XANH = thành công, chấm ĐỎ = có lỗi
   cần sửa lại trong file Word/Excel gốc rồi chạy lại.
6. Bấm "Download ZIP" để tải gói kết quả.

Xem thêm hướng dẫn chi tiết ngay trong giao diện, mục
"How to use — filing workflow" (bấm vào để mở rộng) ở đầu trang.


BƯỚC 5 — NỘP LÊN ACRA
-----------------------
1. Mở file ZIP vừa tải bằng BizFinx Preparation Tool (add-in Excel
   của ACRA — tải miễn phí tại trang ACRA nếu chưa có).
2. Trong BizFinx: bấm "Validate" (kiểm tra offline).
3. Nếu không còn lỗi: bấm "Validate Online" → "Acknowledge and
   Upload" để nộp chính thức.


TẮT CHƯƠNG TRÌNH
-----------------
Chương trình chạy ẩn (không có cửa sổ riêng, chỉ có trình duyệt).
Để tắt hẳn: đóng tab trình duyệt, sau đó mở Task Manager
(Ctrl+Shift+Esc) → tìm "ACRA-Helper.exe" → bấm "End task".


CÂU HỎI THƯỜNG GẶP
--------------------
Q: Có cần Internet không?
A: Không. Mọi xử lý diễn ra trên máy bạn.

Q: Dữ liệu đã upload/kết quả đã chạy có bị mất khi tắt máy không?
A: Không. Chúng được lưu trong 2 thư mục "inputs" và "output" tự
   động sinh ra ngay cạnh file ACRA-Helper.exe.

Q: Trình duyệt báo "localhost từ chối kết nối"?
A: Chương trình có thể chưa khởi động xong, hoặc đã bị Task Manager
   tắt trước đó — mở lại "ACRA-Helper.exe" và chờ vài giây.

Q: Phần "Full set of financial statements" trong file XBRL bị mất
   định dạng bảng biểu (chữ chạy liền, không có bảng)?
A: Đây là do máy chưa cài LibreOffice — phần mềm văn phòng miễn phí
   dùng để giữ nguyên bảng/định dạng đậm từ file Word gốc. Tải và
   cài (miễn phí, ~5 phút) tại:
        https://www.libreoffice.org/download/
   Sau khi cài xong, không cần làm gì thêm — chạy lại chương trình
   là tự nhận được LibreOffice và giữ đúng định dạng.


-----------------------------------------------------------------
Có vấn đề gì trong quá trình dùng thử, xin liên hệ lại để được hỗ trợ.
-----------------------------------------------------------------

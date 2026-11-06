# Kiểm tra hoàn thiện Ngày 1

Ngày kiểm tra: 06/11/2026. Mã sinh viên: 2A202603371.

**Phạm vi người dùng đã xác nhận:** chỉ hoàn thiện codelab LLM API trong thư
mục hiện tại; không triển khai bài chính K5 về phân loại spam. Các ghi chú
K5 ở cuối báo cáo chỉ dùng để phân biệt yêu cầu nộp bài.

Trong phạm vi codelab: Task 1–5 và Bonus A–C đã có mã hoàn chỉnh, 9 kiểm thử
gốc đạt. Hai kiểm thử bổ sung xác nhận hỗ trợ `GOOGLE_API_KEY` cho cả hai
bản mã nguồn. Chưa kiểm chứng gọi API thật vì các khóa OpenAI, Gemini và
Anthropic vẫn chưa được cấu hình tại thời điểm xác nhận phạm vi.

## Kết quả ban đầu

- `starter-code/template.py` và `solution-code/solution.py` đã triển khai Task 1–5, Bonus A–C; hai file giống nhau.
- 9/9 kiểm thử có sẵn đạt trên Python 3.12.10 trong `.venv`.
- `pip check`: không có xung đột phụ thuộc.
- Commit local và commit công khai trên repository GitHub đều là `7ef73d8b2d956b9a5ad8368f0d662bc36d379771` tại lúc kiểm tra.
- Chưa có cấu hình API key hợp lệ lúc bắt đầu kiểm tra.
- Chưa có `solution/solution.py`, bài trả lời `exercises.md` hoặc ZIP theo cấu trúc của Lab 1 Assignment.
- LMS hiển thị hai mục bài nộp là “Not started” lúc bắt đầu kiểm tra; đây là trạng thái giao diện, chưa xác minh lịch sử nộp ở hệ thống khác.

## Công việc đã hoàn thiện

- Thêm bài nộp theo giao diện hàm và cấu trúc kết quả của đề LMS, gồm 4 nhiệm vụ và Bonus A–C.
- Hoàn thiện xử lý streaming: chunk rỗng, ba lượt hội thoại hoàn chỉnh, EOF/quit và lỗi giữa chừng.
- Thêm phân tích Bài tập 2.1, tính toán Bài tập 2.2 và giải thích Bài tập 2.3.
- Khôi phục 19 kiểm thử từ bản sao đề; thêm 8 kiểm thử hành vi còn thiếu.
- Thêm hỗ trợ `GOOGLE_API_KEY` cho bài Gemini theo slide.
- Tổng 36/36 kiểm thử đạt, tất cả request bên ngoài trong bộ kiểm thử được mock.
- Thêm công cụ thu thập dữ liệu temperature thật và công cụ tạo ZIP theo danh sách file rõ ràng.

## Phần chưa thể xác nhận hoàn thành

1. Chưa thu thập bốn phản hồi API thật của Bài tập 2.1 trong lần kiểm tra ban đầu. Người dùng đang tự cấu hình khóa trong `.env`; không ghi kết quả giả làm quan sát thật.
2. Chưa chạy thử trực tiếp API Gemini/Anthropic khi chưa có các khóa tương ứng.
3. Chưa nộp ZIP, repository hoặc Google Form; cần phân biệt bài làm đã chuẩn bị với trạng thái hệ thống xác nhận đã nhận bài.
4. Link repository gốc của Lab 1 Assignment trả 404. Xem `assignment_source.md` để biết nguồn phục hồi và giới hạn đối chiếu.

ZIP được chuẩn bị tại `dist/2A202603371_lab_1.zip`. Sau khi bổ sung dữ liệu thật,
chạy lại `tools/package_submission.py` để cập nhật file nộp.

## Cập nhật khi mở mục nộp GitHub

Mục này hiện dẫn tới bài chính K5 về phân loại spam, có yêu cầu notebook và
báo cáo khác với codelab API. ZIP nói trên chỉ áp dụng cho đề API cũ ở mục
Assignment; chưa phải bài nộp hoàn chỉnh của K5. Xem `current_k5_requirements.md`.
Nhãn tiến độ LMS thay đổi sau khi mở mục; chưa thực hiện gửi bài.

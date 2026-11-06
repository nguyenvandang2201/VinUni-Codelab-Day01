# Ngày 1 — Bài tập & Phản ánh

Mã sinh viên: **2A202603371**  
Ngày chuẩn bị: **06/11/2026**

## Phần 1 — Lập trình cốt lõi

`solution.py` triển khai `call_openai`, `call_openai_mini`, `compare_models`,
`streaming_chatbot` và Bonus A–C. Hàm gọi API trả về `(response_text, latency)`
theo đề nộp LMS. Chatbot giữ ba cặp user/assistant gần nhất; yêu cầu tiếp theo
nhận sáu tin nhắn lịch sử cùng câu hỏi mới. Các kiểm thử dùng mock, không phát
sinh request tính phí.

## Bài tập 2.1 — Độ nhạy của temperature

**Prompt:** “Hãy kể cho tôi một sự thật thú vị về Việt Nam.”  
**Các mức cần thử:** 0.0, 0.5, 1.0 và 1.5.

### Quy luật qua bốn phản hồi (phân tích dự kiến)

Khi giữ các tham số khác cố định, temperature thấp thường cho cách diễn đạt
ổn định hơn, còn temperature cao thường tăng sự đa dạng của lựa chọn từ và
cách kể. Ở mức 1.5, câu trả lời có thể mới lạ hơn nhưng cần kiểm chứng kỹ hơn;
temperature 0 cũng không bảo đảm kết quả hoàn toàn xác định hay đúng sự thật.
Đây là nhận định lý thuyết, chưa phải quan sát từ bốn lần gọi API thực tế.

### Thiết lập cho chatbot hỗ trợ khách hàng

Tôi chọn temperature khoảng **0.2** làm điểm khởi đầu để ưu tiên tính nhất
quán khi giải đáp chính sách, sản phẩm và quy trình. Cần đánh giá trên bộ câu
hỏi thực tế, cung cấp nguồn thông tin đáng tin cậy và cho chatbot chuyển đến
nhân viên khi thiếu dữ kiện; giảm temperature không tự loại bỏ câu trả lời sai.

### Trạng thái thực nghiệm

Chưa có `OPENAI_API_KEY` trong môi trường kiểm tra nên chưa thu thập phản hồi,
độ trễ và token usage thật. Không dùng dữ liệu mock làm bằng chứng thực nghiệm.
Chạy từ thư mục gốc sau khi tự cấu hình key trong `.env`:

```powershell
.\.venv\Scripts\python.exe tools/run_temperature_experiment.py
```

Script sẽ gọi GPT-4o ở bốn mức trên với `top_p=1.0`, lưu câu trả lời cùng
usage thật tại `reports/temperature_results.json`. Cần đọc các kết quả đó
và bổ sung quan sát thực tế trước khi coi phần thực nghiệm là hoàn thành.

## Bài tập 2.2 — Đánh đổi chi phí

### Ước tính workload

Để áp dụng đúng bảng giá **output-only trong đề**, tôi giả định 350 token/lần
đều là token đầu ra. Nếu 350 là tổng input + output, phải biết tỷ lệ từng loại
để tính chi phí hóa đơn; đề chưa cung cấp tỷ lệ đó.

- Số lần gọi/ngày: `10.000 × 3 = 30.000`.
- Token đầu ra/ngày: `30.000 × 350 = 10.500.000`.
- GPT-4o: `10.500.000 / 1.000 × 0,010 = 105 USD/ngày`.
- GPT-4o-mini: `10.500.000 / 1.000 × 0,0006 = 6,30 USD/ngày`.
- Tỷ lệ: `105 / 6,30 ≈ 16,67 lần`; chênh lệch `98,70 USD/ngày`.
- Với 30 ngày và workload không đổi: `3.150 USD` so với `189 USD`.

Đây là kết quả theo giả định và đơn giá cố định của đề, không phải báo giá
API hiện hành. Nó chưa gồm input token, retry hay các chi phí khác.

### Khi nào chọn từng model?

Chi phí GPT-4o có thể xứng đáng cho yêu cầu phân tích nhiều tài liệu và tổng
hợp lập luận phức tạp, nếu kiểm thử thực tế cho thấy chất lượng tốt hơn đủ
để giảm công sửa sai. GPT-4o-mini phù hợp hơn với tác vụ khối lượng lớn có
đầu ra ngắn, tiêu chí rõ ràng, chẳng hạn phân loại câu hỏi hỗ trợ hoặc soạn
phản hồi FAQ từ thông tin đã được cung cấp. Có thể dùng mini trước rồi chuyển
những ca khó sang model lớn, dựa trên đánh giá chất lượng và chi phí đo được.

## Bài tập 2.3 — Trải nghiệm người dùng với streaming

Streaming hữu ích nhất cho chatbot tương tác và câu trả lời dài vì người dùng
có thể đọc phần đầu ngay khi nó xuất hiện, giảm thời gian chờ cảm nhận và cho
phép ngắt phản hồi sớm. Nó không bảo đảm giảm tổng thời gian sinh hoặc tổng
chi phí. Non-streaming phù hợp hơn cho xử lý nền, phân loại hàng loạt hoặc
đầu ra JSON cần kiểm tra đầy đủ trước khi lưu hay hiển thị. Với streaming,
ứng dụng cần xử lý các chunk rỗng, lỗi giữa chừng và chỉ lưu những lượt hội
thoại hoàn chỉnh vào lịch sử; với thông tin cần rà soát trước khi công bố,
nên giữ kết quả lại để kiểm tra thay vì hiển thị ngay từng phần.

## Danh sách kiểm tra

- [x] Triển khai `call_openai` và `call_openai_mini`.
- [x] Triển khai cấu trúc kết quả `compare_models` theo đề LMS.
- [x] Triển khai streaming và giới hạn ba lượt hội thoại hoàn chỉnh.
- [x] Triển khai retry, batch compare và bảng kết quả.
- [x] Điền phần phân tích, tính toán chi phí và streaming UX.
- [ ] Chạy bốn lần gọi API thật và bổ sung quan sát cho Bài tập 2.1.
- [ ] Xác nhận điểm/kết quả sau khi nộp bài lên LMS.

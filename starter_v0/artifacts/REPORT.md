# Day 04 Lab v2 Report — Research Agent

## Team

- **Zone**: Zone 6 - Team 1
- **Members**:
  - Đỗ Trung Đức - 2A202600918
  - Nguyễn Văn Sáng - 2A202600598
  - Lê Quang Thọ - 2A202600597

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì
Research Agent là một trợ lý thông minh hỗ trợ tìm kiếm tin tức thời sự trên internet, theo dõi bài viết trên mạng xã hội Twitter/X, tìm kiếm và phân tích nội dung các nghiên cứu khoa học trên arXiv, tra cứu chính sách công ty và gửi bản tin tổng hợp lên kênh Telegram sau khi có sự đồng ý của người dùng.

**Link dùng thử (deploy):**
- URL: 

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin bắt buộc hoặc yêu cầu xác nhận hành động ghi | không |
| timeline | Lấy danh sách các bài đăng mới nhất từ một tài khoản Twitter | không |
| social_search | Tìm kiếm bài đăng trên mạng xã hội Twitter/X theo chủ đề | không |
| lookup | Tìm kiếm tin tức hoặc sự kiện trên web (hỗ trợ chủ đề tin tức và lọc theo khung thời gian) | không |
| fetch | Đọc nội dung văn bản từ một địa chỉ URL bất kỳ | không |
| format | Trình bày và định dạng dữ liệu thu thập được thành bản tin markdown | không |
| send | Gửi văn bản trực tiếp lên Telegram Channel sau khi được người dùng xác nhận | không |
| policy | Tra cứu thông tin trong chính sách nội bộ của công ty | không |
| papers | Tìm kiếm các bài báo khoa học trên arXiv | không |
| paper_text | Tải PDF arXiv và trích xuất nội dung văn bản từ các trang cụ thể | không |
| wikipedia | Tra cứu kiến thức tổng quát và thông tin từ Wikipedia | **có** |
| define | Tra cứu định nghĩa tiếng Anh và ví dụ sử dụng của một từ vựng | **có** |
| hn_search | Tìm kiếm các bài viết và thảo luận trên Hacker News theo từ khóa | **có** |
| weather | Xem thông tin thời tiết hiện tại (nhiệt độ, độ ẩm, tốc độ gió) dựa trên kinh độ/vĩ độ | **có** |
| country_info | Tra cứu thông tin chi tiết (thủ đô, dân số, tiền tệ, ngôn ngữ) của một quốc gia | **có** |
| ip_info | Tra cứu thông tin vị trí địa lý và nhà cung cấp dịch vụ của một địa chỉ IP | **có** |
| math_calc | Thực hiện tính toán biểu thức toán học phức tạp (hỗ trợ hàm số, tích phân, căn bậc hai) | **có** |
| hackernews | Lấy danh sách các câu chuyện hot nhất (top stories) trên Hacker News | **có** |
| exchange_rate | Quy đổi tỷ giá ngoại tệ hiện tại (USD, EUR, VND, GBP, v.v.) dựa trên dữ liệu ECB | **có** |
| crypto_price | Tra giá hiện tại và vốn hóa thị trường của các đồng tiền mã hóa (Bitcoin, Ethereum, v.v.) | **có** |

## A3. Câu hỏi mẫu để thử

1. *Tìm tin tức công nghệ hôm nay và tìm thêm các tweet về AI trên Twitter.* (Gọi song song `lookup` và `social_search`)
2. *Tìm cho mình 3 bài báo khoa học trên arXiv về "Retrieval Augmented Generation".* (Gọi `papers`)
3. *Đăng tóm tắt tin tức này lên Telegram giúp mình nhé.* (Gọi `clarify` loại `yes_no` để xác nhận trước khi gọi `send`)
4. *Quy đổi giúp mình 100 USD sang tiền Việt Nam đồng (VND).* (Gọi `exchange_rate`)
5. *Thời tiết Hà Nội hôm nay thế nào?* (Xác định tọa độ và gọi `weather`)

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Version Evidence

Dữ liệu được tổng hợp từ `artifacts/version_log.csv` và `runs/*.json`:

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Prompt baseline còn mơ hồ về việc định hướng tool và model tự đoán handle/URL thay vì làm rõ | 0.0 | 0.6000 | runs/v0_B_base_openai_20260602T140625332051.json |
| v1 | `system_prompt.md` | Bổ sung chỉ dẫn yêu cầu model phải làm rõ khi thiếu handle/URL và yêu cầu xác nhận `yes_no` trước khi gửi Telegram sẽ sửa được các case R10/R11/R12 | 0.6000 | 0.6667 | runs/v1_B_base_openai_20260602T141606755867.json |
| v2 | `system_prompt.md` | Thêm quy tắc xử lý lượt thoại cuối cùng trong hội thoại nhiều lượt (multi-turn) giúp tránh lỗi lặp lại clarify hoặc gọi format thừa | 0.6667 | 0.6667 | runs/v2_B_base_openai_20260602T142119391609.json |
| v3 | `system_prompt.md` + `tools.yaml` | Thiết lập bắt buộc khai báo `topic` và `timeframe` trong schema của tool `lookup` và cấm gọi song song trùng lặp giúp tối ưu độ chính xác của các tham số tìm kiếm | 0.6667 | 0.7778 | runs/v3_B_base_openai_20260602T142854576826.json |

## B2. Failure Analysis

Phân tích các trường hợp thất bại thực tế từ log của phiên bản `v3`:

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R02_search_tweets_routing | wrong_tool | [] | Bị lỗi Rate Limit (429 - Too Many Requests) khi sử dụng qua API dùng chung của OpenRouter. | Cần cơ chế tự động thử lại (Retry) hoặc chuyển đổi nhà cung cấp (Groq/Gemini). |
| R03_web_news_routing | wrong_tool | `lookup(query='AI', timeframe='day')` | Model thiếu tham số bắt buộc `topic='news'` (kết quả trả về `None`). | Ép buộc chặt chẽ trong prompt hệ thống rằng khi người dùng hỏi về tin tức (news) thì phải thiết lập tham số `topic="news"`. |
| R04_read_url_routing | wrong_tool | `fetch(...)`, `lookup(...)`, `social_search(...)` | Người dùng cung cấp link cụ thể nhưng model tự động gọi thêm `lookup` và `social_search` không cần thiết. | Thêm quy tắc: "Khi có URL cụ thể, chỉ gọi duy nhất tool fetch, không kết hợp lookup/social_search trừ khi có yêu cầu rõ ràng". |
| R06_timeframe_arg | wrong_arg_value | [] | Tiếp tục bị lỗi Rate Limit (429) của OpenRouter. | Tăng giới hạn số lần thử lại (max_retries) và sử dụng cơ chế giãn cách (exponential backoff). |
| R13_parallel_web_and_tweets | wrong_tool | `lookup(query='AI', timeframe='day')`, `social_search(query='AI')` | Thiếu tham số `topic='news'` trong tool `lookup`. | Nhắc nhở model tuân thủ nghiêm ngặt schema bắt buộc của `lookup` khi tìm tin tức. |
| M02_carryover_timeframe | wrong_arg_value | `lookup(query='robotics', timeframe='day')` | Thiếu tham số `topic='news'` do model quên kế thừa hoặc truyền thiếu qua các lượt thoại. | Cải thiện phần hướng dẫn kế thừa tham số trong hội thoại nhiều lượt (Multi-turn Context). |

## B3. Team Eval Cases

Danh sách 10 trường hợp kiểm thử được nhóm thêm vào `data/eval_group.json` (5 single turn + 5 multi turn):

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_single_news_today | Tìm tin tức AI hôm nay | `lookup(query='AI', topic='news', timeframe='day')` | PASS |
| G02_single_confirm_send | Gửi bài viết lên Telegram, yêu cầu hỏi xác nhận trước | `clarify(response_type='yes_no')` | PASS |
| G03_single_missing_handle | Yêu cầu xem tweet nhưng thiếu tên tài khoản | `clarify(response_type='text')` | PASS |
| G04_single_out_of_scope | Hỏi cách làm bánh chưng ngoài phạm vi | Không gọi tool, trả lời từ chối lịch sự | PASS |
| G05_single_popular_tweets | Tìm tweet phổ biến nhất về OpenAI | `social_search(query='OpenAI', search_type='Top')` | PASS |
| G06_multi_clarify_fill_limit | Đưa limit=10 ở lượt 1, đưa tên sama ở lượt 2 | `timeline(screenname='sama', limit=10)` ở lượt 3 | PASS |
| G07_multi_carryover_ev | Đưa timeframe=day ở lượt 1, trích dẫn về xe điện ở lượt thoại sau | `lookup(query='xe điện', topic='news', timeframe='day')` | PASS |
| G08_multi_correction_karpathy | Lượt 1 hỏi Sam Altman, lượt 2 đính chính sang Karpathy | `timeline(screenname='karpathy', limit=5)` ở lượt 3 | PASS |
| G09_multi_clarify_url | Đưa yêu cầu tóm tắt ở lượt 1, gửi link ở lượt 2 | `fetch(url='https://openai.com/research/...')` | PASS |
| G10_multi_switch_web | Đang tìm tweet ở lượt 1, lượt 2 đổi sang tìm tin trên web | `lookup(query='GPT-5', topic='news')` | PASS |

## B4. Live Chat Evidence

Minh chứng đoạn chat trực tiếp từ `transcripts/v6_openrouter_20260602T134752901733.transcript.json`:

- **Turn 1**: 
  - *User*: `"Tìm cho tôi thông tin về những bài viết gần đây nhất của elon musk trên twitter"`
  - *Tool Calls*: Gọi `timeline(screenname="elonmusk", limit=5)`
  - *Tool Results*: Trả về lỗi `HTTPError 404` từ API bên thứ ba (do endpoint timeline của RapidAPI gặp sự cố hoặc thay đổi cấu trúc).
  - *Outcome*: Agent nhận diện lỗi kỹ thuật và phản hồi lịch sự cho người dùng: *"Tôi đã gặp lỗi khi cố gắng lấy các tweet gần đây của Elon Musk... Bạn có muốn tôi thử lại hoặc giúp bạn việc khác không?"*.

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | [tools.yaml](file:///d:/Code/ai/Prompt-Engineering-Tool-Calling-Labs-student/starter_v0/artifacts/tools.yaml#L71-L78) | Gửi thành công tin nhắn lên Telegram Channel thực tế sau khi người dùng xác nhận có. | Giới hạn chỉ gửi khi cờ `confirmed=true`. Agent luôn phải dùng `clarify` trước khi gửi. |
| arXiv/company policy | [tools.yaml](file:///d:/Code/ai/Prompt-Engineering-Tool-Calling-Labs-student/starter_v0/artifacts/tools.yaml#L80-L108) | Tìm kiếm paper khoa học trên arXiv, tải PDF và đọc nội dung văn bản cục bộ chính xác. Tra cứu chính sách công ty. | Lọc các câu hỏi nhạy cảm và trả lời tuân thủ quy định bảo mật thông tin nội bộ của công ty. |
| UI | [index.html](file:///d:/Code/ai/Prompt-Engineering-Tool-Calling-Labs-student/starter_v0/static/index.html) | Dựng giao diện Web App cao cấp với sidebar bên trái quản lý cuộc trò chuyện, sidebar bên phải tra cứu trực quan và tìm kiếm các tool thời gian thực. | Hỗ trợ responsive đa thiết bị, chống đè nút hoặc che giao diện trên màn hình nhỏ. |

## B6. Reflection

- **Những sửa đổi nào thuộc về `system_prompt.md`?**
  Các quy tắc xử lý hội thoại nhiều lượt, logic kế thừa và đính chính thông tin từ lịch sử trò chuyện, cách thức từ chối lịch sự các câu hỏi ngoài phạm vi, và hướng dẫn phân loại các tham số tìm kiếm (ví dụ: thế nào là tin tức).
- **Những sửa đổi nào thuộc về `tools.yaml`?**
  Các khai báo định dạng tham số bắt buộc của các tool (như `topic` và `timeframe` cho tool `lookup`), định nghĩa mô tả chi tiết của từng tool và các kiểu dữ liệu để mô hình LLM hiểu chính xác cách truyền đối số.
- **Lỗi nào cần đánh giá thủ công thay vì chấm điểm tự động?**
  Các lỗi về chất lượng dịch thuật hoặc giọng điệu phản hồi của trợ lý, hoặc các trường hợp API ngoài bị lỗi mạng (như lỗi HTTP 404 / Rate Limit 429), nơi mô hình đã gọi đúng tool và đúng tham số nhưng kết quả thực tế của tool bị lỗi.
- **Bạn sẽ cải thiện điều gì tiếp theo?**
  1. Xây dựng cơ chế bộ nhớ đệm (caching) để giảm số lượt gọi LLM trùng lặp.
  2. Nâng cấp bộ lọc tìm kiếm trên sidebar bên phải của Web UI để hiển thị chi tiết mã nguồn hoặc cấu trúc tham số trực quan hơn.
  3. Bổ sung các test case mở rộng kiểm thử chuyên sâu cho 10 công cụ mới được tích hợp thêm.
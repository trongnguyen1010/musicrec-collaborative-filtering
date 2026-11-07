# ruff: noqa: E501, F821
# Edits outside Chapters 4-5 for report v18 (advisor feedback of 06/11/2026, items G01-G06,
# G31, G32 and the Abstract). Executed by build_v17.py after the chapter rewrites, with the
# helpers body, find_para, fill, para, heading, run_rpr, copy, NS, q, text in scope.


def find_any(prefix):
    for e in body.iter(q("p")):
        if text(e).startswith(prefix):
            return e
    raise KeyError(prefix)


def set_para(prefix, new_text, start=200, anywhere=False):
    p = find_any(prefix) if anywhere else find_para(prefix, start)
    rpr = copy.deepcopy(p.find("w:r/w:rPr", NS))
    color = rpr.find("w:color", NS)
    if color is not None:
        color.set(q("val"), "000000")
    fill(p, new_text, rpr=rpr)
    return p


def drop(prefix):
    p = find_any(prefix)
    p.getparent().remove(p)


def add_after(p, texts):
    for s in texts:
        n = para(s)
        p.addnext(n)
        p = n
    return p


# G01: IFPI and Spotify figures checked (IFPI Global Music Report 2026, 18/03/2026: streaming
# 69,6% of 2025 recorded music revenue, 837 million paid accounts; Spotify Newsroom
# 30/06/2025: 56 million weekly discoveries, 77% from emerging artists). Text already states
# the year of the data; only the advisor note is removed.
drop("GVHD: Kiểm tra lại các số liệu 69,6%")

# G02: 1.2.1, history-length analysis now through Given-N.
set_para(
    "Mỗi người dùng có số lượng nghệ sĩ đã nghe khác nhau",
    "Mỗi người dùng có số lượng nghệ sĩ đã nghe khác nhau. Nếu chỉ xem kết quả trung bình, chúng ta có "
    "thể không nhận ra mô hình gợi ý tốt cho người có lịch sử nghe dài nhưng chưa tốt cho người có lịch sử "
    "nghe ngắn. Tuy nhiên, trong dữ liệu Last.fm HetRec 2011, 1.829 người dùng có đúng 50 nghệ sĩ, nên sau "
    "khi chia tập hầu hết người dùng có cùng độ dài lịch sử huấn luyện và việc chia nhóm theo độ dài lịch "
    "sử không đủ cỡ mẫu. Vì vậy, ảnh hưởng của độ dài lịch sử được khảo sát bằng thí nghiệm Given-N (mục "
    "4.8), trong đó hệ thống chỉ nhận 0, 1, 3 hoặc 5 nghệ sĩ của người dùng; phân tích theo nhóm độ dài "
    "lịch sử chỉ được trình bày dạng mô tả.",
)
drop("GVHD: Câu này cần điều chỉnh")

# G03: RQ2 rewritten as the Given-N question, evidence E6.
set_para(
    "Độ dài lịch sử ảnh hưởng thế nào",
    "Khi số nghệ sĩ đã biết của người dùng giảm (Given-N với N = 0, 1, 3, 5), chất lượng gợi ý của các "
    "phương án thay đổi thế nào?",
    anywhere=True,
)
set_para(
    "Chỉ số theo nhóm lịch sử và phân bố",
    "Kết quả E6 theo N; phân tích mô tả theo nhóm lịch sử và theo từng người dùng.",
    anywhere=True,
)
add_after(
    find_para("Các câu hỏi trên được tách để tránh gộp", 200),
    [
        "RQ2 và RQ4 dùng chung thí nghiệm Given-N nhưng trả lời hai khía cạnh khác nhau: RQ2 xem xu hướng "
        "của các phương án khi số nghệ sĩ đã biết thay đổi, còn RQ4 xem M2 có vượt phương án chỉ dựa vào "
        "mức phổ biến hay không."
    ],
)
drop("GVHD: Đề nghị sửa nội dung RQ2")

# G04: section numbers 1.6 / 1.7 and the statistical tests.
for old, new in [
    ("1.7 Phương pháp thực hiện", "1.6 Phương pháp thực hiện"),
    ("1.6 Cấu trúc báo cáo", "1.7 Cấu trúc báo cáo"),
]:
    h = find_para(old, 200)
    fill(h, new, rpr=copy.deepcopy(h.find("w:r/w:rPr", NS)))
add_after(
    find_para("Phương pháp chính là thực nghiệm và đánh giá", 200),
    [
        "Vì các mô hình được đánh giá trên cùng nhóm người dùng, khác biệt giữa hai mô hình được kiểm định "
        "theo cặp trên NDCG@10 của từng người dùng bằng kiểm định Wilcoxon có dấu [27]; khi có nhiều cặp so "
        "sánh, giá trị p được hiệu chỉnh theo phương pháp Holm [28], và khoảng tin cậy 95% được ước lượng "
        "bằng bootstrap theo người dùng [29]."
    ],
)
drop("GVHD: Đổi số mục")

# Delivered interface: Next.js (Streamlit kept as fallback).
set_para(
    "Về mặt ứng dụng, đề tài hướng tới",
    "Về mặt ứng dụng, đề tài hướng tới xây dựng một nguyên mẫu gồm dịch vụ API bằng FastAPI và giao diện "
    "minh họa trên nền web, cho phép chọn người dùng có sẵn hoặc nhập lịch sử nghe và nhận danh sách nghệ "
    "sĩ được đề xuất. Sản phẩm này giúp kiểm tra khả năng chuyển mô hình nghiên cứu thành một luồng sử dụng "
    "cụ thể, đồng thời minh họa kết quả và lý do gợi ý. Việc kết hợp thực nghiệm với nguyên mẫu ứng dụng là "
    "cơ sở để nhóm lựa chọn đề tài, với kết luận về hiệu quả của mô hình và các mô-đun cải tiến được rút ra "
    "sau khi có kết quả kiểm chứng.",
)
set_para(
    "Thứ năm, xây dựng dịch vụ API bằng FastAPI",
    "Thứ năm, xây dựng dịch vụ API bằng FastAPI và giao diện minh họa để người dùng nhập thông tin và nhận "
    "gợi ý nghệ sĩ. Chuẩn bị hướng dẫn sử dụng, cấu hình, hạt giống ngẫu nhiên, tệp mô hình, bảng kết quả "
    "và ví dụ đầu vào, đầu ra để hỗ trợ kiểm tra và chạy lại. Hệ thống cần xử lý rõ các trường hợp đầu vào "
    "không hợp lệ.",
)
set_para(
    "Chương 4: Huấn luyện và thực nghiệm đánh giá.",
    "Chương 4: Huấn luyện và thực nghiệm đánh giá. Trình bày môi trường thực nghiệm, dữ liệu sau tiền xử "
    "lý, quá trình tinh chỉnh tham số trên tập xác thực và kết quả so sánh các mô hình trên tập kiểm thử "
    "kèm kiểm định thống kê. Chương này đánh giá M1, M2 và thực nghiệm mở rộng với implicit ALS, phân tích "
    "kết quả theo từng người dùng, chi phí xử lý và trả lời các câu hỏi RQ1 đến RQ4.",
)
set_para(
    "Chương 5: Xây dựng hệ thống và kết luận.",
    "Chương 5: Xây dựng hệ thống và kết luận. Mô tả cách tổ chức mã nguồn, nạp gói mô hình, dịch vụ API "
    "bằng FastAPI và giao diện minh họa bằng Next.js. Chương này trình bày kết quả kiểm thử chức năng, đối "
    "chiếu kết quả trên ứng dụng với đánh giá ngoại tuyến (RQ5) và thời gian phản hồi. Phần cuối tổng kết "
    "mức độ đạt mục tiêu, những hạn chế và hướng phát triển của đề tài.",
)
set_para(
    "Phần tài liệu tham khảo liệt kê",
    "Phần tài liệu tham khảo liệt kê các công trình và nguồn thông tin được trích dẫn trong báo cáo. Các phụ "
    "lục bổ sung quy ước cấu hình, tệp kết quả và ví dụ kiểm tra bộ đánh giá.",
)
set_para(
    "Bản báo cáo hiện còn",
    "Chúng em mong nhận được góp ý của thầy cô để tiếp tục hoàn thiện cách triển khai và diễn giải, đồng "
    "thời chịu trách nhiệm kiểm tra các nội dung trước khi nộp bản cuối cùng.",
    start=0,
)

# G05 (partial): implicit ALS paragraph and what M1 takes from MMR and Abdollahpouri.
# The "related studies on Last.fm HetRec 2011" section still needs source reading.
add_after(
    find_para("Cremonesi và cộng sự [13] nghiên cứu PureSVD"),
    [
        "Phân rã ma trận cho phản hồi ngầm (implicit ALS) của Hu, Koren và Volinsky [8] xử lý trực tiếp dữ "
        "liệu như số lượt nghe. Mỗi ô của ma trận được tách thành sở thích nhị phân (người dùng có nghe nghệ "
        "sĩ hay không) và độ tin cậy tăng theo số lượt nghe. Hàm mất mát là tổng sai số bình phương giữa sở "
        "thích và tích hai véc-tơ nhân tố, có trọng số bằng độ tin cậy, cộng thành phần điều chuẩn. Khác với "
        "SVD có độ lệch, hàm mất mát này tính trên cả các ô chưa quan sát, với độ tin cậy thấp nhất, nên phù "
        "hợp với việc chưa nghe không có nghĩa là không thích. Các nhân tố được học bằng bình phương tối "
        "thiểu luân phiên: cố định nhân tố nghệ sĩ để giải nhân tố người dùng, rồi ngược lại. Khóa luận dùng "
        "implicit ALS trong một thực nghiệm mở rộng ở Chương 4."
    ],
)
add_after(
    find_para("Tái xếp hạng (re-ranking) là bước điều chỉnh"),
    [
        "M1 kế thừa hai ý tưởng từ các công trình này. Từ MMR [18], M1 lấy cách chọn tuần tự: ở mỗi bước, "
        "nghệ sĩ được chọn là nghệ sĩ có điểm cao nhất khi cân bằng mức liên quan với độ tương đồng lớn nhất "
        "so với các nghệ sĩ đã chọn, với trọng số λ. Từ Abdollahpouri và cộng sự [19], M1 lấy ý tưởng thêm "
        "một thành phần phạt theo mức phổ biến khi tái xếp hạng để tăng cơ hội cho nghệ sĩ ít phổ biến, với "
        "trọng số β. Khác với [19], mức phạt của M1 giống nhau cho mọi người dùng, không cá nhân hóa theo "
        "mức ưa chuộng nghệ sĩ phổ biến của từng người."
    ],
)

# G06: 3.7.3, pre-declared threshold stated as done, pointer to the circularity note in 4.7.
set_para(
    "Tham số được chọn trên tập xác thực. Nhóm dự kiến",
    "Tham số được chọn trên tập xác thực. Nhóm đặt trước mức giảm NDCG@10 tương đối tối đa 5% so với mô "
    "hình nền để xem xét lợi ích về đa dạng và mức phổ biến; đây là ngưỡng thiết kế, không phải kết quả. "
    "Vì hàm lựa chọn của M1 dùng cùng độ tương đồng với chỉ số ILD và cùng số người nghe với chỉ số ARP, "
    "kết quả M1 được đọc cùng các thước đo độc lập ở mục 4.7.",
)
drop("GVHD: Xem lưu ý về tính vòng tròn")

# G31: references [31]-[38] added; every entry [1]-[38] is cited in the body (checked by script).
drop("GVHD: Tài liệu tham khảo:")

# G32: remove Appendix C (working document) up to the section properties.
kids = list(body)
c_start = kids.index(find_para("PHỤ LỤC C MA TRẬN TRUY VẾT"))
for e in kids[c_start:]:
    if e.tag != q("sectPr"):
        body.remove(e)

# Abstract page (faculty template: English abstract with keywords before the acknowledgements).
thanks = find_para("LỜI CẢM ƠN", 0)
abstract_title = copy.deepcopy(thanks)
fill(abstract_title, "ABSTRACT", rpr=copy.deepcopy(thanks.find("w:r/w:rPr", NS)))
thanks.addprevious(abstract_title)
add_after(
    abstract_title,
    [
        "**MusicRec: A collaborative filtering-based music artist recommendation system**",
        "Online music services offer catalogues far larger than any listener can explore, so recommender "
        "systems help users find artists that match their taste. This thesis builds and evaluates an artist "
        "recommender based on collaborative filtering, using listening counts from the Last.fm HetRec 2011 "
        "dataset as implicit feedback.",
        "After cleaning, the data contain 1,877 users and 92,801 user-artist pairs, split per user into "
        "training, validation and test sets. Six comparison models (Random, Popularity, user-based and "
        "item-based collaborative filtering, biased SVD and PureSVD) were tuned on the validation set by "
        "NDCG@10 and locked before the test set was opened. Two modules were added: M1, a greedy re-ranker "
        "in the spirit of maximal marginal relevance with a popularity penalty, and M2, a hybrid fallback for "
        "new users that combines item-based scores, artist tags and popularity, evaluated with a Given-N "
        "protocol. Implicit ALS was run as an extension. Evaluation used ranking and beyond-accuracy metrics "
        "with paired Wilcoxon tests, Holm correction and bootstrap intervals.",
        "On the test set, PureSVD achieved the highest NDCG@10 among the six models (0.1828 against 0.0688 "
        "for Popularity, a significant difference), while the neighbourhood models and biased SVD did not "
        "beat Popularity. M1 reduced average recommendation popularity by 15.69% with no significant change "
        "in NDCG@10. M2 did not outperform Popularity for new users, although it widened catalogue coverage. "
        "Implicit ALS reached 0.2175, significantly above PureSVD. The models were packaged as a FastAPI "
        "service with a Next.js interface whose recommendation lists match the offline evaluation exactly, "
        "with median response times between 3.8 and 11.5 ms on a personal computer.",
        "**Keywords:** music recommendation, collaborative filtering, implicit feedback, popularity bias, "
        "cold start, Last.fm.",
    ],
)

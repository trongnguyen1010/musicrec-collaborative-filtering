# Hướng dẫn theo dõi tiến độ hai thành viên

## Khuyến nghị

Dùng **GitHub Issues + GitHub Projects + Pull Requests + Actions** làm công cụ theo dõi chính.
Project đã ở trên GitHub, có CI và PR template, nên cách này liên kết trực tiếp task → code → review
→ test mà không phát sinh một hệ thống vận hành khác. MLflow chỉ theo dõi thí nghiệm ML, không thay
task board.

GitHub Projects hỗ trợ iteration theo tuần, custom fields, table/board/roadmap, automation và chart.
Required status checks có thể chặn merge khi CI chưa pass. Với hai người, chưa cần Jira/Trello hoặc
tự xây web dashboard.

## Bước 1 — Tạo Project

1. Trên GitHub, chọn profile/organization → **Projects** → **New project** → Table.
2. Đặt tên `MusicRec Thesis — 2026` và link repository trong description/settings.
3. Tạo Iteration một tuần, bắt đầu 2026-09-07, sinh đủ 12 iterations.
4. Bật workflow: item mới thành `Todo`; issue đóng thành `Done`.

## Bước 2 — Tạo field chuẩn

| Field | Kiểu | Giá trị |
| --- | --- | --- |
| Status | Single select | Backlog, Ready, In Progress, Review, Blocked, Done |
| Iteration | Iteration | Week 1 ... Week 12 |
| Owner | Assignee | Một owner duy nhất |
| Reviewer | Text/assignee | Thành viên còn lại |
| Area | Single select | Data, Evaluation, Model, MLOps, API, UI, Docs |
| Priority | Single select | P0, P1, P2 |
| Estimate | Number | 1, 2, 3, 5, 8 |
| Actual | Number | Ghi sau nghiệm thu để cải thiện estimate |
| Risk | Single select | Low, Medium, High |
| Evidence | Text | PR, MLflow run, report hoặc artifact |

Không tạo field `% complete` tự nhập. Tiến độ được tính từ accepted points của item Done để tránh
tình trạng “90%” kéo dài.

## Bước 3 — Tạo view

1. **Current week:** filter `iteration:@current`, board theo Status, sort Priority.
2. **By member:** các item chưa Done, group Owner, hiện tổng Estimate.
3. **Blocked:** filter `status:Blocked`, sort Priority/target date.
4. **Review queue:** filter `status:Review`, group Reviewer.
5. **Roadmap:** 12 iterations và milestones.
6. **Quality debt:** label `tech-debt` hoặc `bug`, group Area.

Giới hạn WIP: mỗi người tối đa **một item In Progress**. PR nhỏ có CI xanh không nên chờ review quá
một ngày làm việc.

## Bước 4 — Chuẩn hóa Issue

```markdown
## Mục tiêu / milestone / research question

## Phạm vi
- In scope:
- Out of scope:

## Cách thực hiện dự kiến

## Acceptance criteria
- [ ] Đầu ra cụ thể ...
- [ ] Test ...
- [ ] Quality gates pass
- [ ] Docs/config/ADR cập nhật nếu cần

## Dependency
- Blocked by #...

## Evidence khi hoàn thành
- PR:
- Command/test output:
- MLflow run / artifact / screenshot:
```

Task experiment phải ghi dataset hash, config hash, seed, candidate protocol và metric. Task bug
phải có cách tái lập và regression test.

## Bước 5 — Nối Issue, PR và CI

- Branch chứa issue number, ví dụ `feat/42-item-cf`.
- PR ghi `Closes #42` để issue tự đóng sau merge.
- Bảo vệ `main`: require PR, một approval và required CI job `quality`.
- Bật dismiss stale approval khi có commit mới nếu repository settings hỗ trợ.
- Thêm `.github/CODEOWNERS` sau khi có đúng GitHub username của hai thành viên.

Không đoán username trong `CODEOWNERS`: GitHub chỉ request review khi account hợp lệ và có write
permission.

## Bước 6 — Dashboard và báo cáo tuần

Tạo ba chart:

1. accepted points theo iteration/owner — để nhìn throughput, không xếp hạng cá nhân;
2. items theo Status — để nhìn carry-over, blocker và review queue;
3. Estimate theo Area — để tránh làm nhiều model nhưng thiếu data/evaluation/test.

Mẫu weekly review:

```markdown
# Weekly review — Week N

- Planned / accepted / carry-over points: ... / ... / ...
- Milestone: Green | Yellow | Red
- CI / tests / coverage: ...
- Reproducibility: pass/fail; command/run ID: ...
- Completed evidence: #issue / #PR / MLflow run ...
- Blockers và owner/date: ...
- Escaped defects/rework: ...
- Decisions/ADR: ...
- Next commitment (<= 80% capacity): ...
```

Theo dõi planned/accepted points, carry-over ratio, tuổi blocker, review turnaround, CI first-pass
rate, escaped defects, reproducibility pass/fail và milestone forecast. Không dùng số commit, dòng
code hay thời gian online để đánh giá đóng góp.

## Checker tự động phiên bản nhỏ

Nên dùng board thủ công hai tuần trước để biết nhóm thật sự thiếu báo cáo nào. Sau đó viết một script
dùng GitHub CLI/API, đọc Project/Issues và sinh `reports/progress/week-N.md`; không tạo database mới.

Checker v1 nên phát hiện:

- item In Progress/Review/Done thiếu owner, iteration, estimate hoặc acceptance criteria;
- Done không có merged PR/CI success;
- WIP > 1/người, review quá hạn, blocker quá hai ngày;
- dependency chưa Done nhưng downstream đã In Progress;
- tổng estimate hai người lệch quá 30% trong tuần;
- experiment thiếu MLflow run/data hash/config hash;
- xuất JSON và Markdown; chỉ trả exit code lỗi cho governance P0.

Có thể tạo scheduled GitHub Action chạy chiều Chủ nhật và upload/comment báo cáo. Token chỉ cấp
quyền đọc metadata cần thiết; tuyệt đối không commit personal access token. Nếu Project thuộc
organization/private repository, kiểm tra quyền API trước khi viết script.

## Nguồn chính thức

- [GitHub Projects quickstart](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects)
- [GitHub Projects best practices](https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
- [GitHub iteration fields](https://docs.github.com/en/issues/planning-and-tracking-with-projects/understanding-fields/about-iteration-fields)
- [GitHub Project charts](https://docs.github.com/en/issues/planning-and-tracking-with-projects/viewing-insights-from-your-project/configuring-charts)
- [GitHub required status checks](https://docs.github.com/en/pull-requests/reference/status-checks)
- [GitHub CODEOWNERS](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

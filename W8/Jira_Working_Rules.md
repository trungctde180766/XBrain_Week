# 📋 Jira Working Rules — Xbrain Accelerator

> Mục tiêu: mỗi group tự quản lý công việc qua Jira theo tác phong **agile thật**. Mỗi học viên **mỗi ngày phải thể hiện được mình đang làm gì và đóng góp gì**. Jira là **bằng chứng đóng góp** của từng cá nhân — làm input cho Evidence Pack và Friday presentation.

---

## 1. Thiết lập Project (mỗi group 1 project)

- Loại project: **Team-managed project**
- Template: **Kanban** (hoặc **Scrum** nếu group muốn chạy sprint 1 tuần)
- Board hiển thị theo workflow ở mục 3
- Bật **Backlog** để chứa việc chưa bắt đầu

---

## 2. Issue Types — dùng đúng loại

| Issue type | Khi nào dùng |
|------------|--------------|
| **Story** | Một mục tiêu/đầu việc lớn có giá trị (vd: "Dựng Network Firewall với stateful inspection") |
| **Task** | Việc cụ thể, làm xong trong 1–2 ngày |
| **Sub-task** | Bước nhỏ kiểm chứng được, nằm trong Story/Task |
| **Bug** | Lỗi cần sửa (lab fail, cấu hình sai...) |

> Story lớn **bắt buộc** tách thành Sub-task — thay cho Checklist bên Trello.

---

## 3. Workflow / Statuses

Board tối thiểu có 5 cột (status):

- **Backlog** — đã xác định, chưa bắt đầu
- **To Do** — cam kết làm trong tuần/sprint
- **In Progress** — đang làm (**WIP limit: tối đa 2 issue/người** cùng lúc)
- **In Review** — chờ PM/trainer review hoặc đang **Blocked**
- **Done** — hoàn thành theo Definition of Done

> PM được thêm status phụ nhưng **không bỏ 5 status lõi**.

---

## 4. Quy tắc tạo Issue

Mỗi issue **bắt buộc** có đủ:

- **Summary rõ ràng**: `[Mảng] Mô tả ngắn` — vd: `[Network] Cấu hình route table cho stateful inspection`
- **Assignee**: ai chịu trách nhiệm chính — *không có issue vô chủ (unassigned)*
- **Due date**: deadline dự kiến
- **Label** theo loại việc (xem mục 6)
- (Tùy chọn) **Story Points** nếu group chạy Scrum để ước lượng độ lớn

---

## 5. ⭐ Rule quan trọng nhất — Daily Update

**Mỗi học viên, mỗi ngày làm việc, phải để lại dấu vết trên Jira trước [vd: 21:00].** Một trong hai cách:

### a) Comment cập nhật trên issue đang làm, theo format:

```
📅 [Ngày]
✅ Hôm nay làm: ...
🔜 Mai làm: ...
⛔ Vướng (nếu có): ...
```

### b) Chuyển status issue (To Do → In Progress → In Review → Done) — coi như đã có hoạt động.

> **Nguyên tắc: "No trace = no work".** Việc không thể hiện trên Jira được xem như chưa làm khi đánh giá đóng góp. Jira log lại toàn bộ activity, nên bằng chứng là tự động và minh bạch.

---

## 6. Hệ thống Label

| Label | Ý nghĩa |
|-------|---------|
| `Blocker` | Đang kẹt, cần hỗ trợ gấp (có thể set thêm Priority = Highest) |
| `Need-Review` | Cần PM/trainer check |
| `Lab` | Việc thực hành / hands-on |
| `Docs` | Tài liệu, Evidence Pack |
| `Research` | Tìm hiểu, nghiên cứu |

---

## 7. Đóng góp phải có *bằng chứng*

Khi chuyển issue sang **Done**, phải đính kèm ít nhất **1 bằng chứng**:

- **Attachment**: screenshot console AWS / kết quả lab
- **Link / mô tả text**: tới file, diagram, hoặc kết quả — để dạng text/link trong issue thì mới xuất được ra file export
- Comment ngắn "đã làm được gì, kiểm chứng thế nào"

> Done mà không có bằng chứng → issue bị **chuyển về In Review**.

---

## 8. Vai trò của PM (kèm bộ JQL kiểm tra hằng ngày)

PM **không làm hết việc**, mà điều phối. Dùng các **JQL filter** sau (Filters → Advanced search) để check nhanh:

**Issue vô chủ (chưa có assignee):**
```jql
assignee is EMPTY
```

**Ai đã update hôm nay (kiểm tra daily update):**
```jql
updated >= startOfDay() ORDER BY assignee
```

**Issue đang "In Progress" nhưng 1 ngày không động đến (nghi treo việc):**
```jql
status = "In Progress" AND updated <= -1d
```

**Các blocker đang mở:**
```jql
labels = Blocker AND statusCategory != Done
```

**Sắp tới hạn nhưng chưa xong:**
```jql
due <= endOfWeek() AND statusCategory != Done ORDER BY due ASC
```

**Done trong tuần này (gom cho Evidence Pack / Friday):**
```jql
statusCategory = Done AND statusCategoryChangedDate >= startOfWeek()
```

Việc của PM:
- Mỗi sáng chạy filter *vô chủ* + *quá hạn* để dọn board
- Cuối ngày chạy filter *update hôm nay*, đối chiếu danh sách → nhắc ai chưa daily update
- Báo trainer các `Blocker` quá **24h** chưa gỡ
- Cuối tuần dùng filter *Done tuần này* làm input trình bày

---

## 9. Đánh giá (gắn với scoring)

Vào thứ Sáu, mức đóng góp cá nhân nhìn vào:

- Số issue hoàn thành **có bằng chứng** (không tính issue vô chủ hoặc thiếu evidence)
- Tính **đều đặn** của daily update (đứt quãng nhiều ngày bị trừ)
- Việc gỡ blocker / hỗ trợ thành viên khác (chất lượng, không chỉ số lượng)

> Mục tiêu không phải đếm issue cho nhiều, mà là **mỗi người chứng minh được mình đã đóng góp gì thật**.

---

## 10. 🔑 Cơ chế chứng minh cho Trainer (Weekly Export)


> Quy tắc gốc: việc gì muốn được tính phải nằm trong file export. **Không có trong export = không được tính.**

### 10.1. Filter dùng để export

Lưu sẵn 1 saved filter (tên gợi ý: `Weekly Done Export`):

```jql
statusCategory = Done AND statusCategoryChangedDate >= startOfWeek()
ORDER BY assignee ASC, statusCategoryChangedDate DESC
```

### 10.2. Quy trình export (PM làm mỗi thứ Sáu)

1. Vào **Filters → Advanced issue search** → mở filter `Weekly Done Export`
2. Chọn cột hiển thị: **Key, Summary, Assignee, Status, Updated** (+ cột link bằng chứng nếu có)
3. **Export → Export Excel CSV (current fields)**
4. Upload file vào **thư mục SharePoint/Drive của group** và gắn vào **Evidence Pack**

### 10.3. Lưu ý để export có giá trị

- Attachment **không** đi theo file export — nên bằng chứng phải để dưới dạng **link hoặc mô tả text** ngay trong issue (description/comment) thì mới xuất ra được.
- Mỗi issue Done nên có 1 dòng mô tả ngắn "đã làm gì, kiểm chứng ở đâu" để khi trainer đọc file export là hiểu ngay.

---

## ✅ Definition of Done (chuẩn chung)

Một issue chỉ được coi là **Done** khi:

1. Hoàn thành toàn bộ **Sub-task** trong issue
2. Có ít nhất **1 bằng chứng dạng text/link** trong issue (để xuất được ra file export gửi trainer)
3. Được PM hoặc người review xác nhận (không bị trả về In Review)

---

*Xbrain Accelerator — Tech X Corp*

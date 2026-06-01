# Phase 2 — Tin nhắn cho HV Cloud/DevOps

> Gửi sáng T2 01/06/2026.

Chào cả nhà,

Phase 2 bắt đầu hôm nay (T2 01/06) và kéo dài 5 tuần đến T6 03/07. Track Cloud/DevOps có 9 nhóm × 10 HV.

---

## Phase 2 hoạt động thế nào

5 tuần = 2 giai đoạn:
- **W8–W10** (tuần này + 2 tuần sau) — học chuyên sâu Cloud/DevOps: IaC → K8s → GitOps → Observability → Canary → Security
- **W11–W12** — capstone cross-team pod, pitching trước hội đồng ngày 03/07

Nhịp tuần:
- T2–T4: self-study online (~6h/ngày, đọc material + làm exercise + commit cuối ngày)
- T5–T6: onsite Đà Nẵng — lab + show-and-tell

Mỗi HV 1 repo GitHub cá nhân chứa toàn bộ portfolio Phase 2. Khác Phase 1: ít lecture, nhiều self-study — mentor đặt câu hỏi ngược thay vì đưa đáp án luôn, HV tự đọc + tự ra checkpoint evidence.

---

## W8 — Foundation: IaC + K8s

| Ngày | Hoạt động |
|---|---|
| **T2 01/06 (hôm nay)** | Self-study Terraform phần 1 — IaC overview + HCL syntax |
| **T3 02/06** | Self-study Terraform phần 2 — Workflow (Init/Plan/Apply/Destroy) + State Management + Modules + Best Practices<br>**15h–17h: LIVE Terraform với mentor Minh (online)**<br>**17h–18h: Online Test 1** (60p, scope Terraform) |
| **T4 03/06** | Self-study K8s — đọc trước lấy kiến thức nền về Container/Orchestration (Pod, Service, probes, ConfigMap/Secret, NetworkPolicy) |
| **T5 04/06** | **Onsite Đà Nẵng với mentor Nghĩa — dạy K8s Container/Orchestration + scaling/networking/deploy** + bắt đầu Lab "Build minimal K8s platform" |
| **T6 05/06** | Onsite — hoàn thiện Lab → show-and-tell pod 5 người 13h30–15h → **15h–16h: Online Test 2** (60p, scope K8s + Lab) |

---

## Tài liệu tham khảo

### Terraform

Tài liệu chính thống:
- HashiCorp Learn — https://developer.hashicorp.com/terraform/tutorials (start: "Get Started — AWS")
- Terraform Docs — https://developer.hashicorp.com/terraform/docs (reference đầy đủ)
- *Terraform: Up & Running* — Yevgeniy Brikman (O'Reilly) — sách production-grade
- Terraform Best Practices — https://www.terraform-best-practices.com (community-curated)
- Terraform Registry — https://registry.terraform.io (module marketplace)

Series của mentor Nghĩa Huỳnh:
- **Terraform from Basics to Production** — https://kkloudtarus.net/en/blog/series/terraform-from-basics-to-production

### Docker / Containers

Tài liệu chính thống:
- Docker Docs — https://docs.docker.com
- Docker Curriculum — https://docker-curriculum.com (tutorial từ scratch)
- *Docker Deep Dive* — Nigel Poulton
- OCI Image Spec — https://github.com/opencontainers/image-spec (chuẩn image)

Series của mentor Nghĩa Huỳnh:
- **Docker from Basics to Swarm** — https://kkloudtarus.net/en/blog/series/docker-from-basics-to-swarm

### Kubernetes

Tài liệu chính thống:
- Kubernetes Docs — https://kubernetes.io/docs (start: Concepts → Tutorials)
- Kubernetes Basics (interactive) — https://kubernetes.io/docs/tutorials/kubernetes-basics
- CNCF Curriculum (CKA/CKAD reference) — https://github.com/cncf/curriculum
- *Kubernetes in Action* — Marko Lukša (sách classic)
- *Kubernetes Patterns* — Bilgin Ibryam (design patterns)
- kubectl Cheat Sheet — https://kubernetes.io/docs/reference/kubectl/cheatsheet (bookmark!)

### AWS (background cho lab tuần này)

- AWS Docs — https://docs.aws.amazon.com
- **AWS Skill Builder** — https://skillbuilder.aws (free + paid courses, hands-on labs, learning plans cho cert)
- AWS Workshops — https://workshops.aws (hands-on labs miễn phí)
- Well-Architected Framework — https://aws.amazon.com/architecture/well-architected

---

## Repo cá nhân

Tên repo: `{your-username}-aws-accelerator-p2`

```
cloud/
  w8/
    day-a/      # Terraform
    day-b/      # K8s Container/Orchestration
    day-c/      # K8s Scaling + Networking
    lab/        # minimal K8s platform
    reflection.md
  w9/  w10/
capstone/
  w11/  w12/
```

Commit message: `[W8-D1] <topic ngắn>`. Push hằng ngày T2–T4 — mentor track qua repo.

---

## Cần hỗ trợ

- Câu hỏi material → `#phase2-cloud-daily`
- Vướng technical → `#phase2-cloud-help` (kèm screenshot + log)
- Urgent → DM mentor Minh hoặc Nghĩa

— Mentor team

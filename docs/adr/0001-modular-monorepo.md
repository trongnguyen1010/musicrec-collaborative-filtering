# ADR 0001: Dùng modular monorepo

- **Status:** Accepted
- **Date:** 2026-08-25

## Decision

Sử dụng một package Python `musicrec`, tách module theo trách nhiệm và tách luồng
offline/online bằng entry point thay vì tách microservice.

## Rationale

Phạm vi khóa luận cần tái lập thí nghiệm và demo web hơn là vận hành phân tán. Cách
này giảm chi phí triển khai, vẫn giữ được ranh giới rõ ràng để mở rộng sau này.

## Consequences

API/UI không được import logic training trực tiếp. Artifact release là hợp đồng giữa
offline pipeline và serving layer.

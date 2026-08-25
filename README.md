# MusicRec

Hệ thống khuyến nghị âm nhạc dựa trên Collaborative Filtering cho khóa luận tốt
nghiệp. Repository tổ chức tách biệt pipeline ML offline với API/UI suy luận online.

## Bắt đầu

```powershell
uv sync --all-extras
uv run pre-commit install
uv run pytest
```

Sau khi cấu hình DVC remote và có quyền truy cập dữ liệu:

```powershell
uv run dvc pull
uv run dvc repro
uv run uvicorn musicrec.api.main:app --reload
uv run streamlit run src/musicrec/ui/app.py
```

Xem [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) để biết kiến trúc và quy trình,
[DEVELOPMENT_RULES.md](DEVELOPMENT_RULES.md) để biết các quy tắc bắt buộc, và
[CHANGELOG.md](CHANGELOG.md) để theo dõi thay đổi.

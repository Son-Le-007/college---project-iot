Nơi viết code backend + frontend theo kiến trúc server side render.

Hướng khung hiện tại: Python + FastAPI + Jinja2.

Lý do chọn hướng này:
- phù hợp với SSR
- nhẹ, dễ khởi tạo
- tách route, template, static rõ ràng
- dễ mở rộng API, MQTT, auth, dashboard sau này

Cấu trúc khung:
- `app/main.py`: entrypoint khởi tạo ứng dụng
- `app/core/`: cấu hình và dependency dùng chung
- `app/routes/`: route cho trang và API
- `app/services/`: logic nghiệp vụ sau này
- `templates/`: giao diện SSR
- `static/`: CSS, JS, image

Luồng hiện tại chỉ là skeleton, chưa gắn database hay MQTT.

Cài uv: `pip install uv`

Add dependencies: `uv add <package_name>`

Chạy app:
- cài venv: `uv venv`
- cài dependencies: `uv sync`
- chạy server (uv tự kích hoạt venv): `uv run uvicorn app.main:app --reload`
- hoặc chạy trực tiếp: `uv run app/main.py`

Ghi chú:
- chạy lệnh trong thư mục `app/`
- nếu muốn tách tiếp tầng dữ liệu, thêm database và MQTT vào `app/services/`


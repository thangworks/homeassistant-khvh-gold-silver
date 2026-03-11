# Kim Khánh Việt Hùng - Giá Vàng Bạc (Home Assistant)

Custom integration cho Home Assistant để lấy giá vàng/bạc từ trang Kim Khánh Việt Hùng.

## Tính năng

- Tự động trích xuất bảng giá từ: `https://kimkhanhviethung.vn/tra-cuu-gia-vang.html`
- Tên sensor chuẩn tiếng Anh, ngắn gọn với tiền tố `KHVH`
- Tạo sensor cho từng sản phẩm:
  - `Buy Price`
  - `Sell Price`
  - `Exchange Price`
- Tự động cập nhật mặc định mỗi `1 giờ` (có thể chỉnh từ UI)
- Có service cập nhật thủ công: `kim_khanh_viet_hung_gia_vang_bac.refresh_prices`
- Cấu hình qua giao diện (`Config Flow`)

## Cài bằng HACS (Custom Repository)

1. Vào HACS -> Integrations -> menu 3 chấm -> `Custom repositories`.
2. Thêm URL repo này, chọn loại `Integration`.
3. Tìm `Kim Khánh Việt Hùng - Giá Vàng Bạc` và cài đặt.
4. Khởi động lại Home Assistant.
5. Vào `Settings -> Devices & Services -> Add Integration` và tìm `Kim Khánh Việt Hùng`.

## Cấu hình

- `URL nguồn dữ liệu`: mặc định là trang tra cứu của Kim Khánh Việt Hùng
- `Chu kỳ cập nhật (giờ)`: mặc định `1`

## Entity được tạo

Mỗi dòng giá tạo 3 entity sensor, ví dụ:

- `sensor.khvh_vang_999_9_buy_price`
- `sensor.khvh_vang_999_9_sell_price`
- `sensor.khvh_vang_999_9_exchange_price`

Các thuộc tính thêm:

- `group`: nhóm vàng/bạc
- `last_fetch`: thời điểm lấy dữ liệu (UTC ISO)
- `source_url`: URL nguồn

## Cập nhật thủ công

Vào `Developer Tools -> Services`, gọi service:

- `kim_khanh_viet_hung_gia_vang_bac.refresh_prices`

## Lưu ý

- Dữ liệu phụ thuộc trực tiếp vào cấu trúc HTML của trang nguồn.
- Nếu trang thay đổi HTML lớn, parser có thể cần cập nhật.

use std::sync::Arc;

use winit::event::{Event, WindowEvent};
use winit::event_loop::EventLoop;
use winit::window::{WindowBuilder, WindowLevel};
use winit::raw_window_handle::{HasWindowHandle, RawWindowHandle};

use windows::Win32::Foundation::{COLORREF, HWND};
use windows::Win32::Graphics::Gdi::{
    GetDC, ReleaseDC, StretchDIBits,
    BITMAPINFO, BITMAPINFOHEADER, BI_RGB,
    DIB_RGB_COLORS, SRCCOPY,
};
use windows::Win32::UI::WindowsAndMessaging::{
    GetWindowLongPtrW, SetWindowLongPtrW, SetLayeredWindowAttributes,
    GWL_EXSTYLE, LWA_COLORKEY,
    WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TRANSPARENT,
};

const MAGENTA: COLORREF = COLORREF(0x00FF00FF);
const WIDTH: i32 = 800;
const HEIGHT: i32 = 600;

fn main() {
    let event_loop = EventLoop::new().expect("EventLoop");

    let window = Arc::new(
        WindowBuilder::new()
            .with_title("Chess Overlay")
            .with_inner_size(winit::dpi::LogicalSize::new(WIDTH as f64, HEIGHT as f64))
            .with_transparent(true)
            .with_decorations(false)
            .build(&event_loop)
            .expect("Не удалось создать окно"),
    );

    window.set_window_level(WindowLevel::AlwaysOnTop);

    let hwnd = match window.window_handle().expect("handle").as_raw() {
        RawWindowHandle::Win32(h) => HWND(h.hwnd.get() as *mut _),
        _ => panic!("Это не Windows"),
    };

    unsafe {
        let ex = GetWindowLongPtrW(hwnd, GWL_EXSTYLE);
        let new_ex = ex
            | (WS_EX_LAYERED.0 as isize)
            | (WS_EX_TRANSPARENT.0 as isize)
            | (WS_EX_NOACTIVATE.0 as isize);
        SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_ex);
        SetLayeredWindowAttributes(hwnd, MAGENTA, 0, LWA_COLORKEY)
            .expect("color-key failed");
    }

    let mut buffer = vec![0u8; (WIDTH * HEIGHT * 4) as usize];

    event_loop
        .run(move |event, elwt| match event {
            Event::WindowEvent { event, .. } => match event {
                WindowEvent::CloseRequested => elwt.exit(),
                WindowEvent::RedrawRequested => unsafe {
                    // Заполняем магентой в BGRA
                    for p in buffer.chunks_exact_mut(4) {
                        p[0] = 0xFF; // B
                        p[1] = 0x00; // G
                        p[2] = 0xFF; // R
                        p[3] = 0x00; // резерв
                    }

                    let hdc = GetDC(hwnd); // <-- без Some(...)
                    if hdc.is_invalid() {
                        eprintln!("GetDC failed");
                        elwt.exit();
                        return;
                    }

                    let mut bmi = BITMAPINFO::default();
                    bmi.bmiHeader = BITMAPINFOHEADER {
                        biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
                        biWidth: WIDTH,
                        biHeight: -HEIGHT, // top-down
                        biPlanes: 1,
                        biBitCount: 32,
                        biCompression: BI_RGB.0,
                        ..Default::default()
                    };

                    StretchDIBits(
                        hdc,
                        0, 0, WIDTH, HEIGHT,
                        0, 0, WIDTH, HEIGHT,
                        Some(buffer.as_ptr() as *const _),
                        &bmi,
                        DIB_RGB_COLORS,
                        SRCCOPY,
                    );

                    let _ = ReleaseDC(hwnd, hdc); // <-- без Some(...)
                },
                _ => {}
            },
            Event::AboutToWait => window.request_redraw(),
            _ => {}
        })
        .expect("event loop");
}
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};

use winit::application::ApplicationHandler;
use winit::event::WindowEvent;
use winit::event_loop::{ActiveEventLoop, EventLoop};
use winit::window::{Window, WindowId, WindowLevel};
use winit::raw_window_handle::{HasWindowHandle, RawWindowHandle};
use winit::dpi::LogicalSize as WinitLogicalSize;

use windows::Win32::Foundation::{COLORREF, HWND, LPARAM, LRESULT, POINT, RECT, WPARAM};
use windows::Win32::System::LibraryLoader::GetModuleHandleW;
use windows::Win32::System::Threading::{AttachThreadInput, GetCurrentThreadId};
use windows::Win32::UI::WindowsAndMessaging::{
    CallNextHookEx, GetCursorPos, GetForegroundWindow, GetWindowLongPtrW, GetWindowRect,
    GetWindowThreadProcessId, SetForegroundWindow,
    SetLayeredWindowAttributes, SetWindowLongPtrW, SetWindowPos, SetWindowsHookExW, ShowWindow,
    GWL_EXSTYLE, HHOOK, LWA_ALPHA, MSLLHOOKSTRUCT,
    SWP_FRAMECHANGED, SWP_NOACTIVATE, SWP_NOMOVE, SWP_NOSIZE,
    SW_MINIMIZE, SW_RESTORE, SW_SHOW,
    WH_MOUSE_LL, WM_MOUSEWHEEL,
    WS_EX_LAYERED, WS_EX_NOACTIVATE, WS_EX_TRANSPARENT,
    HWND_TOPMOST, HWND_NOTOPMOST,
};
use windows::Win32::UI::Input::KeyboardAndMouse::{GetAsyncKeyState, VK_SHIFT};

use wry::{WebContext, WebViewBuilder, Rect as WryRect};
use wry::dpi::{LogicalPosition, LogicalSize as WryLogicalSize};

const WINDOW_W: f64 = 800.0;
const WINDOW_H: f64 = 800.0;
const MIN_SIZE: i32 = 200;
const MAX_SIZE: i32 = 2000;

const START_URL: &str = "https://www.chess.com/play/online";

const VK_CAPITAL: i32 = 0x14;

static WHEEL_ACCUM: AtomicI32 = AtomicI32::new(0);
static RESIZE_MODE: AtomicI32 = AtomicI32::new(0);

const TRANSPARENT_SCRIPT: &str = r#"
(function() {
    const css = `
        html, body {
            background: transparent !important;
            background-color: transparent !important;
        }
    `;
    function apply() {
        if (!document.head && !document.documentElement) return;
        let el = document.getElementById('__chess_overlay_transparent__');
        if (!el) {
            el = document.createElement('style');
            el.id = '__chess_overlay_transparent__';
            el.textContent = css;
            (document.head || document.documentElement).appendChild(el);
        }
    }
    for (let i = 0; i < 30; i++) {
        setTimeout(apply, i * 100);
    }
    const observer = new MutationObserver(apply);
    observer.observe(document.documentElement, { childList: true, subtree: true });
})();
"#;

fn is_key_down(vk: i32) -> bool {
    unsafe { (GetAsyncKeyState(vk) as u16 & 0x8000) != 0 }
}

fn get_window_pos(hwnd: HWND) -> (i32, i32) {
    unsafe {
        let mut r = RECT::default();
        if GetWindowRect(hwnd, &mut r).is_ok() {
            (r.left, r.top)
        } else {
            (0, 0)
        }
    }
}

fn get_cursor_pos() -> (i32, i32) {
    unsafe {
        let mut p = POINT::default();
        let _ = GetCursorPos(&mut p);
        (p.x, p.y)
    }
}

/// Обход блокировки SetForegroundWindow: цепляемся к потоку активного окна.
/// Плюс временно снимаем topmost — так Windows разрешает активацию.
unsafe fn force_foreground(hwnd: HWND) {
    let _ = SetWindowPos(
        hwnd,
        HWND_NOTOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
    );

    let fg = GetForegroundWindow();
    let fg_thread = GetWindowThreadProcessId(fg, None);
    let my_thread = GetCurrentThreadId();

    if fg_thread != 0 && fg_thread != my_thread {
        let _ = AttachThreadInput(fg_thread, my_thread, true);
        let _ = SetForegroundWindow(hwnd);
        let _ = AttachThreadInput(fg_thread, my_thread, false);
    } else {
        let _ = SetForegroundWindow(hwnd);
    }

    let _ = SetWindowPos(
        hwnd,
        HWND_TOPMOST,
        0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
    );
}

unsafe extern "system" fn mouse_hook(
    code: i32,
    wparam: WPARAM,
    lparam: LPARAM,
) -> LRESULT {
    if code >= 0 && wparam.0 == WM_MOUSEWHEEL as usize {
        let info = &*(lparam.0 as *const MSLLHOOKSTRUCT);
        let delta = ((info.mouseData >> 16) as u16 as i16) as i32;
        WHEEL_ACCUM.fetch_add(delta, Ordering::Relaxed);

        if RESIZE_MODE.load(Ordering::Relaxed) != 0 {
            return LRESULT(1);
        }
    }
    CallNextHookEx(HHOOK::default(), code, wparam, lparam)
}

struct App {
    window: Option<Arc<Window>>,
    webview: Option<wry::WebView>,
    _web_context: Option<WebContext>,
    caps_prev_interactive: bool,
    caps_prev_drag: bool,
    drag_start_cursor: (i32, i32),
    drag_start_window: (i32, i32),
    current_w: i32,
    current_h: i32,
    _hook: Option<HHOOK>,
    frame_counter: u32,
}

impl App {
    fn new() -> Self {
        Self {
            window: None,
            webview: None,
            _web_context: None,
            caps_prev_interactive: false,
            caps_prev_drag: false,
            drag_start_cursor: (0, 0),
            drag_start_window: (0, 0),
            current_w: WINDOW_W as i32,
            current_h: WINDOW_H as i32,
            _hook: None,
            frame_counter: 0,
        }
    }
}

impl ApplicationHandler for App {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        let window = Arc::new(
            event_loop
                .create_window(
                    Window::default_attributes()
                        .with_title("Chess Overlay")
                        .with_inner_size(WinitLogicalSize::new(WINDOW_W, WINDOW_H))
                        .with_transparent(true)
                        .with_decorations(false)
                        .with_visible(true)
                        .with_window_level(WindowLevel::AlwaysOnTop),
                )
                .expect("Не удалось создать окно"),
        );

        if let Ok(handle) = window.window_handle() {
            if let RawWindowHandle::Win32(h) = handle.as_raw() {
                let hwnd = HWND(h.hwnd.get() as *mut _);
                unsafe {
                    let ex = GetWindowLongPtrW(hwnd, GWL_EXSTYLE);
                    let new_ex = ex
                        | (WS_EX_LAYERED.0 as isize)
                        | (WS_EX_TRANSPARENT.0 as isize)
                        | (WS_EX_NOACTIVATE.0 as isize);
                    SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_ex);

                    let _ = SetLayeredWindowAttributes(hwnd, COLORREF(0), 255, LWA_ALPHA);

                    let _ = SetWindowPos(
                        hwnd,
                        HWND_TOPMOST,
                        0, 0, 0, 0,
                        SWP_NOSIZE | SWP_NOACTIVATE,
                    );

                    let after_ex = GetWindowLongPtrW(hwnd, GWL_EXSTYLE);
                    eprintln!("[styles] after set: {:#x}", after_ex);
                }
            }
        }

        unsafe {
            let hmod = GetModuleHandleW(None).unwrap_or_default();
            match SetWindowsHookExW(WH_MOUSE_LL, Some(mouse_hook), hmod, 0) {
                Ok(h) => {
                    eprintln!("[hook] installed OK");
                    self._hook = Some(h);
                }
                Err(e) => {
                    eprintln!("[hook] FAILED: {e}");
                }
            }
        }

        let data_dir = std::env::var("LOCALAPPDATA")
            .map(std::path::PathBuf::from)
            .map(|p| p.join("ChessOverlay").join("webview_data"))
            .unwrap_or_else(|_| std::path::PathBuf::from("webview_data"));

        let _ = std::fs::create_dir_all(&data_dir);
        eprintln!("[data] using: {}", data_dir.display());

        let mut web_context = WebContext::new(Some(data_dir));

        let webview = WebViewBuilder::new_with_web_context(&mut web_context)
            .with_url(START_URL)
            .with_transparent(true)
            .with_bounds(WryRect {
                position: LogicalPosition::new(0.0, 0.0).into(),
                size: WryLogicalSize::new(WINDOW_W, WINDOW_H).into(),
            })
            .with_initialization_script(TRANSPARENT_SCRIPT)
            .build_as_child(&window)
            .expect("Не удалось создать WebView");

        self.window = Some(window);
        self.webview = Some(webview);
        self._web_context = Some(web_context);

        eprintln!("=== РЕЖИМЫ ===");
        eprintln!("CapsLock                    — взаимодействие с доской");
        eprintln!("Shift + CapsLock            — двигать окно");
        eprintln!("Shift + CapsLock + колесо   — менять размер");
        eprintln!("Ничего не зажато            — клики сквозь в игру");
    }

    fn about_to_wait(&mut self, _event_loop: &ActiveEventLoop) {
        let Some(window) = self.window.as_ref() else { return };
        let Ok(handle) = window.window_handle() else { return };
        let RawWindowHandle::Win32(h) = handle.as_raw() else { return };
        let hwnd = HWND(h.hwnd.get() as *mut _);

        // === Пинок для WebView2: minimize+restore заставляет его
        // пересоздать composition surface и включить прозрачность.
        self.frame_counter += 1;

        if self.frame_counter == 180 {
            unsafe {
                let _ = ShowWindow(hwnd, SW_MINIMIZE);
            }
            eprintln!("[init] minimize");
        }

        if self.frame_counter == 240 {
            unsafe {
                let _ = ShowWindow(hwnd, SW_RESTORE);
                let (wx, wy) = get_window_pos(hwnd);
                let _ = SetWindowPos(
                    hwnd,
                    HWND_TOPMOST,
                    wx, wy,
                    self.current_w, self.current_h,
                    SWP_NOACTIVATE,
                );
            }
            if let Some(wv) = &self.webview {
                let _ = wv.set_bounds(WryRect {
                    position: LogicalPosition::new(0.0, 0.0).into(),
                    size: WryLogicalSize::new(
                        self.current_w as f64,
                        self.current_h as f64,
                    ).into(),
                });
            }
            eprintln!("[init] restore + set_bounds");
        }

        window.request_redraw();
    }

    fn window_event(
        &mut self,
        event_loop: &ActiveEventLoop,
        _window_id: WindowId,
        event: WindowEvent,
    ) {
        match event {
            WindowEvent::CloseRequested => event_loop.exit(),

            WindowEvent::RedrawRequested => {
                let Some(window) = self.window.as_ref() else { return };
                let Ok(handle) = window.window_handle() else { return };
                let RawWindowHandle::Win32(h) = handle.as_raw() else { return };
                let hwnd = HWND(h.hwnd.get() as *mut _);

                let caps = is_key_down(VK_CAPITAL);
                let shift = is_key_down(VK_SHIFT.0 as i32);

                let interactive = caps && !shift;
                let drag = caps && shift;

                // --- Переключение interactive / click-through ---
                if interactive != self.caps_prev_interactive {
                    unsafe {
                        let ex = GetWindowLongPtrW(hwnd, GWL_EXSTYLE);
                        let tr = WS_EX_TRANSPARENT.0 as isize;
                        let na = WS_EX_NOACTIVATE.0 as isize;
                        let lay = WS_EX_LAYERED.0 as isize;

                        let new_ex = if interactive {
                            // Снимаем ВСЕ три флага — иначе клики не пробрасываются
                            // в дочернее окно WebView2.
                            ((ex & !tr) & !na) & !lay
                        } else {
                            ex | tr | na | lay
                        };
                        SetWindowLongPtrW(hwnd, GWL_EXSTYLE, new_ex);

                        let _ = SetWindowPos(
                            hwnd,
                            HWND_TOPMOST,
                            0, 0, 0, 0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED,
                        );

                        if interactive {
                            let _ = ShowWindow(hwnd, SW_SHOW);
                            force_foreground(hwnd);
                        } else {
                            // WS_EX_LAYERED переустановили — нужно заново задать альфу.
                            let _ = SetLayeredWindowAttributes(
                                hwnd, COLORREF(0), 255, LWA_ALPHA,
                            );
                        }

                        eprintln!(
                            "[mode] {} (ex={:#x})",
                            if interactive { "interactive" } else { "click-through" },
                            new_ex
                        );
                    }
                    self.caps_prev_interactive = interactive;
                }

                // --- Drag + resize ---
                if drag {
                    RESIZE_MODE.store(1, Ordering::Relaxed);

                    let cur = get_cursor_pos();
                    if !self.caps_prev_drag {
                        self.drag_start_cursor = cur;
                        self.drag_start_window = get_window_pos(hwnd);
                        WHEEL_ACCUM.store(0, Ordering::Relaxed);
                    } else {
                        let dx = cur.0 - self.drag_start_cursor.0;
                        let dy = cur.1 - self.drag_start_cursor.1;
                        let nx = self.drag_start_window.0 + dx;
                        let ny = self.drag_start_window.1 + dy;
                        unsafe {
                            let _ = SetWindowPos(
                                hwnd,
                                HWND_TOPMOST,
                                nx, ny, self.current_w, self.current_h,
                                SWP_NOACTIVATE,
                            );
                        }

                        let wheel = WHEEL_ACCUM.swap(0, Ordering::Relaxed);
                        if wheel != 0 {
                            let clicks = wheel / 120;
                            let step = clicks * 20;
                            self.current_w = (self.current_w + step).clamp(MIN_SIZE, MAX_SIZE);
                            let ratio = WINDOW_H / WINDOW_W;
                            self.current_h = (self.current_w as f64 * ratio) as i32;

                            let (wx, wy) = get_window_pos(hwnd);
                            unsafe {
                                let _ = SetWindowPos(
                                    hwnd,
                                    HWND_TOPMOST,
                                    wx, wy, self.current_w, self.current_h,
                                    SWP_NOACTIVATE,
                                );
                            }

                            if let Some(wv) = &self.webview {
                                let _ = wv.set_bounds(WryRect {
                                    position: LogicalPosition::new(0.0, 0.0).into(),
                                    size: WryLogicalSize::new(
                                        self.current_w as f64,
                                        self.current_h as f64,
                                    ).into(),
                                });
                            }

                            eprintln!("[resize] {}x{}", self.current_w, self.current_h);
                        }
                    }
                    self.caps_prev_drag = true;
                } else {
                    RESIZE_MODE.store(0, Ordering::Relaxed);
                    self.caps_prev_drag = false;
                }
            }
            _ => {}
        }
    }
}

fn main() {
    let event_loop = EventLoop::new().expect("EventLoop");
    let mut app = App::new();
    event_loop.run_app(&mut app).expect("Ошибка event loop");
}
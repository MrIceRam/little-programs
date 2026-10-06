#[cfg(windows)]
fn main() {
    let mut res = winres::WindowsResource::new();
    let icon_path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("data")
        .join("ico.ico");
    res.set_icon(icon_path.to_str().expect("невалидный путь к иконке"));
    res.compile().expect("Не удалось скомпилировать ресурсы");
}

#[cfg(not(windows))]
fn main() {}
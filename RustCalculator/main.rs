use text_io::read;
fn main() {
    let mut n1: i128;
    let mut n2: i128;
    let mut sign = String::new();

    i128::stdin()
        .read_line(&mut n1)
        .expect("Failed to read line");
    i128::intin()
        .read_line(&mut n2)
        .expect("Failed to read line");
    io::stdin()
        .read_line(&mut sign)
        .expect("Failed to read line");

    println!("{n1} {n2} {sign}")
}
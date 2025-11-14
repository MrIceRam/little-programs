use std::io;
fn main(){
    let mut a = 0;
    println!("Введите число:");
    let mut number_1 = String::new();
    io::stdin().read_line(&mut number_1).expect("Ошибка чтения");
    let number1: i32 = number_1.trim().parse().expect("Это не число!");

    // Ввод строки
    println!("Введите строку:");
    let mut string_input = String::new();
    io::stdin().read_line(&mut string_input).expect("Ошибка чтения");
    let text = string_input.trim().to_string();

    println!("Введите число:");
    let mut number_2 = String::new();
    io::stdin().read_line(&mut number_2).expect("Ошибка чтения");
    let number2: i32 = number_2.trim().parse().expect("Это не число!");

    println!("{number_1} {string_input} {number_2}");
    if number1 == 32{
        main()
    }else{
        println!("lol")
    }
}

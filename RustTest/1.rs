fn main(){
    let mut x = "LOL";

    println!("{x}");

    match x {
        "lol"=>println!("lox"),
        "ww"=>println!("lox"),
        "LOL"=>x="LLLOOOOLLLL",
        _ => println!("lox"),
    };

    print!("{x}")
}

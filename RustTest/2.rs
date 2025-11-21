fn main(){
    let mut x:i32=1;   // 2**32 int string bool float cahr
    let x2 = demo(x);       
    println!("{x2}");
   loop{
    println!("loop 6");
    x = x + 1;
    if x == 10{
        break;
    }
}
    let x3 =[10,20,30,40,50];
    for i in x3 {
        println!("{i}")
    }
}

fn demo(x:i32)->i32{ // -> значит тут вернется число с i32

    println!("hi demo");
    return x+2
} // end rust 2 6:01
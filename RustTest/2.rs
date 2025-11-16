fn main(){
    let x:i32=1;
    let x2=demo(x);       
    println!("{x2}")
}
fn demo(x:i32)->i32{ // -> значит тут вернется число с i32

    println!("hi demo");
    x+2
} // end rust 2 6:01
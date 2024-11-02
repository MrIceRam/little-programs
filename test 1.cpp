#include <iostream>

int maks(int x){
    if (x == 18){
        return 1;
    }
    else{
        return 2;
    }
}



int main(){
    setlocale(LC_ALL, "ru");
    int a;
    std::cout << "age = ";
    std::cin >> a;
    if (a != 0){
        std::cout << maks(a) << "\n";
        main();
    }
}
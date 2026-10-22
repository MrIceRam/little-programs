#include <iostream>
#include <ctime>
#include <fstream>
#include <string>

int maks(int x,int b){
    if (x == b){
        return 1;
    }
    if (x == 0){
        std::cout << "GG\n";
        exit(0);        
    }
    else
    {
        return -1;
    }
}

int main(){
    setlocale(LC_ALL, "ru");
    srand(time(0));

    int a;
    int b = 1 + rand() % 10;
    std::cout << "b = "<< b << "\n";
    std::cout << "age = ";
    std::cin >> a;
    std::cout << maks(a,b) << "\n";
    for (int i = 0; i < 10; i++){
        int b = 1 + rand() % 20;
        std::cout << i << " = " << b << "\n";
        main();
    }
}
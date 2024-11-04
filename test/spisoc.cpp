#include <iostream>

int main(){
    setlocale(LC_ALL, "ru");
    int a[3];

    a[0] = 5;
    a[1] = 10;
    a[2] = 20;

    
    for (int i = 0; i<3; i++){   
        std::cout << a[i] <<"\n";   
    }    
    return 0;
}
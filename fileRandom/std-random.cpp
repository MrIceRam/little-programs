#include <iostream>
#include <fstream>

int main(){
    setlocale(LC_ALL, "ru");
    int i;

    std::ifstream read("RandomNUM.txt", std::ios::out);
    read >> i;
    std::cout << i << "\n";
    

}
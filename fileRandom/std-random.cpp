#include <iostream>
#include <fstream>

int main(){
    setlocale(LC_ALL, "ru");

   //system (python randomNUM.py)
    
    int i;

    std::ifstream read("RandomNUM.txt", std::ios::out);
    read >> i;
    std::cout << i << "\n";
    

}

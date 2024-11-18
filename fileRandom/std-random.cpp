#include <iostream>
#include <fstream>


int main(){
    setlocale(LC_ALL, "ru");

   // system("python3 Randompy.py");
    system("Randompy.py");

    int i;
    std::ifstream read("RandomNUM.txt", std::ios::out);
    read >> i;
    std::cout << "c++ num: "<< i << "\n";
}

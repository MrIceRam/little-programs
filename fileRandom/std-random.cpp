#include <iostream>
#include <fstream>


int main(){
    setlocale(LC_ALL, "ru");

   // system("python3 Randompy.py");
   // OR \|/
    system("Randompy.py");

    int i;
    std::ifstream read("RandomNUM.txt", std::ios::out);
    read >> i;
    std::cout << "c++ num: "<< i << "\n";
    
    // ПРАВИЛЬНЕЕ
    // std::string line;
    // std::ifstream file("input.txt");
    // if (file.is_open()){
    //     while (getline(file, line)){}
    //         cout << line << "\n";
    //         file.close();
    // }
    // else{
    //     cout << "Unable to open file";
    // return 0;}
}

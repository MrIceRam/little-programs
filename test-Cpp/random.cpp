#include <iostream>
#include <random>

using namespace std;
int main(){
    cout << "hello world";
    random_device rd;   // non-deterministic generator
    mt19937_64 gen(rd());  // to seed mersenne twister.
    uniform_int_distribution<> dist(1,6); // distribute results between 1 and 6 inclusive.
    int a = dist(gen);
    cout << a << " "; // pass the generator to the distribution.
    
    std::cout << endl;
    return 0;
}
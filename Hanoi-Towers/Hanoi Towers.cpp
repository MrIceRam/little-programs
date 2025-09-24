#include <iostream>
#include <windows.h>
#include <conio.h>
#include <list>

std::list<int> stick1;
std::list<int> stick2;
std::list<int> stick3;

void gotoxy(int x, int y) {
    COORD p = { x, y };
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), p);
}

void CreateStiks(int x) {
    stick1.clear();
    stick2.clear();
    stick3.clear();

    for (int i = x; i >= 1; i--) {
        stick1.push_front(i);
    }
    for (int i = 0; i < x; i++) {
        stick2.push_front(0);
    }
    for (int i = 0; i < x; i++) {
        stick3.push_front(0);
    }
}

void PrintMap(int x) {
    for (int i = 0; i < x; i++) {
        gotoxy(5,  i);
        int val = *next(stick1.begin(), i);
        if (val != 0) std::cout << val;
        else std::cout << " ";
    }
    for (int i = 0; i < x; i++) {
        gotoxy(10,  i);
        int val = *next(stick2.begin(), i);
        if (val != 0) std::cout << val;
        else std::cout << " ";
    }
    for (int i = 0; i < x; i++) {
        gotoxy(15, i);
        int val = *next(stick3.begin(), i);
        if (val != 0) std::cout << val;
        else std::cout << " ";
    }
}

void moveDisk(std::list<int>& source, std::list<int>& target) {
    // Find first non-zero in source
    auto source_it = source.begin();
    while (source_it != source.end() && *source_it == 0) {
        ++source_it;
    }

    if (source_it == source.end()) return; // no disk to move

    // Find last zero in target
    auto target_it = target.end();
    --target_it;
    while (target_it != target.begin() && *target_it != 0) {
        --target_it;
    }

    if (*target_it != 0) return; // no space

    // Move the disk
    *target_it = *source_it;
    *source_it = 0;

    // Print the move   
    system("cls");
    PrintMap(source.size());
    Sleep(500);
}

void hanoi(int n, std::list<int>& source, std::list<int>& target, std::list<int>& auxiliary) {
    if (n == 1) {
        moveDisk(source, target);
    }
    else {
        hanoi(n - 1, source, auxiliary, target);
        moveDisk(source, target);
        hanoi(n - 1, auxiliary, target, source);
    }
}

void Run(int x) {
    CreateStiks(x);
    PrintMap(x);
    // Determine which rod is which
    hanoi(x, stick1, stick3, stick2);

    gotoxy(0, x + 1);
    std::cout << "конец";
    _getch();
}

int main() {
    setlocale(LC_ALL, "Russian");
    int x;
    system("color 3");
    std::cout << "Количество дисков: ";
    std::cin >> x;
    
    system("mode con cols=25 lines=30");

    Run(x);
    return 0;
}

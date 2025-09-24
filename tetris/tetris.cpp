#include <iostream>
#include <windows.h>
#include <conio.h>
#include <vector>
#include <random>

using namespace std;

void gotoxy(int x, int y) {
    COORD p = { x, y };
    SetConsoleCursorPosition(GetStdHandle(STD_OUTPUT_HANDLE), p);
}

const int WIDTH = 10 + 2; 
const int HEIGHT = 14 + 1;
int point = 0;

struct Point {
    int x;
    int y;
};

int RandomNum(int x) {
    random_device rd;
    mt19937_64 gen(rd());
    uniform_int_distribution<> dist(1, 4);
    return dist(gen);
}

class Figure {
    vector<Point> vec;
    int type;  // Тип фигуры (1-4)
    int rotation = 0;  // Текущий поворот (0-3)
public:
    void push(int x, int y) {
        Point temp;
        temp.x = x;
        temp.y = y;
        vec.push_back(temp);
    }

    void show() {
        for (int i = 0; i < vec.size(); i++) {
            gotoxy(vec[i].x, vec[i].y);
            cout << "*";
        }
    }

    void hide() {
        for (int i = 0; i < vec.size(); i++) {
            gotoxy(vec[i].x, vec[i].y);
            cout << " ";
        }
    }
    
    void moveDown() {
        for (int i = 0; i < vec.size(); i++) {
            vec[i].y++;
        }
    }

    void moveUp() {
        for (int i = 0; i < vec.size(); i++) {
            vec[i].y--;
        }
    }

    void moveLeft() {
        for (int i = 0; i < vec.size(); i++) {
            vec[i].x--;
        }
    }

    void moveRight() {
        for (int i = 0; i < vec.size(); i++) {
            vec[i].x++;
        }
    }

    bool isCollision(const vector<vector<int>>& vec2d) {
        for (int i = 0; i < vec.size(); i++) {
            if (vec[i].y < 0 || vec[i].y >= HEIGHT || vec[i].x < 0 || vec[i].x >= WIDTH)
                return true;
            if (vec2d[vec[i].y][vec[i].x] == 1 || vec2d[vec[i].y][vec[i].x] == 2)
                return true;
        }
        return false;
    }

    void fixed(vector<vector<int>>& vec2d) {
        for (int i = 0; i < vec.size(); i++) {
            vec2d[vec[i].y][vec[i].x] = 2;
        }
    }


    void rotate(const vector<vector<int>>& vec2d) {
        if (type == 1) return;  
        
        vector<Point> old = vec;
        
        int centerX = vec[0].x;
        int centerY = vec[0].y;
        
        for (int i = 0; i < vec.size(); i++) {
            int x = vec[i].x - centerX;
            int y = vec[i].y - centerY;
            vec[i].x = centerX - y;
            vec[i].y = centerY + x;
        }
        
        if (isCollision(vec2d)) {
            vec = old;
        }
    }

    void spawn() {
        vec.clear();
        type = RandomNum(1);

        switch (type) {
            case 1:  // Квадрат
                push(4, 0);
                push(5, 0);
                push(4, 1);
                push(5, 1);
                break;
            case 2:  // Палка
                push(4, 0);
                push(5, 0);
                push(6, 0);
                push(7, 0);
                break;
            case 3:  // J
                push(5, 0);
                push(5, 1);
                push(5, 2);
                push(4, 2);
                break;
            case 4:  // L
                push(4, 0);
                push(4, 1);
                push(4, 2);
                push(5, 2);
                break;
        }
    }
};

class Game {
    vector<vector<int>> vec;

public:
    Game() {}

    void initVec(vector<vector<int>>& vec, int width, int height) {
        vector<int> temp;
        temp.push_back(1);
        for (int i = 1; i < width - 1; i++) {
            temp.push_back(0);
        }
        temp.push_back(1);

        for (int i = 0; i < height-1; i++) {
            vec.push_back(temp);
        }

        temp.clear();
        for (int i = 0; i < width; i++) {
            temp.push_back(1);
        }
        vec.push_back(temp);
    }

    void showField(const vector<vector<int>>& vec) {
        for (int i = 0; i < vec.size(); i++) {
            gotoxy(0, i);
            for (int j = 0; j < vec[i].size(); j++) {
                if (vec[i][j] == 1) {
                    cout << "#";
                }
                if (vec[i][j] == 2) {
                    cout << "@";
                }
                if (vec[i][j] == 0) {
                    cout << " ";
                }
            }
            cout << endl;
        }
    }

    void deleteLines() {
        for (int i = vec.size() - 2; i >= 0; i--) {
            bool lineFull = true;
            for (int j = 1; j < vec[i].size() - 1; j++) {
                if (vec[i][j] != 2) {
                    lineFull = false;
                    break;
                }
            }
            
            if (lineFull) {
                vec.erase(vec.begin() + i);
                vector<int> newLine(WIDTH, 0);
                newLine[0] = 1;
                newLine[WIDTH - 1] = 1;
                vec.insert(vec.begin(), newLine);
                point++;
            }
        }
    }

    int run() {
        initVec(vec, WIDTH, HEIGHT);
        showField(vec);

        Figure fig;
        fig.spawn();

        int ch = 0;
        while (true) {
            while (!_kbhit()) {
                fig.hide();
                fig.moveDown();
                
                if (fig.isCollision(vec)) {
                    fig.moveUp();
                    fig.fixed(vec);
                    deleteLines();
                    showField(vec);
                    gotoxy(20, 1);
                    cout << "Points " << point;
                    fig.spawn();
                }
                
                fig.show();
                Sleep(200);
            }

            ch = _getch();
            fig.hide();
            
            switch (ch) {
                case 77:  // Вправо
                    fig.moveRight();
                    if (fig.isCollision(vec)) fig.moveLeft();
                    break;
                case 75:  // Влево
                    fig.moveLeft();
                    if (fig.isCollision(vec)) fig.moveRight();
                    break;
                case 80:  // Вниз
                    fig.moveDown();
                    if (fig.isCollision(vec)) fig.moveUp();
                    break;
                case 72:  // Вверх - поворот
                    fig.rotate(vec);
                    break;
            }
            
            fig.show();
        }
        return 0;
    }
};

int main() {
    system("mode con cols=30 lines=20");
    setlocale(LC_ALL, "Russian");
    gotoxy(20, 1);
    cout << "Points 0";
    Game game;
    game.run();
    _getch();
    return 0;
}
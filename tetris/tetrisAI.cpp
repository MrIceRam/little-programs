// ============================================================================
//  Тетрис — улучшенная версия (Windows, C++17, MSVC-совместимая)
// ============================================================================
#define NOMINMAX
#include <windows.h>
#include <vector>
#include <array>
#include <random>
#include <chrono>
#include <string>
#include <algorithm>
#include <thread>
#include <cmath>
#include <utility>
#include <initializer_list>

// ---------------------------------------------------------------------------
//  Константы
// ---------------------------------------------------------------------------
constexpr int FIELD_W = 10;
constexpr int FIELD_H = 20;
constexpr int CELL_W  = 2;

constexpr int BOARD_OX = 3;
constexpr int BOARD_OY = 2;
constexpr int BORDER_L = BOARD_OX - 1;
constexpr int BORDER_R = BOARD_OX + FIELD_W * CELL_W;
constexpr int BORDER_T = BOARD_OY - 1;
constexpr int BORDER_B = BOARD_OY + FIELD_H;

constexpr int SIDEBAR_X = BORDER_R + 3;
constexpr int SCREEN_W  = 44;
constexpr int SCREEN_H  = 26;

constexpr double DAS_DELAY          = 0.15;
constexpr double DAS_REPEAT         = 0.04;
constexpr double SOFT_DROP_INTERVAL = 0.025;
constexpr double LOCK_DELAY         = 0.45;

// ---------------------------------------------------------------------------
//  Двойной буфер экрана
// ---------------------------------------------------------------------------
class Screen {
public:
    Screen(int w, int h) : w_(w), h_(h), buf_(size_t(w) * size_t(h)) {
        out_ = GetStdHandle(STD_OUTPUT_HANDLE);
        CONSOLE_CURSOR_INFO ci{1, FALSE};
        SetConsoleCursorInfo(out_, &ci);
    }
    void clear(WORD attr = 0) {
        CHAR_INFO c{};
        c.Char.UnicodeChar = L' ';
        c.Attributes = attr;
        std::fill(buf_.begin(), buf_.end(), c);
    }
    void put(int x, int y, wchar_t ch, WORD attr) {
        if (x < 0 || y < 0 || x >= w_ || y >= h_) return;
        auto& ci = buf_[size_t(y) * size_t(w_) + size_t(x)];
        ci.Char.UnicodeChar = ch;
        ci.Attributes = attr;
    }
    void putStr(int x, int y, const std::wstring& s, WORD attr) {
        for (size_t i = 0; i < s.size(); ++i) put(x + int(i), y, s[i], attr);
    }
    void present() {
        COORD size{(SHORT)w_, (SHORT)h_};
        COORD origin{0, 0};
        SMALL_RECT region{0, 0, (SHORT)(w_ - 1), (SHORT)(h_ - 1)};
        WriteConsoleOutputW(out_, buf_.data(), size, origin, &region);
    }
private:
    int w_, h_;
    std::vector<CHAR_INFO> buf_;
    HANDLE out_;
};

// ---------------------------------------------------------------------------
//  Определения фигур
// ---------------------------------------------------------------------------
struct Cell { int x, y; };

struct PieceDef {
    std::array<std::vector<Cell>, 4> rot;
    WORD color;
};

static std::vector<Cell> C(std::initializer_list<Cell> lst) {
    return std::vector<Cell>(lst);
}
static std::array<PieceDef, 7> makePieces() {
    std::array<PieceDef, 7> p{};

    // 0: I — голубой
    p[0].rot[0] = C({ {0,1},{1,1},{2,1},{3,1} });
    p[0].rot[1] = C({ {2,0},{2,1},{2,2},{2,3} });
    p[0].rot[2] = C({ {0,2},{1,2},{2,2},{3,2} });
    p[0].rot[3] = C({ {1,0},{1,1},{1,2},{1,3} });
    p[0].color  = BACKGROUND_BLUE | BACKGROUND_GREEN | BACKGROUND_INTENSITY;

    // 1: O — жёлтый
    p[1].rot[0] = C({ {0,0},{1,0},{0,1},{1,1} });
    p[1].rot[1] = C({ {0,0},{1,0},{0,1},{1,1} });
    p[1].rot[2] = C({ {0,0},{1,0},{0,1},{1,1} });
    p[1].rot[3] = C({ {0,0},{1,0},{0,1},{1,1} });
    p[1].color  = BACKGROUND_RED | BACKGROUND_GREEN | BACKGROUND_INTENSITY;

    // 2: T — фиолетовый
    p[2].rot[0] = C({ {1,0},{0,1},{1,1},{2,1} });
    p[2].rot[1] = C({ {1,0},{1,1},{2,1},{1,2} });
    p[2].rot[2] = C({ {0,1},{1,1},{2,1},{1,2} });
    p[2].rot[3] = C({ {1,0},{0,1},{1,1},{1,2} });
    p[2].color  = BACKGROUND_RED | BACKGROUND_BLUE | BACKGROUND_INTENSITY;

    // 3: S — зелёный
    p[3].rot[0] = C({ {1,0},{2,0},{0,1},{1,1} });
    p[3].rot[1] = C({ {1,0},{1,1},{2,1},{2,2} });
    p[3].rot[2] = C({ {1,1},{2,1},{0,2},{1,2} });
    p[3].rot[3] = C({ {0,0},{0,1},{1,1},{1,2} });
    p[3].color  = BACKGROUND_GREEN | BACKGROUND_INTENSITY;

    // 4: Z — красный
    p[4].rot[0] = C({ {0,0},{1,0},{1,1},{2,1} });
    p[4].rot[1] = C({ {2,0},{1,1},{2,1},{1,2} });
    p[4].rot[2] = C({ {0,1},{1,1},{1,2},{2,2} });
    p[4].rot[3] = C({ {1,0},{0,1},{1,1},{0,2} });
    p[4].color  = BACKGROUND_RED | BACKGROUND_INTENSITY;

    // 5: J — синий
    p[5].rot[0] = C({ {0,0},{0,1},{1,1},{2,1} });
    p[5].rot[1] = C({ {1,0},{2,0},{1,1},{1,2} });
    p[5].rot[2] = C({ {0,1},{1,1},{2,1},{2,2} });
    p[5].rot[3] = C({ {1,0},{1,1},{0,2},{1,2} });
    p[5].color  = BACKGROUND_BLUE | BACKGROUND_INTENSITY;

    // 6: L — оранжевый
    p[6].rot[0] = C({ {2,0},{0,1},{1,1},{2,1} });
    p[6].rot[1] = C({ {1,0},{1,1},{1,2},{2,2} });
    p[6].rot[2] = C({ {0,1},{1,1},{2,1},{0,2} });
    p[6].rot[3] = C({ {0,0},{1,0},{1,1},{1,2} });
    p[6].color  = BACKGROUND_RED | BACKGROUND_GREEN;

    return p;
}

const std::array<PieceDef, 7> PIECES = makePieces();

// Wall kicks (экранные координаты, y вниз)
static std::array<std::vector<Cell>, 8> makeKicksJLSTZ() {
    std::array<std::vector<Cell>, 8> k;
    k[0] = C({ {0,0},{-1,0},{-1,-1},{0,2},{-1,2} }); // 0->1
    k[1] = C({ {0,0},{1,0},{1,1},{0,-2},{1,-2} });   // 1->0
    k[2] = C({ {0,0},{1,0},{1,1},{0,-2},{1,-2} });   // 1->2
    k[3] = C({ {0,0},{-1,0},{-1,-1},{0,2},{-1,2} }); // 2->1
    k[4] = C({ {0,0},{1,0},{1,-1},{0,2},{1,2} });    // 2->3
    k[5] = C({ {0,0},{-1,0},{-1,1},{0,-2},{-1,-2} });// 3->2
    k[6] = C({ {0,0},{-1,0},{-1,1},{0,-2},{-1,-2} });// 3->0
    k[7] = C({ {0,0},{1,0},{1,-1},{0,2},{1,2} });    // 0->3
    return k;
}

static std::array<std::vector<Cell>, 8> makeKicksI() {
    std::array<std::vector<Cell>, 8> k;
    k[0] = C({ {0,0},{-2,0},{1,0},{-2,1},{1,-2} }); // 0->1
    k[1] = C({ {0,0},{2,0},{-1,0},{2,-1},{-1,2} }); // 1->0
    k[2] = C({ {0,0},{-1,0},{2,0},{-1,-2},{2,1} }); // 1->2
    k[3] = C({ {0,0},{1,0},{-2,0},{1,2},{-2,-1} }); // 2->1
    k[4] = C({ {0,0},{2,0},{-1,0},{2,-1},{-1,2} }); // 2->3
    k[5] = C({ {0,0},{-2,0},{1,0},{-2,1},{1,-2} }); // 3->2
    k[6] = C({ {0,0},{1,0},{-2,0},{1,2},{-2,-1} }); // 3->0
    k[7] = C({ {0,0},{-1,0},{2,0},{-1,-2},{2,1} }); // 0->3
    return k;
}

const std::array<std::vector<Cell>, 8> KICKS_JLSTZ = makeKicksJLSTZ();
const std::array<std::vector<Cell>, 8> KICKS_I     = makeKicksI();

inline int kickIndex(int from, int to) {
    if (from == 0 && to == 1) return 0;
    if (from == 1 && to == 0) return 1;
    if (from == 1 && to == 2) return 2;
    if (from == 2 && to == 1) return 3;
    if (from == 2 && to == 3) return 4;
    if (from == 3 && to == 2) return 5;
    if (from == 3 && to == 0) return 6;
    if (from == 0 && to == 3) return 7;
    return -1;
}

inline WORD toFg(WORD bg) { return WORD(bg >> 4); }

// ---------------------------------------------------------------------------
//  Повторитель клавиши с DAS/ARR
// ---------------------------------------------------------------------------
struct KeyRepeat {
    bool held = false;
    double timer = 0;
    bool repeating = false;
    bool update(bool nowDown, double dt) {
        bool fire = false;
        if (nowDown) {
            if (!held) { fire = true; timer = 0; repeating = false; }
            else {
                timer += dt;
                if (timer >= (repeating ? DAS_REPEAT : DAS_DELAY)) {
                    fire = true; timer = 0; repeating = true;
                }
            }
        } else { timer = 0; repeating = false; }
        held = nowDown;
        return fire;
    }
};

inline bool keyDown(int vk) { return (GetAsyncKeyState(vk) & 0x8000) != 0; }

// ---------------------------------------------------------------------------
//  Игра
// ---------------------------------------------------------------------------
class Game {
public:
    explicit Game(Screen& s) : scr_(s), rng_(std::random_device{}()) {}

    void run() {
        restart();
        auto last = std::chrono::steady_clock::now();
        while (!quit_) {
            auto now = std::chrono::steady_clock::now();
            double dt = std::chrono::duration<double>(now - last).count();
            last = now;
            if (dt > 0.1) dt = 0.1;

            if (!gameOver_) {
                handleInput(dt);
                if (!paused_ && !gameOver_) update(dt);
            } else {
                handleInput(dt);
            }
            render();
            std::this_thread::sleep_for(std::chrono::milliseconds(4));
        }
    }

private:
    struct ActivePiece { int type = 0, rot = 0, x = 0, y = 0; };

    Screen& scr_;
    int board_[FIELD_H][FIELD_W] = {};
    ActivePiece cur_;
    int nextType_ = 0;
    int holdType_ = -1;
    bool holdUsed_ = false;

    std::mt19937 rng_;
    std::vector<int> bag_;

    int score_ = 0, level_ = 1, lines_ = 0;
    double fallTimer_ = 0, lockTimer_ = 0;
    bool gameOver_ = false, paused_ = false, quit_ = false;

    KeyRepeat dasL_, dasR_, dasD_;
    bool pRotCW_ = false, pRotCCW_ = false, pHard_ = false,
         pHold_ = false, pPause_ = false, pEsc_ = false, pRestart_ = false;

    // ----------------------------------------------------------------
    int drawFromBag() {
        if (bag_.empty()) {
            bag_ = {0,1,2,3,4,5,6};
            std::shuffle(bag_.begin(), bag_.end(), rng_);
        }
        int t = bag_.back();
        bag_.pop_back();
        return t;
    }

    bool collides(const ActivePiece& p) const {
        for (auto& c : PIECES[p.type].rot[p.rot]) {
            int bx = p.x + c.x;
            int by = p.y + c.y;
            if (bx < 0 || bx >= FIELD_W) return true;
            if (by >= FIELD_H) return true;
            if (by < 0) continue;
            if (board_[by][bx]) return true;
        }
        return false;
    }

    int spawnX(int type) const {
        if (type == 0) return 3;   // I
        if (type == 1) return 4;   // O
        return 3;                  // остальные
    }

    void spawn() {
        cur_.type = nextType_;
        cur_.rot = 0;
        cur_.x = spawnX(cur_.type);
        cur_.y = 0;
        nextType_ = drawFromBag();
        holdUsed_ = false;
        fallTimer_ = 0;
        lockTimer_ = 0;
        if (collides(cur_)) gameOver_ = true;
    }

    void restart() {
        std::fill(&board_[0][0], &board_[0][0] + FIELD_W * FIELD_H, 0);
        bag_.clear();
        nextType_ = drawFromBag();
        holdType_ = -1;
        holdUsed_ = false;
        score_ = 0; level_ = 1; lines_ = 0;
        fallTimer_ = lockTimer_ = 0;
        gameOver_ = paused_ = quit_ = false;
        spawn();
    }

    // ----------------------------------------------------------------
    void handleInput(double dt) {
        bool rotCW   = keyDown('X') || keyDown(VK_UP);
        bool rotCCW  = keyDown('Z');
        bool hard    = keyDown(VK_SPACE);
        bool hold    = keyDown('C') || keyDown(VK_SHIFT);
        bool pause   = keyDown('P');
        bool esc     = keyDown(VK_ESCAPE);
        bool enter   = keyDown(VK_RETURN);
        bool r       = keyDown('R');

        if (gameOver_) {
            if (enter || r) { restart(); return; }
            if (esc) quit_ = true;
            pRotCW_ = rotCW; pRotCCW_ = rotCCW; pHard_ = hard;
            pHold_ = hold; pPause_ = pause; pEsc_ = esc; pRestart_ = r;
            return;
        }

        if (pause && !pPause_) paused_ = !paused_;
        if (esc && !pEsc_) quit_ = true;
        if (r && !pRestart_) { restart(); return; }

        if (!paused_) {
            if (rotCW && !pRotCW_) rotate(true);
            if (rotCCW && !pRotCCW_) rotate(false);
            if (hard && !pHard_) hardDrop();
            if (hold && !pHold_) doHold();
        }

        pRotCW_ = rotCW; pRotCCW_ = rotCCW; pHard_ = hard;
        pHold_ = hold; pPause_ = pause; pEsc_ = esc; pRestart_ = r;

        if (paused_ || gameOver_) return;

        if (dasL_.update(keyDown(VK_LEFT), dt))  moveBy(-1, 0);
        if (dasR_.update(keyDown(VK_RIGHT), dt)) moveBy(+1, 0);
        dasD_.update(keyDown(VK_DOWN), dt);
    }

    void moveBy(int dx, int dy) {
        ActivePiece t = cur_;
        t.x += dx; t.y += dy;
        if (!collides(t)) {
            cur_ = t;
            if (dy == 0) lockTimer_ = 0;
        }
    }

    void rotate(bool cw) {
        if (cur_.type == 1) return;
        int from = cur_.rot;
        int to = cw ? (from + 1) % 4 : (from + 3) % 4;
        const auto& kicks = (cur_.type == 0)
            ? KICKS_I[kickIndex(from, to)]
            : KICKS_JLSTZ[kickIndex(from, to)];
        for (auto& k : kicks) {
            ActivePiece t = cur_;
            t.rot = to;
            t.x += k.x;
            t.y += k.y;
            if (!collides(t)) {
                cur_ = t;
                lockTimer_ = 0;
                return;
            }
        }
    }

    void hardDrop() {
        int cells = 0;
        while (true) {
            ActivePiece t = cur_;
            t.y++;
            if (collides(t)) break;
            cur_ = t;
            cells++;
        }
        score_ += cells * 2;
        lockPiece();
    }

    void doHold() {
        if (holdUsed_) return;
        holdUsed_ = true;
        int stored = holdType_;
        holdType_ = cur_.type;
        if (stored < 0) {
            spawn();
        } else {
            cur_.type = stored;
            cur_.rot = 0;
            cur_.x = spawnX(cur_.type);
            cur_.y = 0;
            fallTimer_ = 0;
            lockTimer_ = 0;
            if (collides(cur_)) gameOver_ = true;
        }
    }

    // ----------------------------------------------------------------
    double fallInterval() const {
        double v = std::pow(0.85, level_ - 1);
        return std::max(0.04, v);
    }

    void update(double dt) {
        ActivePiece test = cur_; test.y++;
        bool onGround = collides(test);

        if (onGround) {
            lockTimer_ += dt;
            if (lockTimer_ >= LOCK_DELAY) { lockPiece(); return; }
        } else {
            lockTimer_ = 0;
        }

        bool soft = dasD_.held;
        double interval = soft ? SOFT_DROP_INTERVAL : fallInterval();
        fallTimer_ += dt;
        while (fallTimer_ >= interval) {
            fallTimer_ -= interval;
            ActivePiece t = cur_; t.y++;
            if (!collides(t)) {
                cur_ = t;
                lockTimer_ = 0;
                if (soft) score_ += 1;
            } else break;
        }
    }

    void lockPiece() {
        for (auto& c : PIECES[cur_.type].rot[cur_.rot]) {
            int bx = cur_.x + c.x;
            int by = cur_.y + c.y;
            if (by < 0) { gameOver_ = true; return; }
            if (bx >= 0 && bx < FIELD_W && by < FIELD_H)
                board_[by][bx] = cur_.type + 1;
        }

        int cleared = 0;
        int y = FIELD_H - 1;
        while (y >= 0) {
            bool full = true;
            for (int x = 0; x < FIELD_W; ++x)
                if (!board_[y][x]) { full = false; break; }
            if (full) {
                ++cleared;
                for (int yy = y; yy > 0; --yy)
                    for (int x = 0; x < FIELD_W; ++x)
                        board_[yy][x] = board_[yy - 1][x];
                for (int x = 0; x < FIELD_W; ++x) board_[0][x] = 0;
            } else --y;
        }

        if (cleared) {
            lines_ += cleared;
            int base = (cleared == 1) ? 100 :
                       (cleared == 2) ? 300 :
                       (cleared == 3) ? 500 : 800;
            score_ += base * level_;
            level_ = lines_ / 10 + 1;
        }
        spawn();
    }

    // ----------------------------------------------------------------
    void drawCell(int bx, int by, WORD attr) {
        int sx = BOARD_OX + bx * CELL_W;
        int sy = BOARD_OY + by;
        for (int i = 0; i < CELL_W; ++i) scr_.put(sx + i, sy, L' ', attr);
    }

    void drawBorder() {
        scr_.put(BORDER_L, BORDER_T, L'\u2554', 0x0F);
        scr_.put(BORDER_R, BORDER_T, L'\u2557', 0x0F);
        scr_.put(BORDER_L, BORDER_B, L'\u255A', 0x0F);
        scr_.put(BORDER_R, BORDER_B, L'\u255D', 0x0F);
        for (int x = BORDER_L + 1; x < BORDER_R; ++x) {
            scr_.put(x, BORDER_T, L'\u2550', 0x0F);
            scr_.put(x, BORDER_B, L'\u2550', 0x0F);
        }
        for (int y = BORDER_T + 1; y < BORDER_B; ++y) {
            scr_.put(BORDER_L, y, L'\u2551', 0x0F);
            scr_.put(BORDER_R, y, L'\u2551', 0x0F);
        }
    }

    void drawPreview(int type, int ox, int oy) {
        int mnx = 99, mxx = -1, mny = 99, mxy = -1;
        for (auto& c : PIECES[type].rot[0]) {
            mnx = std::min(mnx, c.x); mxx = std::max(mxx, c.x);
            mny = std::min(mny, c.y); mxy = std::max(mxy, c.y);
        }
        int w = mxx - mnx + 1, h = mxy - mny + 1;
        int baseX = ox + (8 - w * CELL_W) / 2;
        int baseY = oy + (4 - h) / 2;
        for (auto& c : PIECES[type].rot[0]) {
            int px = baseX + (c.x - mnx) * CELL_W;
            int py = baseY + (c.y - mny);
            for (int i = 0; i < CELL_W; ++i)
                scr_.put(px + i, py, L' ', PIECES[type].color);
        }
    }

    void drawSidebar() {
        WORD white = FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY;
        WORD dim   = FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE;

        int x = SIDEBAR_X;
        scr_.putStr(x, 2, L"NEXT", white);
        drawPreview(nextType_, x, 3);

        scr_.putStr(x, 8, L"HOLD", white);
        if (holdType_ >= 0) drawPreview(holdType_, x, 9);

        scr_.putStr(x, 14, L"SCORE", dim);
        scr_.putStr(x, 15, std::to_wstring(score_), white);

        scr_.putStr(x, 17, L"LEVEL", dim);
        scr_.putStr(x, 18, std::to_wstring(level_), white);

        scr_.putStr(x, 20, L"LINES", dim);
        scr_.putStr(x, 21, std::to_wstring(lines_), white);
    }

    void renderOverlay(const std::wstring& text, WORD attr) {
        int len = (int)text.size();
        int x = (SCREEN_W - len) / 2;
        int y = SCREEN_H / 2;
        for (int i = -2; i < len + 2; ++i)
            for (int j = -1; j <= 1; ++j)
                scr_.put(x + i, y + j, L' ', 0);
        scr_.putStr(x, y, text, attr);
    }

    void render() {
        scr_.clear();
        drawBorder();

        for (int y = 0; y < FIELD_H; ++y)
            for (int x = 0; x < FIELD_W; ++x)
                if (board_[y][x])
                    drawCell(x, y, PIECES[board_[y][x] - 1].color);

        if (!gameOver_) {
            ActivePiece ghost = cur_;
            while (true) {
                ActivePiece t = ghost; t.y++;
                if (collides(t)) break;
                ghost = t;
            }
            for (auto& c : PIECES[cur_.type].rot[cur_.rot]) {
                int bx = ghost.x + c.x;
                int by = ghost.y + c.y;
                if (by < 0 || by >= FIELD_H) continue;
                if (bx < 0 || bx >= FIELD_W) continue;
                bool overlap = false;
                for (auto& cc : PIECES[cur_.type].rot[cur_.rot])
                    if (cur_.x + cc.x == bx && cur_.y + cc.y == by) { overlap = true; break; }
                if (overlap) continue;
                int sx = BOARD_OX + bx * CELL_W;
                int sy = BOARD_OY + by;
                WORD fg = toFg(PIECES[cur_.type].color);
                for (int i = 0; i < CELL_W; ++i)
                    scr_.put(sx + i, sy, L'\u2591', fg);
            }

            for (auto& c : PIECES[cur_.type].rot[cur_.rot]) {
                int bx = cur_.x + c.x;
                int by = cur_.y + c.y;
                if (by < 0 || by >= FIELD_H) continue;
                if (bx < 0 || bx >= FIELD_W) continue;
                drawCell(bx, by, PIECES[cur_.type].color);
            }
        }

        drawSidebar();

        if (paused_)
            renderOverlay(L"PAUSED",
                FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY);
        if (gameOver_)
            renderOverlay(L"GAME OVER", FOREGROUND_RED | FOREGROUND_INTENSITY);

        scr_.present();
    }
};

// ---------------------------------------------------------------------------
//  Настройка консоли
// ---------------------------------------------------------------------------
static void setupConsole() {
    HANDLE h = GetStdHandle(STD_OUTPUT_HANDLE);
    SMALL_RECT small{0, 0, 1, 1};
    SetConsoleWindowInfo(h, TRUE, &small);
    COORD size{(SHORT)SCREEN_W, (SHORT)SCREEN_H};
    SetConsoleScreenBufferSize(h, size);
    SMALL_RECT rect{0, 0, (SHORT)(SCREEN_W - 1), (SHORT)(SCREEN_H - 1)};
    SetConsoleWindowInfo(h, TRUE, &rect);
    SetConsoleTitleW(L"Tetris");
}

int main() {
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
    setupConsole();
    Screen scr(SCREEN_W, SCREEN_H);
    Game game(scr);
    game.run();
    return 0;
}
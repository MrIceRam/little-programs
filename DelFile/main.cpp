namespace fs = std::filesystem;
using namespace std;
int main(){
//Даем права на чтение/выполнение/запись файла всем пользователям
fs::permissions("d:/it/test.txt", fs::perms::all);
//Удаляем файл
fs::remove("d:/it/test.txt");
}
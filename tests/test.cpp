#include <vector>
#include <queue>
#include <unordered_map>
#include <algorithm>
#include <memory>
#include <iostream>
#include <thread>
#include <mutex>
#include <chrono>
#include <condition_variable>
#include <string.h>

#include "tcp.h"
#include "../tests/server.h"

using namespace std;

auto cv = condition_variable{};
auto q = queue<int>{};
auto mtx = mutex{};


void printints(){
    auto i = 0;
    while(1){
        auto lock = unique_lock<mutex>{mtx};
        // printf("thread ID: %d\n", gettid());

        while(q.empty()){
            cout << gettid() << " is sleeping " << endl;
            cv.wait(lock);
            cout << gettid() << " is waked up " << endl;
        }

        // cout << gettid() << " attend contention " << endl;

        i = q.front();
        q.pop();

        cout << gettid() << " got: " << i << endl;
    }
}

auto generateints(){
    for (auto i = 0; i < 20; i++){
        this_thread::sleep_for(chrono::seconds(2));
        
        {
            auto lock = scoped_lock{mtx};
            q.push(i);
        }

        cv.notify_all();
    }
}

class A{
    public:
    A(int i){}

    A(const A& a){
        printf("A copy constructor\n");
    }

    virtual void a(){
        printf("dsfasf");
    }
};

class B : public A{
    public:
        B() : A(10){}
        B(const B& b) : A(b){
            printf("B copy constructor\n");
        }
    
    void a() override{}

        void t(){
            A::a();
        }
};

int main(int argc, char **argv)
{
    char str[20];

    cout << strlen(str);
    // tcpserv02();
}

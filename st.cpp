#include <iostream>
#include <stack>
using namespace std;
int main() {
    stack<int> myStack;

    myStack.push(10);
    myStack.push(20);
    myStack.push(30);

    for (int i = 0; i < 15; ++i) {
        cout << "Top element: " << myStack.top() <<endl;
        myStack.pop();
    }


    // Remove this line or push an integer value instead
    // myStack.push(40);  // if you need to push another number

    return 0;
}
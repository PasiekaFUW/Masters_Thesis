#include "ClassA.h"
#include <iostream>

ClassA::ClassA() {}

void ClassA::sayHello() const {
    std::cout << "Hello from ClassA!" << std::endl;
}
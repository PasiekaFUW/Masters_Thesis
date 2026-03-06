#include "ClassB.h"
#include <iostream>
#include "TString.h"

// g++ -Wall -I./ `root-config --cflags` ClassB.cc main.cc `root-config --libs` -o myApplication
ClassB::ClassB() {
    TString aText("This is a text");
    aText.Print();
}

void ClassB::sayHello() const {
    std::cout << "Hello from ClassB!" << std::endl;
}
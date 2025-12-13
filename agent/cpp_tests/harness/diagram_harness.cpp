#include <iostream>
#include <string>
#include <vector>
#include <cstdlib>

// This harness attempts to exercise small parts of the project API. It
// is optional and will only be compiled if Qt (Widgets) is available in
// the environment. It accepts simple commands and returns 0 on success.

#include "diagramscene.h"
#include "diagramitem.h"

int main(int argc, char** argv) {
    try {
        // Minimal arg parsing: commands of form:
        //   arg <value>
        //   long <string>
        //   parse int <val>
        //   parse float <val>
        if (argc < 2) {
            std::cout << "harness: no-op" << std::endl;
            return 0;
        }
        std::string cmd = argv[1];
        if (cmd == "arg") {
            // call into project by creating DiagramItem and applying numeric arg
            double v = 0.0;
            if (argc >= 3) v = atof(argv[2]);
            // instantiate minimal objects (no QApplication here; safe for non-GUI tests in many builds)
            DiagramItem item(DiagramItem::Step, nullptr);
            item.setWidth(static_cast<qreal>(v));
            std::cout << "harness: setWidth " << v << std::endl;
            return 0;
        } else if (cmd == "long") {
            std::string val = argc >= 3 ? argv[2] : std::string(1000, 'a');
            DiagramItem item(DiagramItem::Step, nullptr);
            item.textContent = QString::fromStdString(val);
            std::cout << "harness: longtext len=" << val.size() << std::endl;
            return 0;
        } else if (cmd == "parse") {
            if (argc < 4) {
                std::cerr << "harness: parse missing args" << std::endl;
                return 2;
            }
            std::string typ = argv[2];
            std::string sval = argv[3];
            if (typ == "int") {
                try {
                    int x = std::stoi(sval);
                    std::cout << "harness: parsed int=" << x << std::endl;
                    return 0;
                } catch (...) {
                    std::cerr << "harness: parse int exception" << std::endl;
                    return 3;
                }
            } else if (typ == "float") {
                try {
                    double x = std::stod(sval);
                    std::cout << "harness: parsed float=" << x << std::endl;
                    return 0;
                } catch (...) {
                    std::cerr << "harness: parse float exception" << std::endl;
                    return 4;
                }
            }
        }
        std::cout << "harness: unknown command" << std::endl;
        return 0;
    } catch (...) {
        return 5;
    }
}

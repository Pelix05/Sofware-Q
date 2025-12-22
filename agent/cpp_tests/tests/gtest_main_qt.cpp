#include <QApplication>
#include <gtest/gtest.h>

// 全局开关（与被测代码保持一致）
extern bool isInsertPath;

int main(int argc, char** argv) {
    QApplication app(argc, argv);
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
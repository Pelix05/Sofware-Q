#include <gtest/gtest.h>
#include <QApplication>
#include <QToolButton>
#include <QComboBox>
#include <memory>

#include "mainwindow.h"
#include "diagramscene.h"

extern bool isInsertPath;

class MainWindowTest : public ::testing::Test {
protected:
    void SetUp() override {
        mainWindow = std::make_unique<MainWindow>();
    }

    void TearDown() override {
        mainWindow.reset();
    }

    std::unique_ptr<MainWindow> mainWindow;
};

TEST_F(MainWindowTest, WindowCreatesWithoutCrash) {
    EXPECT_NE(mainWindow.get(), nullptr);
}

TEST_F(MainWindowTest, SceneIsInitialized) {
    // MainWindow 应该创建并持有 DiagramScene
    EXPECT_NE(mainWindow->findChild<DiagramScene*>(), nullptr);
}

TEST_F(MainWindowTest, ToolButtonsExist) {
    // 验证工具按钮存在（通过查找所有QToolButton）
    auto toolButtons = mainWindow->findChildren<QToolButton*>();
    EXPECT_GT(toolButtons.size(), 0) << "No QToolButton found in MainWindow";
    
    // 如果源码设置了objectName，可以精确查找
    // 否则只验证按钮数量足够
    EXPECT_GE(toolButtons.size(), 2) << "Expected at least 2 tool buttons";
}

TEST_F(MainWindowTest, ItemComboBoxPopulated) {
    auto itemCombo = mainWindow->findChild<QComboBox*>();
    EXPECT_NE(itemCombo, nullptr);
    EXPECT_GT(itemCombo->count(), 0);
}
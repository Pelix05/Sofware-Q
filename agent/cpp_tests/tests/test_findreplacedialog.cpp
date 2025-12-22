#include <gtest/gtest.h>
#include <QSignalSpy>
#include <QLineEdit>
#include <QPushButton>
#include <memory>

#include "findreplacedialog.h"

extern bool isInsertPath;

class FindReplaceDialogTest : public ::testing::Test {
protected:
    void SetUp() override {
        dialog = std::make_unique<FindReplaceDialog>();
    }

    void TearDown() override {
        dialog.reset();
    }

    std::unique_ptr<FindReplaceDialog> dialog;
};

TEST_F(FindReplaceDialogTest, DialogCreatesWithoutCrash) {
    EXPECT_NE(dialog.get(), nullptr);
}

TEST_F(FindReplaceDialogTest, FindTextSignalEmitsOnButtonClick) {
    QSignalSpy spy(dialog.get(), &FindReplaceDialog::findText);
    
    auto lineEdits = dialog->findChildren<QLineEdit*>();
    auto buttons = dialog->findChildren<QPushButton*>();
    
    ASSERT_GE(lineEdits.size(), 1) << "No QLineEdit found";
    ASSERT_GE(buttons.size(), 1) << "No QPushButton found";
    
    lineEdits[0]->setText("test");
    buttons[0]->click();
    
    EXPECT_GE(spy.count(), 1);
    if (spy.count() > 0) {
        EXPECT_EQ(spy.first().at(0).toString(), QString("test"));
    }
}

TEST_F(FindReplaceDialogTest, ReplaceTextSignalEmitsWithCorrectParams) {
    QSignalSpy spy(dialog.get(), &FindReplaceDialog::replaceText);
    
    auto lineEdits = dialog->findChildren<QLineEdit*>();
    auto buttons = dialog->findChildren<QPushButton*>();
    
    ASSERT_GE(lineEdits.size(), 2) << "Need at least 2 QLineEdit";
    ASSERT_GE(buttons.size(), 2) << "Need at least 2 QPushButton";
    
    lineEdits[0]->setText("old");
    lineEdits[1]->setText("new");
    buttons[1]->click();
    
    EXPECT_GE(spy.count(), 1);
    if (spy.count() > 0) {
        EXPECT_EQ(spy.first().at(0).toString(), QString("old"));
        EXPECT_EQ(spy.first().at(1).toString(), QString("new"));
    }
}
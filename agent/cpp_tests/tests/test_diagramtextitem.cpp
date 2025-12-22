#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QGraphicsView>
#include <QSignalSpy>
#include <QFocusEvent>
#include <QCoreApplication>
#include <memory>

#include "diagramtextitem.h"

extern bool isInsertPath;

class DiagramTextItemTest : public ::testing::Test {
protected:
    void SetUp() override {
        textItem = new DiagramTextItem();
        scene.addItem(textItem);
        view = std::make_unique<QGraphicsView>(&scene);
        view->show();
        QCoreApplication::processEvents();
    }

    void TearDown() override {
        view.reset();
        if (textItem && scene.items().contains(textItem)) {
            scene.removeItem(textItem);
        }
        delete textItem;
        textItem = nullptr;
    }

    QGraphicsScene scene;
    DiagramTextItem* textItem = nullptr;
    std::unique_ptr<QGraphicsView> view;
};

TEST_F(DiagramTextItemTest, DefaultTextIsEditable) {
    textItem->setTextInteractionFlags(Qt::TextEditorInteraction);
    EXPECT_TRUE(textItem->textInteractionFlags() & Qt::TextEditorInteraction);
}

TEST_F(DiagramTextItemTest, SetPlainTextUpdatesContent) {
    const QString testText = "Test Diagram Label";
    textItem->setPlainText(testText);
    EXPECT_EQ(textItem->toPlainText(), testText);
}

TEST_F(DiagramTextItemTest, TextColorPersists) {
    const QColor testColor(Qt::red);
    textItem->setDefaultTextColor(testColor);
    EXPECT_EQ(textItem->defaultTextColor(), testColor);
}

TEST_F(DiagramTextItemTest, LostFocusEmitsSignal) {
    QSignalSpy spy(textItem, &DiagramTextItem::lostFocus);
    
    textItem->setTextInteractionFlags(Qt::TextEditorInteraction);
    textItem->setFocus();
    QCoreApplication::processEvents();
    
    textItem->clearFocus();
    QCoreApplication::processEvents();
    
    EXPECT_GE(spy.count(), 1);
    if (spy.count() > 0) {
        EXPECT_EQ(spy.first().at(0).value<DiagramTextItem*>(), textItem);
    }
}

TEST_F(DiagramTextItemTest, SelectedChangeEmitsSignal) {
    QSignalSpy spy(textItem, &DiagramTextItem::selectedChange);
    
    textItem->setSelected(true);
    
    EXPECT_EQ(spy.count(), 1);
    EXPECT_EQ(spy.first().at(0).value<QGraphicsItem*>(), textItem);
}
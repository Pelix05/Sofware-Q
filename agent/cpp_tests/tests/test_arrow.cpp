#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QMenu>
#include <memory>

#include "diagramitem.h"
#include "arrow.h"

extern bool isInsertPath;

class ArrowTest : public ::testing::Test {
protected:
    void SetUp() override {
        menu = std::make_unique<QMenu>();
        startItem = new DiagramItem(DiagramItem::Step, menu.get());
        endItem = new DiagramItem(DiagramItem::Step, menu.get());
        
        startItem->setPos(0, 0);
        endItem->setPos(200, 150);
        
        scene.addItem(startItem);
        scene.addItem(endItem);
        
        arrow = new Arrow(startItem, endItem);
        scene.addItem(arrow);
    }

    void TearDown() override {
        if (arrow && scene.items().contains(arrow)) {
            scene.removeItem(arrow);
        }
        delete arrow;
        
        if (startItem && scene.items().contains(startItem)) {
            scene.removeItem(startItem);
        }
        delete startItem;
        
        if (endItem && scene.items().contains(endItem)) {
            scene.removeItem(endItem);
        }
        delete endItem;
        
        startItem = nullptr;
        endItem = nullptr;
        arrow = nullptr;
    }

    QGraphicsScene scene;
    DiagramItem* startItem = nullptr;
    DiagramItem* endItem = nullptr;
    Arrow* arrow = nullptr;
    std::unique_ptr<QMenu> menu;
};

TEST_F(ArrowTest, StartItemReturnsCorrectItem) {
    EXPECT_EQ(arrow->startItem(), startItem);
}

TEST_F(ArrowTest, EndItemReturnsCorrectItem) {
    EXPECT_EQ(arrow->endItem(), endItem);
}

TEST_F(ArrowTest, UpdatePositionAfterItemMove) {
    QLineF originalLine = arrow->line();
    
    endItem->setPos(400, 300);
    arrow->updatePosition();
    
    QLineF newLine = arrow->line();
    EXPECT_NE(originalLine, newLine);
    EXPECT_GT(newLine.length(), originalLine.length());
}

TEST_F(ArrowTest, BoundingRectContainsArrowHead) {
    arrow->updatePosition();
    QRectF bounds = arrow->boundingRect();
    
    EXPECT_GT(bounds.width(), 0);
    EXPECT_GT(bounds.height(), 0);
    
    // 验证包围盒包含线段端点
    QLineF line = arrow->line();
    EXPECT_TRUE(bounds.contains(line.p1()));
    EXPECT_TRUE(bounds.contains(line.p2()));
}
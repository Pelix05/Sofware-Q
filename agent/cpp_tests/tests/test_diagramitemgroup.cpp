#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QMenu>
#include <memory>

#include "diagramitemgroup.h"
#include "diagramitem.h"

extern bool isInsertPath;

class DiagramItemGroupTest : public ::testing::Test {
protected:
    void SetUp() override {
        menu = std::make_unique<QMenu>();
        scene = std::make_unique<QGraphicsScene>();
        group = new DiagramItemGroup();
        scene->addItem(group);
    }

    void TearDown() override {
        if (group && scene->items().contains(group)) {
            scene->removeItem(group);
        }
        delete group;
        group = nullptr;
    }

    std::unique_ptr<QGraphicsScene> scene;
    std::unique_ptr<QMenu> menu;
    DiagramItemGroup* group = nullptr;
};

TEST_F(DiagramItemGroupTest, GroupCreatesWithoutCrash) {
    EXPECT_NE(group, nullptr);
}

TEST_F(DiagramItemGroupTest, AddItemIncreasesChildCount) {
    auto* item = new DiagramItem(DiagramItem::Step, menu.get());
    int initialCount = group->childItems().size();
    
    // 使用QGraphicsItem*版本
    group->addItem(static_cast<QGraphicsItem*>(item));
    
    EXPECT_EQ(group->childItems().size(), initialCount + 1);
    EXPECT_TRUE(group->childItems().contains(item));
}

TEST_F(DiagramItemGroupTest, GetTopLeftReturnsValidPoint) {
    auto* item1 = new DiagramItem(DiagramItem::Step, menu.get());
    auto* item2 = new DiagramItem(DiagramItem::Conditional, menu.get());
    
    item1->setPos(100, 100);
    item2->setPos(50, 150);
    
    group->addItem(static_cast<QGraphicsItem*>(item1));
    group->addItem(static_cast<QGraphicsItem*>(item2));
    
    QPointF topLeft = group->getTopLeft();
    EXPECT_LE(topLeft.x(), 100);
    EXPECT_LE(topLeft.y(), 150);
}

TEST_F(DiagramItemGroupTest, GroupContainsAddedItems) {
    auto* item = new DiagramItem(DiagramItem::Step, menu.get());
    group->addItem(static_cast<QGraphicsItem*>(item));
    
    EXPECT_EQ(item->parentItem(), group);
}
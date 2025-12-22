#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QMenu>
#include <memory>

#include "diagramitem.h"
#include "diagrampath.h"

extern bool isInsertPath;

class DiagramPathTest : public ::testing::Test {
protected:
    void SetUp() override {
        menu = std::make_unique<QMenu>();
        startItem = new DiagramItem(DiagramItem::Step, menu.get());
        endItem = new DiagramItem(DiagramItem::Step, menu.get());
        
        startItem->setPos(0, 0);
        endItem->setPos(300, 200);
        
        scene.addItem(startItem);
        scene.addItem(endItem);
        
        path = new DiagramPath(startItem, endItem, 
                              DiagramItem::TF_Right, 
                              DiagramItem::TF_Left);
        scene.addItem(path);
    }

    void TearDown() override {
        if (path && scene.items().contains(path)) {
            scene.removeItem(path);
        }
        delete path;
        
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
        path = nullptr;
    }

    QGraphicsScene scene;
    DiagramItem* startItem = nullptr;
    DiagramItem* endItem = nullptr;
    DiagramPath* path = nullptr;
    std::unique_ptr<QMenu> menu;
};

TEST_F(DiagramPathTest, GetStartItemReturnsCorrectItem) {
    EXPECT_EQ(path->getStartItem(), startItem);
}

TEST_F(DiagramPathTest, GetEndItemReturnsCorrectItem) {
    EXPECT_EQ(path->getEndItem(), endItem);
}

TEST_F(DiagramPathTest, UpdatePathGeneratesNonEmptyPath) {
    path->updatePath();
    const QPainterPath& painterPath = path->path();
    EXPECT_FALSE(painterPath.isEmpty());
    EXPECT_GT(painterPath.elementCount(), 2);
}

TEST_F(DiagramPathTest, PathConnectsStartAndEndAnchors) {
    path->updatePath();
    const QPainterPath& painterPath = path->path();
    
    QPointF startAnchor = startItem->mapToScene(
        startItem->linkWhere()[DiagramItem::TF_Right].center());
    QPointF endAnchor = endItem->mapToScene(
        endItem->linkWhere()[DiagramItem::TF_Left].center());
    
    // 验证路径包含起点和终点附近的元素
    bool hasStartRegion = false;
    bool hasEndRegion = false;
    
    for (int i = 0; i < painterPath.elementCount(); ++i) {
        QPainterPath::Element elem = painterPath.elementAt(i);
        QPointF pt(elem.x, elem.y);
        
        if ((pt - startAnchor).manhattanLength() < 20.0) {
            hasStartRegion = true;
        }
        if ((pt - endAnchor).manhattanLength() < 20.0) {
            hasEndRegion = true;
        }
    }
    
    EXPECT_TRUE(hasStartRegion);
    EXPECT_TRUE(hasEndRegion);
}
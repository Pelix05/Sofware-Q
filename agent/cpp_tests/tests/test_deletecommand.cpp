#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QMenu>
#include <memory>

#include "diagramitem.h"
#include "deletecommand.h"

extern bool isInsertPath;

class DeleteCommandTest : public ::testing::Test {

protected:
    void SetUp() override {
        menu = std::make_unique<QMenu>();
        item = new DiagramItem(DiagramItem::Step, menu.get());
        item->setPos(QPointF(10.0, 15.0));
        scene.addItem(item);
    }

    void TearDown() override {
        if (item && scene.items().contains(item)) {
            scene.removeItem(item);
        }
        delete item;
        item = nullptr;
    }

    QGraphicsScene scene;
    DiagramItem* item = nullptr;
    std::unique_ptr<QMenu> menu;
};

TEST_F(DeleteCommandTest, RedoRemovesItemFromScene) {
    ASSERT_TRUE(scene.items().contains(item));
    DeleteCommand cmd(item, &scene);
    cmd.redo();
    EXPECT_FALSE(scene.items().contains(item));
}

TEST_F(DeleteCommandTest, UndoRestoresItemWithOriginalPosition) {
    DeleteCommand cmd(item, &scene);
    cmd.redo();
    ASSERT_FALSE(scene.items().contains(item));
    cmd.undo();
    EXPECT_TRUE(scene.items().contains(item));
    EXPECT_EQ(item->pos(), QPointF(10.0, 15.0));
}
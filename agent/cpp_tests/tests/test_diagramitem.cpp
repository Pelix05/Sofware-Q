#include <gtest/gtest.h>
#include <QGraphicsScene>
#include <QMenu>
#include <memory>

#include "diagramitem.h"

extern bool isInsertPath;

class DiagramItemTest : public ::testing::Test {
protected:
    void SetUp() override {
        menu = std::make_unique<QMenu>();
        item = new DiagramItem(DiagramItem::Step, menu.get());
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

TEST_F(DiagramItemTest, SetFixedSizeUpdatesStoredSize) {
    const QSizeF newSize(200.0, 120.0);
    item->setFixedSize(newSize);
    EXPECT_DOUBLE_EQ(item->getSize().width(), newSize.width());
    EXPECT_DOUBLE_EQ(item->getSize().height(), newSize.height());
}

TEST_F(DiagramItemTest, RectWhereReturnsEightResizeHandles) {
    const auto rects = item->rectWhere();
    ASSERT_EQ(rects.size(), 8);

    const QRectF topRect = rects.value(DiagramItem::TF_Top);
    EXPECT_DOUBLE_EQ(topRect.topLeft().x(), 70.0);
    EXPECT_DOUBLE_EQ(topRect.topLeft().y(), 0.0);
    EXPECT_DOUBLE_EQ(topRect.width(), 10.0);
    EXPECT_DOUBLE_EQ(topRect.height(), 10.0);

    const QRectF rightRect = rects.value(DiagramItem::TF_Right);
    EXPECT_DOUBLE_EQ(rightRect.topLeft().x(), 140.0);
    EXPECT_DOUBLE_EQ(rightRect.topLeft().y(), 45.0);
}

TEST_F(DiagramItemTest, LinkWhereReturnsFourConnectionAnchors) {
    const auto links = item->linkWhere();
    ASSERT_EQ(links.size(), 4);

    const QRectF topLink = links.value(DiagramItem::TF_Top);
    EXPECT_DOUBLE_EQ(topLink.topLeft().x(), 70.0);
    EXPECT_DOUBLE_EQ(topLink.topLeft().y(), -15.0);

    const QRectF bottomLink = links.value(DiagramItem::TF_Bottom);
    EXPECT_DOUBLE_EQ(bottomLink.topLeft().x(), 70.0);
    EXPECT_DOUBLE_EQ(bottomLink.topLeft().y(), 105.0);
}

TEST_F(DiagramItemTest, RotationAnglePersists) {
    item->setRotationAngle(45.0);
    EXPECT_DOUBLE_EQ(item->rotationAngle(), 45.0);
}
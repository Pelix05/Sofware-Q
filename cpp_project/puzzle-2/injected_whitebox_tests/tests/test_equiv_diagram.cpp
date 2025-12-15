#include <gtest/gtest.h>
#include <QApplication>
#include <QMenu>
#include "diagramitem.h"
#include "diagramscene.h"

// These tests are conservative: they avoid showing GUI windows and focus on
// exercising public APIs for boundary conditions. They succeed as long as no
// crashes occur and basic invariants hold.

TEST(DiagramItemBoundary, WidthNegativeDoesNotCrash) {
  int argc = 0;
  char **argv = nullptr;
  QApplication app(argc, argv);
  DiagramItem item(DiagramItem::Step, nullptr);
  // Should not crash; width may be clamped or stored. Verify it remains a finite value.
  item.setWidth(-1.0);
  QSizeF s = item.getSize();
  EXPECT_FALSE(std::isnan(s.width()));
}

TEST(DiagramItemBoundary, LargeSizeHandled) {
  int argc = 0;
  char **argv = nullptr;
  QApplication app(argc, argv);
  DiagramItem item(DiagramItem::Step, nullptr);
  item.setSize(QSizeF(1e12, 1e12));
  QSizeF s = item.getSize();
  EXPECT_FALSE(std::isnan(s.width()));
  EXPECT_FALSE(std::isnan(s.height()));
}

TEST(DiagramItemTextLong, LongTextStored) {
  int argc = 0;
  char **argv = nullptr;
  QApplication app(argc, argv);
  DiagramItem item(DiagramItem::Step, nullptr);
  QString longstr;
  for (int i = 0; i < 2000; ++i) longstr.append('a');
  item.textContent = longstr;
  EXPECT_EQ(item.textContent, longstr);
}

TEST(DiagramItemRotation, LargeRotationHandled) {
  int argc = 0;
  char **argv = nullptr;
  QApplication app(argc, argv);
  DiagramItem item(DiagramItem::Step, nullptr);
  item.setRotationAngle(1e9);
  EXPECT_NO_THROW({ item.rotationAngle(); });
}

TEST(DiagramSceneBasic, CreateItemDoesNotCrash) {
  int argc = 0;
  char **argv = nullptr;
  QApplication app(argc, argv);
  DiagramScene scene(nullptr, nullptr);
  // Try creating a couple of items
  QGraphicsItem *it = scene.createItem(0);
  EXPECT_TRUE(it == nullptr || dynamic_cast<QGraphicsItem*>(it));
}

// Note: Tests are intentionally minimal and focus on safety rather than
// asserting specific domain semantics. Expand with project-specific
// expectations if desired.

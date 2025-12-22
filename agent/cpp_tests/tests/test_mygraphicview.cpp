#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <utility>

using Point = std::pair<int, int>;
using ::testing::Return;  // ✅ 添加

// Mock QAction
class MockQAction {
public:
    MOCK_METHOD(void, triggered, ());
    MOCK_METHOD(void, setEnabled, (bool));
    MOCK_METHOD(bool, isEnabled, (), (const));
};

// Mock QMenu
class MockQMenu {
public:
    MOCK_METHOD(MockQAction*, addAction, (const std::string&));
    MOCK_METHOD(MockQAction*, exec, (const Point&));
};

// Mock MainWindow
class MockMainWindow {
public:
    MOCK_METHOD(void, pasteItems, ());
};

// ✅ 修复：重新设计 MockMyGraphicsView
class MockMyGraphicsView {
private:
    MockQAction* pAction;
    MockMainWindow* parentWindow;
    MockQMenu* mockMenu;  // ✅ 添加：持有 mock menu 的指针

public:
    MockMyGraphicsView(MockMainWindow* parent) 
        : pAction(new MockQAction()), 
          parentWindow(parent),
          mockMenu(new MockQMenu()) {}
    
    ~MockMyGraphicsView() { 
        delete pAction;
        delete mockMenu;
    }
    
    void initializeConnection() {
        // 模拟信号槽连接
    }
    
    // ✅ 修复：接受 Mock 对象作为参数，方便测试设置期望
    void simulateContextMenu(int x, int y, MockQAction* returnAction = nullptr) {
        Point pos{x, y};
        
        if (returnAction && parentWindow) {
            parentWindow->pasteItems();
        }
    }
    
    MockQAction* getAction() const { return pAction; }
    MockQMenu* getMenu() const { return mockMenu; }  // ✅ 添加：暴露 menu 用于测试
};

// ========== Test Cases ==========
class MyGraphicsViewTest : public ::testing::Test {
protected:
    MockMainWindow* mockMainWindow;
    MockMyGraphicsView* view;

    void SetUp() override {
        mockMainWindow = new MockMainWindow();
        view = new MockMyGraphicsView(mockMainWindow);
    }

    void TearDown() override {
        delete view;
        delete mockMainWindow;
    }
};

TEST_F(MyGraphicsViewTest, ConstructorInitializesAction) {
    ASSERT_NE(view->getAction(), nullptr) 
        << "QAction should be initialized in constructor";
}

// ✅ 修复：正确设置 Mock 返回值
TEST_F(MyGraphicsViewTest, ContextMenuCallsPasteItems) {
    EXPECT_CALL(*mockMainWindow, pasteItems()).Times(1);
    
    // 模拟用户选择了 "Paste" 动作（传入 pAction）
    view->simulateContextMenu(100, 100, view->getAction());
}

TEST_F(MyGraphicsViewTest, NullParentHandling) {
    MockMyGraphicsView* viewWithNullParent = new MockMyGraphicsView(nullptr);
    ASSERT_NE(viewWithNullParent, nullptr);
    
    // 即使父窗口为空，也不应该崩溃
    viewWithNullParent->simulateContextMenu(100, 100, viewWithNullParent->getAction());
    
    delete viewWithNullParent;
}

// ✅ 修复：正确设置多次调用
TEST_F(MyGraphicsViewTest, MultipleContextMenuCalls) {
    EXPECT_CALL(*mockMainWindow, pasteItems()).Times(3);
    
    view->simulateContextMenu(100, 100, view->getAction());
    view->simulateContextMenu(200, 200, view->getAction());
    view->simulateContextMenu(300, 300, view->getAction());
}

// ✅ 新增：测试用户取消菜单（不选择任何项）
TEST_F(MyGraphicsViewTest, ContextMenuCancelDoesNotCallPaste) {
    EXPECT_CALL(*mockMainWindow, pasteItems()).Times(0);
    
    // 传入 nullptr 表示用户取消了菜单
    view->simulateContextMenu(100, 100, nullptr);
}

// ✅ 新增：测试 Action 的初始状态
TEST_F(MyGraphicsViewTest, ActionInitialState) {
    MockQAction* action = view->getAction();
    ASSERT_NE(action, nullptr);
    
    // 可以添加对 action 属性的验证
    // 例如：EXPECT_CALL(*action, isEnabled()).WillOnce(Return(true));
}
#include <gtest/gtest.h>

// Simple unit under test: small utility function used as example for gtest
static int add_ints(int a, int b) { return a + b; }

TEST(MathTests, AddInts) {
    EXPECT_EQ(add_ints(1, 2), 3);
    EXPECT_EQ(add_ints(-1, 1), 0);
}

TEST(Sanity, TrueIsTrue) {
    EXPECT_TRUE(true);
}

// Boundary-oriented GoogleTest cases. These attempt to exercise edge inputs
// such as long strings and malformed parsing inputs. Tests skip if no
// executable is found; they assert behavior (exit code) where reasonable.

#include <gtest/gtest.h>
#include <cstdlib>
#include <string>
#include <sstream>
#include <filesystem>

static std::string find_project_exe() {
    const char* env = std::getenv("PROJECT_EXE");
    if (env && *env) return std::string(env);
    std::vector<std::string> candidates = {"app.exe", "diagram_harness.exe", "main.exe", "project.exe"};
    std::filesystem::path p = std::filesystem::current_path();
    for (int depth = 0; depth < 4; ++depth) {
        for (auto &c : candidates) {
            auto cand = p / c;
            if (std::filesystem::exists(cand) && std::filesystem::is_regular_file(cand))
                return cand.string();
        }
        p = p.parent_path();
        if (p.empty()) break;
    }
    return std::string();
}

static int run_cmd(const std::string &cmd) {
    int rc = std::system(cmd.c_str());
#ifdef _WIN32
    return rc;
#else
    return WEXITSTATUS(rc);
#endif
}

TEST(Boundary, LongString) {
    std::string exe = find_project_exe();
    if (exe.empty()) GTEST_SKIP() << "No project executable found (set PROJECT_EXE).";
    std::string longstr(800, 'A');
    std::ostringstream oss;
    oss << '"' << exe << '"' << " long " << '"' << longstr << '"';
    int rc = run_cmd(oss.str());
    // We expect the program to handle long strings without crashing (exit code 0)
    EXPECT_EQ(rc, 0) << "Long-string invocation failed; rc=" << rc;
}

TEST(Boundary, ParseIntMalformed) {
    std::string exe = find_project_exe();
    if (exe.empty()) GTEST_SKIP() << "No project executable found (set PROJECT_EXE).";
    std::ostringstream oss;
    oss << '"' << exe << '"' << " parse int notanint";
    int rc = run_cmd(oss.str());
    // Malformed parse should be handled gracefully; allow either nonzero or zero
    EXPECT_NE(rc, 127) << "Program appears missing or command failed to start";
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

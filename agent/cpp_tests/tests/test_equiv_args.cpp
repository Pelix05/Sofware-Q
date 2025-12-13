// Lightweight GoogleTest that runs the project executable with several
// equivalence-style argument variants. If no executable is found via the
// environment variable PROJECT_EXE or simple discovery, the tests are skipped.

#include <gtest/gtest.h>
#include <cstdlib>
#include <string>
#include <vector>
#include <sstream>
#include <filesystem>

static std::string find_project_exe() {
    const char* env = std::getenv("PROJECT_EXE");
    if (env && *env) return std::string(env);
    // Try common names in parent directories (best-effort)
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
    // Use system() and return exit code; tests treat non-zero as failure where expected.
    int rc = std::system(cmd.c_str());
#ifdef _WIN32
    return rc;
#else
    return WEXITSTATUS(rc);
#endif
}

TEST(EquivalenceArgs, BasicVariants) {
    std::string exe = find_project_exe();
    if (exe.empty()) {
        GTEST_SKIP() << "No project executable found (set PROJECT_EXE env to run).";
    }

    std::vector<std::vector<std::string>> argsets = {
        {},
        {"0"},
        {"-1"},
        {"10000000000"},
        {""}
    };

    for (size_t i = 0; i < argsets.size(); ++i) {
        std::ostringstream oss;
        oss << '"' << exe << '"';
        for (auto &a : argsets[i]) {
            oss << ' ' << a;
        }
        std::string cmd = oss.str();
        int rc = run_cmd(cmd);
        EXPECT_EQ(rc, 0) << "Executable failed for argset index=" << i << " cmd=" << cmd;
    }
}

// allow running as standalone main when linked into test runner
int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

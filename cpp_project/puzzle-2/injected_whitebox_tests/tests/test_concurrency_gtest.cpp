// Concurrency-oriented test using the Python concurrency harness when available.
// The harness prints a SUMMARY_JSON object; the test verifies the ALL_DONE array
// contains expected task indices.

#include <gtest/gtest.h>
#include <cstdlib>
#include <string>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <regex>

static std::string find_python_harness() {
    const char* env = std::getenv("PY_CONCURRENCY_HARNESS");
    if (env && *env) return std::string(env);
    std::filesystem::path p = std::filesystem::current_path();
    for (int depth = 0; depth < 3; ++depth) {
        auto cand = p / "tools" / "concurrency_harness.py";
        if (std::filesystem::exists(cand)) return cand.string();
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

TEST(Concurrency, AllTasksComplete) {
    std::string harness = find_python_harness();
    if (harness.empty()) GTEST_SKIP() << "No concurrency harness found (set PY_CONCURRENCY_HARNESS if needed).";

    // Run harness and capture output to temporary file
    std::filesystem::path out = std::filesystem::current_path() / "concurrency_output.txt";
    std::ostringstream cmd;
    // Prefer explicit PYTHON environment variable if set, otherwise fall back to `py -3` on Windows
    const char* pyenv = std::getenv("PYTHON");
    if (pyenv && *pyenv) {
        cmd << '"' << pyenv << '"' << " \"" << harness << "\" --tasks 3 --stagger 0.02 > \"" << out.string() << "\" 2>&1";
    } else {
        cmd << "py -3 \"" << harness << "\" --tasks 3 --stagger 0.02 > \"" << out.string() << "\" 2>&1";
    }

    int rc = run_cmd(cmd.str());
    EXPECT_EQ(rc, 0) << "Concurrency harness failed to run; rc=" << rc;

    // Read output and search for SUMMARY_JSON
    std::string txt;
    try {
        std::ifstream ifs(out);
        std::ostringstream ss;
        ss << ifs.rdbuf();
        txt = ss.str();
    } catch (...) {
        FAIL() << "Failed to read harness output file";
    }

    std::smatch m;
    std::regex re(R"(SUMMARY_JSON:\s*(\{.*\}))", std::regex::ECMAScript | std::regex::icase);
    if (!std::regex_search(txt, m, re) || m.size() < 2) {
        FAIL() << "SUMMARY_JSON not found in harness output";
    }

    std::string json = m[1].str();
    // Look for "ALL_DONE": [0, 1, 2]
    if (json.find("\"ALL_DONE\": [0, 1, 2]") == std::string::npos && json.find("\"ALL_DONE\": [0,1,2]") == std::string::npos) {
        FAIL() << "ALL_DONE array did not contain expected indices; json=" << json;
    }
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

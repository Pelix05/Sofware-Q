# CMake generated Testfile for 
# Source directory: D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests
# Build directory: D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
include("D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/build/test_example[1]_include.cmake")
add_test(gtest_equiv_args "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/build/test_equiv_args.exe")
set_tests_properties(gtest_equiv_args PROPERTIES  _BACKTRACE_TRIPLES "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;71;add_test;D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;0;")
add_test(gtest_boundary "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/build/test_boundary.exe")
set_tests_properties(gtest_boundary PROPERTIES  _BACKTRACE_TRIPLES "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;77;add_test;D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;0;")
add_test(gtest_concurrency "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/build/test_concurrency_gtest.exe")
set_tests_properties(gtest_concurrency PROPERTIES  _BACKTRACE_TRIPLES "D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;83;add_test;D:/semester5/quality/ai-agent-project/cpp_project/puzzle-2/injected_whitebox_tests/CMakeLists.txt;0;")
subdirs("_deps/googletest-build")

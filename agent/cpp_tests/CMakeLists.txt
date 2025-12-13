cmake_minimum_required(VERSION 3.14)
project(agent_cpp_tests LANGUAGES CXX)

# Require C++17 for tests and FetchContent-provided GoogleTest
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Enable testing
include(CTest)
enable_testing()

# Option to enable sanitizers (AddressSanitizer / UBSan) for Linux/macOS builds
option(USE_SANITIZERS "Build tests with sanitizers (ASAN/UBSAN)" OFF)

# Fetch GoogleTest
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/heads/main.zip
)
# For Windows: prevent overriding the parent project's compiler/linker settings
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

if(USE_SANITIZERS)
  if(NOT MSVC)
    message(STATUS "Building tests with AddressSanitizer/UndefinedBehaviorSanitizer")
    # Add sanitizer flags for compile and link
    set(SAN_FLAGS "-fsanitize=address,undefined -fno-omit-frame-pointer -g")
    set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${SAN_FLAGS}")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${SAN_FLAGS}")
    set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${SAN_FLAGS}")
  else()
    message(WARNING "Sanitizers (ASAN/UBSAN) are not supported with MSVC in this configuration")
  endif()
endif()

# Optional harness: build an executable that exercises project APIs if Qt Widgets are available
find_package(Qt6 COMPONENTS Widgets Core Gui QUIET)
if(Qt6_FOUND)
  message(STATUS "Qt6 found: building diagram_harness")
  add_executable(diagram_harness harness/diagram_harness.cpp)
  target_compile_features(diagram_harness PRIVATE cxx_std_17)
  target_include_directories(diagram_harness PRIVATE "${PROJECT_SRC_ROOT}")
  target_link_libraries(diagram_harness PRIVATE Qt6::Widgets)
else()
  message(STATUS "Qt6 not found: skipping diagram_harness")
endif()

add_executable(test_example tests/test_example.cpp)
target_compile_features(test_example PRIVATE cxx_std_17)

target_link_libraries(test_example PRIVATE GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(test_example)

# Additional GoogleTest-based white-box test targets added by agent
if(TARGET GTest::gtest_main)
  # Equivalence argument runner
  add_executable(test_equiv_args tests/test_equiv_args.cpp)
  target_compile_features(test_equiv_args PRIVATE cxx_std_17)
  target_link_libraries(test_equiv_args PRIVATE GTest::gtest_main)
  add_test(NAME gtest_equiv_args COMMAND $<TARGET_FILE:test_equiv_args>)

  # Boundary tests
  add_executable(test_boundary tests/test_boundary.cpp)
  target_compile_features(test_boundary PRIVATE cxx_std_17)
  target_link_libraries(test_boundary PRIVATE GTest::gtest_main)
  add_test(NAME gtest_boundary COMMAND $<TARGET_FILE:test_boundary>)

  # Concurrency harness-based test
  add_executable(test_concurrency_gtest tests/test_concurrency_gtest.cpp)
  target_compile_features(test_concurrency_gtest PRIVATE cxx_std_17)
  target_link_libraries(test_concurrency_gtest PRIVATE GTest::gtest_main)
  add_test(NAME gtest_concurrency COMMAND $<TARGET_FILE:test_concurrency_gtest>)
endif()
# Auto-generate a header-compile test that includes headers from the uploaded project
# When this scaffold is injected into a workspace the uploaded project is expected
# at ../cpp_project relative to this CMakeLists. If headers exist, we generate a
# small test source that includes them so the CI can detect compile-time issues
# in project headers (best-effort).
set(PROJECT_SRC_ROOT "${CMAKE_SOURCE_DIR}/../cpp_project")
if(EXISTS ${PROJECT_SRC_ROOT})
  file(GLOB_RECURSE PROJECT_HEADERS
       "${PROJECT_SRC_ROOT}/*.h"
       "${PROJECT_SRC_ROOT}/*.hpp"
  )
  if(PROJECT_HEADERS)
    message(STATUS "Found ${PROJECT_SRC_ROOT} headers: generating header-compile test")
    set(GEN_TEST_SRC "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_project_headers.cpp")
    file(WRITE ${GEN_TEST_SRC} "#include <gtest/gtest.h>\n\n// Auto-generated header-compile test\n\n")
    foreach(H IN LISTS PROJECT_HEADERS)
      # Use absolute path includes to avoid depending on relative include layout
      file(APPEND ${GEN_TEST_SRC} "#include \"${H}\"\n")
    endforeach()
    file(APPEND ${GEN_TEST_SRC} "\nTEST(ProjectHeadersCompile, AllHeaders) { SUCCEED(); }\n")

    add_executable(test_project_headers ${GEN_TEST_SRC})
    target_compile_features(test_project_headers PRIVATE cxx_std_17)
    target_include_directories(test_project_headers PRIVATE "${PROJECT_SRC_ROOT}")
    target_link_libraries(test_project_headers PRIVATE GTest::gtest_main)
    include(GoogleTest)
    gtest_discover_tests(test_project_headers)
  endif()
endif()

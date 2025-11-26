cmake_minimum_required(VERSION 3.14)
project(agent_cpp_tests LANGUAGES CXX)

# Enable testing
include(CTest)

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

add_executable(test_example tests/test_example.cpp)
target_compile_features(test_example PRIVATE cxx_std_17)

target_link_libraries(test_example PRIVATE GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(test_example)

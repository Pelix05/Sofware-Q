cmake_minimum_required(VERSION 3.14)
project(agent_cpp_tests LANGUAGES CXX)

set(CMAKE_AUTOMOC ON)

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

# 仅对 gtest/gmock 目标放宽 MinGW 的属性（避免影响你的被测代码）
if(MINGW)
  foreach(t IN ITEMS gtest gtest_main gmock gmock_main)
    if(TARGET ${t})
      target_compile_definitions(${t} PRIVATE
        GTEST_ATTRIBUTE_NODISCARD_=
        GTEST_API_=
      )
      target_compile_options(${t} PRIVATE -Wno-attributes -fpermissive)
    endif()
  endforeach()
endif()


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

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets Test Svg)

add_executable(test_example 
  tests/test_deletecommand.cpp
  tests/test_example.cpp
  tests/test_diagramitem.cpp
  tests/test_diagrampath.cpp
  tests/test_arrow.cpp
  tests/test_diagramtextitem.cpp
  tests/test_diagramscene.cpp
  tests/test_mainwindow.cpp
  tests/test_findreplacedialog.cpp
  tests/test_diagramitemgroup.cpp
  tests/test_snapshotcommand.cpp
  tests/test_mygraphicview.cpp
)
target_compile_features(test_example PRIVATE cxx_std_17)


target_link_libraries(test_example PRIVATE
  Qt6::Core Qt6::Gui Qt6::Widgets Qt6::Test Qt6::Svg
  GTest::gtest GTest::gmock
)

if(MINGW)
  target_compile_definitions(test_example PRIVATE
    GTEST_ATTRIBUTE_NODISCARD_=
    GTEST_API_=
  )
  target_compile_options(test_example PRIVATE -Wno-attributes)
endif()

if(WIN32 AND TARGET Qt6::Core)
  add_custom_command(TARGET test_example POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
      $<TARGET_FILE:Qt6::Core>
      $<TARGET_FILE:Qt6::Gui>
      $<TARGET_FILE:Qt6::Widgets>
      $<TARGET_FILE:Qt6::Test>
      $<TARGET_FILE:Qt6::Svg>
      $<TARGET_FILE_DIR:test_example>
    COMMAND ${CMAKE_COMMAND} -E make_directory
      $<TARGET_FILE_DIR:test_example>/platforms
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
      $<TARGET_FILE:Qt6::QWindowsIntegrationPlugin>
      $<TARGET_FILE_DIR:test_example>/platforms/
  )
endif()

if(DEFINED ENV{CPP_SOURCE_DIR})
  set(CPP_PROJECT_DIR "$ENV{CPP_SOURCE_DIR}")
  message(STATUS "Using source from CPP_SOURCE_DIR: ${CPP_PROJECT_DIR}")
elseif(DEFINED CPP_SOURCE_DIR)
  set(CPP_PROJECT_DIR "${CPP_SOURCE_DIR}")
  message(STATUS "Using source from command line: ${CPP_PROJECT_DIR}")
else()
  message(FATAL_ERROR 
    "CPP_SOURCE_DIR not set!\n"
    "FlaskApp must set environment variable CPP_SOURCE_DIR to the uploaded source directory.\n"
    "Example: set CPP_SOURCE_DIR=D:\\workspaces\\123\\cpp_project\\diagramscene_ultima"
  )
endif()

# 验证路径有效性
if(NOT EXISTS "${CPP_PROJECT_DIR}/diagramitem.cpp")
  message(FATAL_ERROR 
    "Invalid CPP_PROJECT_DIR: ${CPP_PROJECT_DIR}\n"
    "Cannot find diagramitem.cpp in this directory.\n"
    "Please check FlaskApp's source detection logic."
  )
endif()

message(STATUS "Source files will be included from: ${CPP_PROJECT_DIR}")
target_include_directories(test_example PRIVATE "${CPP_PROJECT_DIR}")
target_sources(test_example PRIVATE
  ${CPP_PROJECT_DIR}/deletecommand.cpp
  ${CPP_PROJECT_DIR}/diagramitem.cpp
  ${CPP_PROJECT_DIR}/arrow.cpp
  ${CPP_PROJECT_DIR}/diagramtextitem.cpp
  ${CPP_PROJECT_DIR}/diagrampath.cpp
  ${CPP_PROJECT_DIR}/diagramscene.cpp
  ${CPP_PROJECT_DIR}/mainwindow.cpp
  ${CPP_PROJECT_DIR}/findreplacedialog.cpp
  ${CPP_PROJECT_DIR}/diagramitemgroup.cpp
  ${CPP_PROJECT_DIR}/snapshotcommand.cpp
  tests/gtest_main_qt.cpp
  #tests/test_global.cpp
)

include(GoogleTest)
gtest_discover_tests(test_example)

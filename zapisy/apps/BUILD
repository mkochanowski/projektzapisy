load("@io_bazel_rules_python//python:python.bzl", "py_binary", "py_library", "py_test")
load("@py_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "feeds",
    srcs = ["feeds.py"],
    deps = [
        "//zapisy/zapisy/apps/news:project",
        requirement("django"),
    ],
)
load("@io_bazel_rules_python//python:python.bzl", "py_binary", "py_library", "py_test")
load("@py_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "decorators",
    srcs = ["decorators.py"],
    deps = [
        "//zapisy/zapisy/apps/users/models:project",
        requirement("django"),
    ],
)

py_library(
    name = "exceptions",
    srcs = ["exceptions.py"],
    deps = [
        "//zapisy/zapisy/apps/users/models:project",
        requirement("django"),
    ],
)

py_library(
    name = "api",
    srcs = ["api.py"],
    deps = [
        "//zapisy/zapisy/apps/users/models:project",
        requirement("django"),
        requirement("rest_framework"),
    ],
)

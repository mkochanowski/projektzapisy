load("@io_bazel_rules_python//python:python.bzl", "py_binary", "py_library", "py_test")
load("@py_deps//:requirements.bzl", "requirement")

py_binary(
    name = "manage",
    srcs = ["manage.py"],
    deps = [
        "//zapisy/zapisy:settings",
        requirement("django"),
    ],
)

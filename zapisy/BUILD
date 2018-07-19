load("@io_bazel_rules_python//python:python.bzl", "py_binary", "py_library", "py_test")
load("@py_deps//:requirements.bzl", "all_requirements", "requirement")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "manage",
    srcs = ["manage.py"],
    deps = [
        "//zapisy/zapisy:settings",
        requirement("django"),
    ],
)

py_binary(
    name = "run",
    srcs = ["run.py"],
    data = [
        ":project",
    ],
    deps = [
        requirement("click"),
        requirement("Fabric3"),
    ],
)

# This is a placeholder target. It needs to exist until all the targets are
# defined correctly.
py_library(
    name = "project",
    srcs = glob(["**/*.py"]),
    data = glob([
        "**/*.html",
        "**/*.js",
        "**/*.ts",
        "**/*.json",
    ]),
    deps = [
    ] + all_requirements,
)

load("@py_deps//:requirements.bzl", "all_requirements", "requirement")

package(default_visibility = ["//visibility:public"])

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
        "//zapisy/zapisy/apps/user:project",
    ] + all_requirements,
)
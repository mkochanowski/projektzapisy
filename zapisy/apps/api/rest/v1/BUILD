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
        "//zapisy/apps/enrollment:project",
        "//zapisy/apps/offer/desiderata:project",
        "//zapisy/apps/schedule:project",
        "//zapisy/apps/users:project",
    ] + all_requirements,
)
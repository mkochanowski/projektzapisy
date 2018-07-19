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
        "//zapisy/apps/enrollment/records:project",
        "//zapisy/apps/schedule:project",
        "//zapisy/apps/offer/proposal:project",
        "//zapisy/apps/users:project",
        "//zapisy/apps/notifications:project",
        "//zapisy/zapisy:common",
    ] + all_requirements,
)

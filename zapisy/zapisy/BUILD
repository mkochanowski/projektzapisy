load("@py_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "settings",
    srcs = ["settings.py"],
    deps = [
        "//zapisy:project",
        requirement("django-environ"),
    ],
)

py_library(
    name = "common",
    srcs = ["common.py"],
)

py_library(
    name = "urls",
    srcs = ["urls.py"],
    deps = [
        "//zapisy/apps:feeds",
        "//zapisy/apps/api/rest/v1:project",
        "//zapisy/apps/email_change:project",
        "//zapisy/apps/enrollment/courses:project",
        "//zapisy/apps/enrollment/records:project",
        "//zapisy/apps/grade:project",
        "//zapisy/apps/help:project",
        "//zapisy/apps/news:project",
        "//zapisy/apps/notifications:project",
        "//zapisy/apps/offer/desiderata:project",
        "//zapisy/apps/offer/preferences:project",
        "//zapisy/apps/offer/proposal:project",
        "//zapisy/apps/offer/vote:project",
        "//zapisy/apps/rest/v1:project",
        "//zapisy/apps/schedule:project",
        "//zapisy/apps/statistics:project",
        "//zapisy/apps/users:project",
        requirement("django"),
        requirement("django_cas_ng"),
    ],
)

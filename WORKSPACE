## Different tools depend on the Go rules.
http_archive(
    name = "io_bazel_rules_go",
    sha256 = "c1f52b8789218bb1542ed362c4f7de7052abcf254d865d96fb7ba6d44bc15ee3",
    url = "https://github.com/bazelbuild/rules_go/releases/download/0.12.0/rules_go-0.12.0.tar.gz",
)

## The rules below download and set-up the Node/TS toolchain.

# TypeScript rules depend on running Node.js.
http_archive(
    name = "build_bazel_rules_nodejs",
    sha256 = "634206524d90dc03c52392fa3f19a16637d2bcf154910436fe1d669a0d9d7b9c",
    strip_prefix = "rules_nodejs-0.10.1",
    url = "https://github.com/bazelbuild/rules_nodejs/archive/0.10.1.zip",
)

# ts_web_test depends on the web testing rules to provision browsers.
http_archive(
    name = "io_bazel_rules_webtesting",
    sha256 = "cecc12f07e95740750a40d38e8b14b76fefa1551bef9332cb432d564d693723c",
    strip_prefix = "rules_webtesting-0.2.0",
    url = "https://github.com/bazelbuild/rules_webtesting/archive/v0.2.0.zip",
)

# Include @bazel/typescript in package.json#devDependencies
local_repository(
    name = "build_bazel_rules_typescript",
    path = "zapisy/node_modules/@bazel/typescript",
)

## The rules below download and set-up buildifier (a BUILD file formatter).

http_archive(
    name = "com_github_bazelbuild_buildtools",
    sha256 = "43c2df6ce1bd01b4d8173efe0795b05b19240f24ea33fde3694096f7b6043f8a",
    strip_prefix = "buildtools-4fe6acf537e980ff6878a51e5894605be221224c",
    url = "https://github.com/bazelbuild/buildtools/archive/4fe6acf537e980ff6878a51e5894605be221224c.zip",
)

load("@io_bazel_rules_go//go:def.bzl", "go_register_toolchains", "go_rules_dependencies")

go_rules_dependencies()

go_register_toolchains()

load("@build_bazel_rules_nodejs//:defs.bzl", "node_repositories")

# Point to the package.json file so Bazel can run the package manager for you.
node_repositories(package_json = ["//zapisy:package.json"])

load("@io_bazel_rules_webtesting//web:repositories.bzl", "browser_repositories", "web_test_repositories")

web_test_repositories()

browser_repositories(
    chromium = True,
    firefox = True,
)

load("@build_bazel_rules_typescript//:defs.bzl", "ts_setup_workspace")

ts_setup_workspace()

load("@com_github_bazelbuild_buildtools//buildifier:deps.bzl", "buildifier_dependencies")

buildifier_dependencies()

## The rules to define Python targets and depend on PIP libraries.

http_archive(
    name = "io_bazel_rules_python",
    sha256 = "40499c0a9d55f0c5deb245ed24733da805f05aaf6085cb39027ba486faf1d2e1",
    strip_prefix = "rules_python-8b5d0683a7d878b28fffe464779c8a53659fc645",
    url = "https://github.com/bazelbuild/rules_python/archive/8b5d0683a7d878b28fffe464779c8a53659fc645.zip",
)

# Only needed for PIP support:
load("@io_bazel_rules_python//python:pip.bzl", "pip_import", "pip_repositories")

pip_repositories()

# This rule translates the specified requirements.txt into
# @my_deps//:requirements.bzl, which itself exposes a pip_install method.
pip_import(
    name = "py_deps",
    requirements = "//zapisy:requirements.development.txt",
)

# Load the pip_install symbol for my_deps, and create the dependencies'
# repositories.
load("@py_deps//:requirements.bzl", "pip_install")

pip_install()

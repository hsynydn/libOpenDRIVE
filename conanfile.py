from conan.tools.cmake import CMake, CMakeToolchain
from conan import ConanFile
from conan.tools.files import copy
from io import StringIO


class OpenDriveConan(ConanFile):
    name = "OpenDrive"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def set_version(self):

        version_io = StringIO()
        self.run("git tag -l --sort=v:refname | tail -n 1", output=version_io)

        version_tag = version_io.getvalue()
        version_tag_split = version_tag[1:].split('.')
        version_major = version_tag_split[0]
        version_minor = version_tag_split[1]
        version_patch = version_tag_split[2]

        tag_io = StringIO()
        self.run(f"git rev-list --count `git rev-list -n 1 {version_tag}`", output=tag_io)

        last_commit_io = StringIO()
        self.run("git rev-list --count `git log --pretty=format:%h -n 1`", output=last_commit_io)

        version_tweak = int(last_commit_io.getvalue()) - int(tag_io.getvalue())

        with open("version.cmake", mode="w") as file:
            file.write(f"set(VERSION_MAJOR {version_major})\n")
            file.write(f"set(VERSION_MINOR {version_minor})\n")
            file.write(f"set(VERSION_PATCH {version_patch})\n")
            file.write(f"set(VERSION_TWEAK {version_tweak})\n")

        self.version = version_tag

    def export_sources(self):
        self.copy("*", dst="", keep_path=True)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def package(self):
        self.copy("*.so", dst="lib", keep_path=False, symlinks=True)
        self.copy("include/*", dst="", keep_path=True, symlinks=True)
        self.copy("thirdparty/pugixml/*", dst="include/pugixml", keep_path=False, symlinks=True)
        self.copy("thirdparty/earcut/*", dst="include/earcut", keep_path=False, symlinks=True)

    def package_info(self):
        self.cpp_info.libs = ["OpenDrive"]
        self.cpp_info.set_property("cmake_file_name", "OpenDrive")
        self.cpp_info.set_property("cmake_target_name", "OpenDrive::OpenDrive")



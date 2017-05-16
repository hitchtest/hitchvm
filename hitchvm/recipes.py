class Recipe(object):
    def run(self, cmd):
        raise NotImplementedError("Inherit from Recipe")


class Brew(Recipe):
    def run(self, cmd):
        cmd(
            "echo -ne '\n' | ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\"",
        ).run()
        cmd("brew update").run()
        cmd("brew upgrade --all").run()


class AptGet(Recipe):
    def __init__(self, *packages):
        for package in packages:
            assert isinstance(package, str), "package names must be strings"
        self._packages = packages

    def run(self, cmd):
        for package in self._packages:
            cmd("apt-get install {0} -y".format(package))

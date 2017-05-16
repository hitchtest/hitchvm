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

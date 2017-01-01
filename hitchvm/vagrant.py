from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from commandlib import Command
from hitchvm import utils
from path import Path


TEMPLATE_DIR = Path(__file__).abspath().dirname().joinpath("templates")


STANDARD_BOXES = {
    "ubuntu-trusty-64": {
        "url": (
            "https://cloud-images.ubuntu.com/vagrant/trusty/current/"
            "trusty-server-cloudimg-amd64-vagrant-disk1.box",
        ),
        "template": "linux.jinja2",
    }
}


class VagrantBox(object):
    def __init__(self, location=None):
        self._location = location

    @property
    def template(self):
        return "linux.jinja2"

    def retrieve(self):
        pass

    @property
    def location(self):
        if self._location is None:
            raise Exception(
                "VagrantBox has no location yet. Perhaps .retrieve() was not run."
            )
        return self._location


class StandardBox(VagrantBox):
    def __init__(self, download_folder, name):
        self._download_folder = Path(download_folder).abspath()
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def download_to(self):
        return Path(self._download_folder).joinpath("{0}.box".format(self._name))

    @property
    def url(self):
        return STANDARD_BOXES[self._name]['url']

    @property
    def template(self):
        return STANDARD_BOXES[self._name]['template']

    def retrieve(self):
        if self.download_to.exists():
            self._location = self.download_to.abspath()
        else:
            utils.download_file(self.download_to, self.url)
            self._location = self.download_to.abspath()


class Vagrant(object):
    def __init__(self, path, machine):
        self._path = Path(path).abspath()
        self._machine = machine
        self._id = utils.random_id(6)

    @property
    def vagrant_path(self):
        return Path(self._path).joinpath(self.machine_name)

    @property
    def machine_name(self):
        return "{0}-{1}".format(self._machine.name, self._id)

    @property
    def vagrant_file(self):
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATE_DIR)
        return env.get_template(self._machine.template).render(
            machine_name=self.machine_name,
            underscored_name=self.machine_name.replace("-", "_"),
            location=self._machine.location,
        )

    def up(self):
        """
        Start and return live box.
        """
        self._machine.retrieve()
        if self.vagrant_path.exists():
            self.vagrant_path.rmtree()
        self.vagrant_path.mkdir()
        self.vagrant_path.joinpath("Vagrantfile").write_text(self.vagrant_file)
        Command("vagrant")("up").in_dir(self.vagrant_path).run()
        return RunningVagrant(self)


class RunningVagrant(object):
    def __init__(self, vagrant_template):
        self._vagrant_template = vagrant_template

    @property
    def cmd(self):
        """
        Command to run within the vagrant box.
        """
        return Command("vagrant", "ssh", "-c").in_dir(self._vagrant_template.vagrant_path)

    def destroy(self):
        """
        Eliminate the virtual machine.
        """
        Command("vagrant")("destroy", "-f").in_dir(self._vagrant_template.vagrant_path).run()
        Path(self._vagrant_template.vagrant_path).rmtree(ignore_errors=True)

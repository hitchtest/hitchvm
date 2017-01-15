from jinja2.environment import Environment
from jinja2 import FileSystemLoader
from commandlib import Command
from hitchvm import utils
from path import Path
import copy


TEMPLATE_DIR = Path(__file__).abspath().dirname().joinpath("templates")


STANDARD_BOXES = {
    "ubuntu-trusty-64": {
        "url": "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box",
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
        self._sync_from_location = None
        self._sync_to_location = None
        self._cmd = Command("vagrant").in_dir(self.vagrant_path)

    @property
    def vagrant_path(self):
        return Path(self._path).joinpath(self.machine_name)

    @property
    def machine_name(self):
        return self._machine.name

    @property
    def vagrant_file(self):
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATE_DIR)
        return env.get_template(self._machine.template).render(
            machine_name=self.machine_name,
            underscored_name=self.machine_name.replace("-", "_"),
            location=self._machine.location,
            sync_from_location=self._sync_from_location,
            sync_to_location=self._sync_to_location,
        )

    def synced_with(self, from_location, to_location):
        new_vagrant = copy.copy(self)
        new_vagrant._sync_from_location = Path(from_location).abspath()
        new_vagrant._sync_to_location = to_location
        assert new_vagrant._sync_from_location.exists()
        return new_vagrant

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

    @property
    def cmd(self):
        """
        Base command to run bash command within the vagrant box.
        """
        return self._cmd("ssh", "-c")

    def halt(self):
        """
        Stop the virtual machine, but do not destroy.
        """
        self._cmd("halt").run()

    def take_snapshot(self, name):
        """
        Save a named snapshot of the virtual machine.
        """
        self._cmd("snapshot", "save", name).run()

    def snapshot_exists(self, name):
        """
        Return True if snapshot with name exists.
        """
        return name in self._cmd("snapshot", "list").output().strip().split('\n')

    def restore_snapshot(self, name):
        """
        Restore a snapshot of the virtual machine.
        """
        self._cmd("snapshot", "restore", name, "--no-provision").run()

    def delete_snapshot(self, name):
        """
        Delete a snapshot of the virtual machine.
        """
        self._cmd("snapshot", "delete", name).run()

    def sync(self):
        """
        Resync files that the vm template was configured to sync with.
        """
        self._cmd("rsync").run()

    def destroy(self):
        """
        Eliminate the virtual machine and template files.
        """
        self._cmd("destroy", "-f").run()
        Path(self.vagrant_path).rmtree(ignore_errors=True)

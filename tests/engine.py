from subprocess import check_call, call, PIPE, CalledProcessError
from os import path, system, chdir
from commandlib import run, CommandError
from simex import DefaultSimex
import hitchpython
import hitchserve
import hitchtest
import hitchcli
import signal


class ExecutionEngine(hitchtest.ExecutionEngine):
    """Python engine for running tests."""

    def set_up(self):
        """Set up your applications and the test environment."""
        self.path.project = self.path.engine.parent

        if self.path.state.exists():
            self.path.state.rmtree(ignore_errors=True)
        self.path.state.mkdir()

        for filename, text in self.preconditions.get("files", {}).items():
            filepath = self.path.state.joinpath(filename)
            if not filepath.dirname().exists():
                filepath.dirname().makedirs()
            filepath.write_text(text)

        for filename, linkto in self.preconditions.get("symlinks", {}).items():
            filepath = self.path.state.joinpath(filename)
            linktopath = self.path.state.joinpath(linkto)
            linktopath.symlink(filepath)

        self.python_package = hitchpython.PythonPackage(
            self.preconditions.get('python_version', '3.5.0')
        )
        self.python_package.build()

        self.pip = self.python_package.cmd.pip
        self.python = self.python_package.cmd.python

        # Install debugging packages
        with hitchtest.monitor([self.path.engine.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                run(self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.engine))

        # Uninstall and reinstall
        run(self.pip("uninstall", "pathquery", "-y").ignore_errors())
        run(self.pip("install", ".").in_dir(self.path.project))

        run(self.pip("install", "path.py=={0}".format(self.preconditions['pathpy_version'])))

        self.services = hitchserve.ServiceBundle(
            str(self.path.project),
            startup_timeout=8.0,
            shutdown_timeout=1.0
        )

        self.services['IPython'] = hitchpython.IPythonKernelService(self.python_package)

        self.services.startup(interactive=False)
        self.ipython_kernel_filename = self.services['IPython'].wait_and_get_ipykernel_filename()
        self.ipython_step_library = hitchpython.IPythonStepLibrary()
        self.ipython_step_library.startup_connection(self.ipython_kernel_filename)

        self.run_command = self.ipython_step_library.run
        self.assert_true = self.ipython_step_library.assert_true
        self.assert_exception = self.ipython_step_library.assert_exception
        self.shutdown_connection = self.ipython_step_library.shutdown_connection
        self.run_command("import os")
        self.run_command("os.chdir('{}')".format(self.path.state))

        for line in self.settings['always run']:
            self.run_command(line)

    def on_failure(self):
        if hasattr(self, 'services'):
            if self.settings.get("pause_on_failure", True):
                if self.preconditions.get("launch_shell", True):
                    self.services.log(message=self.stacktrace.to_template())
                    self.shell()

    def shell(self):
        if hasattr(self, 'services'):
            #self.run_command("from hitchtrigger import *")
            self.services.start_interactive_mode()
            import sys
            import time ; time.sleep(0.5)
            if path.exists(path.join(
                path.expanduser("~"), ".ipython/profile_default/security/",
                self.ipython_kernel_filename)
            ):
                call([
                        sys.executable, "-m", "IPython", "console",
                        "--existing",
                        path.join(
                            path.expanduser("~"),
                            ".ipython/profile_default/security/",
                            self.ipython_kernel_filename
                        )
                    ])
            else:
                call([
                    sys.executable, "-m", "IPython", "console",
                    "--existing", self.ipython_kernel_filename
                ])
            self.services.stop_interactive_mode()

    def assert_file_contains(self, filename, contents):
        assert self.path.state.joinpath(filename).bytes().decode('utf8').strip() == contents.strip()

    def touch(self, filename):
        with open(self.path.state.joinpath(filename), 'a') as handle:
            handle.write("Change something!")

    def should_have_run(self, which):
        if not self.path.state.joinpath("should{0}.txt".format(which)).exists():
            raise RuntimeError("{0} was not run".format(which))

    def output_is(self, expected_contents):
        output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8').strip()
        regex = DefaultSimex(
            open_delimeter="(((",
            close_delimeter=")))"
        ).compile(expected_contents.strip())
        if regex.match(output_contents) is None:
            raise RuntimeError("Expected output:\n{0}\n\nActual output:\n{1}".format(
                expected_contents,
                output_contents,
            ))
        self.path.state.joinpath("output.txt").remove()

    def output_contains(self, expected_contents, but_not=None):
        output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8').strip()
        for expected_item in expected_contents:
            found = False
            for output_item in output_contents.split('\n'):
                if output_item.strip() == str(self.path.state.joinpath(expected_item).abspath()).strip():
                    found = True
            if not found:
                raise RuntimeError("Expected:\n{0}\n\nNot found in:\n{1}".format(
                    str(self.path.state.join(expected_item)).strip(),
                    output_contents,
                ))

        if but_not is not None:
            for unexpected_item in but_not:
                found = False
                for output_item in output_contents.split('\n'):
                    if output_item.strip() == str(self.path.state.joinpath(unexpected_item).abspath()).strip():
                        found = True
                if found:
                    raise RuntimeError("Expected NOT to find:\n{0}\n\nBut found in:\n{1}".format(
                        str(self.path.state.joinpath(unexpected_item).strip()),
                        output_contents,
                    ))

    def make_directory(self, directory):
        self.path.state.joinpath(directory).mkdir()

    def sleep(self, howlong):
        import time
        time.sleep(float(howlong))

    def sleep_for_over_a_second(self):
        self.sleep(1.5)

    def flake8(self, directory, args=None):
        # Silently install flake8
        self.services.start_interactive_mode()
        flake8 = self.python_package.cmd.flake8
        try:
            run(flake8(str(self.path.project.joinpath(directory)), *args).in_dir(self.path.project))
        except CommandError:
            raise RuntimeError("flake8 failure")

    def pause(self, message="Pause"):
        if hasattr(self, 'services'):
            self.services.start_interactive_mode()
        self.ipython(message)
        if hasattr(self, 'services'):
            self.services.stop_interactive_mode()


    def tear_down(self):
        try:
            self.shutdown_connection()
        except:
            pass
        if hasattr(self, 'services'):
            self.services.shutdown()

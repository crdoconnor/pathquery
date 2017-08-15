from commandlib import run
import hitchpython
from hitchstory import StoryCollection, StorySchema, BaseEngine, exceptions
from hitchrun import expected
from commandlib import Command
import strictyaml
from strictyaml import MapPattern, Str, Map, Int, Optional, load
from pathquery import pathq
import hitchtest
import hitchdoc
from hitchrun import hitch_maintenance
from commandlib import python
from hitchrun import DIR
from hitchrun.decorators import ignore_ctrlc


from jinja2.environment import Environment
from jinja2 import DictLoader


class Engine(BaseEngine):
    """Python engine for running tests."""
    schema = StorySchema(
        preconditions=Map({
            "setup": Str(),
            "files": MapPattern(Str(), Str()),
            "symlinks": MapPattern(Str(), Str()),
            "python version": Str(),
            "pathpy version": Str(),
            "code": Str(),
        }),
        params=Map({
            "python version": Str(),
            "pathpy version": Str(),
        }),
        about={
            "description": Str(),
            Optional("importance"): Int(),
        },
    )

    def __init__(self, paths, settings):
        self.path = paths
        self.settings = settings

    def set_up(self):
        """Set up your applications and the test environment."""
        self.doc = hitchdoc.Recorder(
            hitchdoc.HitchStory(self),
            self.path.gen.joinpath('storydb.sqlite'),
        )

        self.path.state = self.path.gen.joinpath("state")
        if self.path.gen.joinpath("state").exists():
            self.path.gen.joinpath("state").rmtree(ignore_errors=True)
        self.path.gen.joinpath("state").mkdir()

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
        with hitchtest.monitor([self.path.key.joinpath("debugrequirements.txt")]) as changed:
            if changed:
                run(self.pip("install", "-r", "debugrequirements.txt").in_dir(self.path.key))

        # Uninstall and reinstall
        with hitchtest.monitor(pathq(self.path.project.joinpath("pathquery")).ext("py")) as changed:
            if changed:
                run(self.pip("uninstall", "pathquery", "-y").ignore_errors())
                run(self.pip("install", ".").in_dir(self.path.project))
                run(self.pip("install", "path.py=={0}".format(
                    self.preconditions["pathpy version"]
                )))

    def run_command(self, command):
        self.ipython_step_library.run(command)
        self.doc.step("code", command=command)

    def variable(self, name, value):
        self.path.state.joinpath("{}.yaml".format(name)).write_text(
            value
        )
        self.ipython_step_library.run(
            """{} = Path("{}").bytes().decode("utf8")""".format(
                name, "{}.yaml".format(name)
            )
        )
        self.doc.step("variable", var_name=name, value=value)

    def run_code(self):
        """
        Runs code.
        """
        class UnexpectedException(Exception):
            pass

        error_path = self.path.state.joinpath("error.txt")
        output_path = self.path.state.joinpath("output.txt")
        if output_path.exists():
            output_path.remove()
        runpy = self.path.gen.joinpath("runmypy.py")
        if error_path.exists():
            error_path.remove()
        env = Environment()
        env.loader = DictLoader(
            load(self.path.key.joinpath("codetemplates.yml").bytes().decode('utf8')).data
        )
        runpy.write_text(env.get_template("raises_exception").render(
            setup=self.preconditions['setup'],
            code=self.preconditions['code'],
            variables=self.preconditions.get('variables', None),
            error_path=error_path,
            output_path=output_path,
        ))
        self.python(runpy).in_dir(self.path.state).run()
        if error_path.exists():
            raise UnexpectedException(error_path.bytes().decode('utf8'))

    def output_contains(self, expected_contents, but_not=None):
        try:
            output_contents = self.path.state.joinpath("output.txt").bytes().decode('utf8').strip()
        except FileNotFoundError:
            raise Exception("Output not found")

        for expected_item in expected_contents:
            found = False
            for output_item in output_contents.split('\n'):
                if output_item.strip() == str(
                    self.path.state.joinpath(expected_item).abspath()
                ).strip():
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
                    if output_item.strip() == str(
                        self.path.state.joinpath(unexpected_item).abspath()
                    ).strip():
                        found = True
                if found:
                    raise RuntimeError("Expected NOT to find:\n{0}\n\nBut found in:\n{1}".format(
                        str(self.path.state.joinpath(unexpected_item).strip()),
                        output_contents,
                    ))

    def pause(self, message="Pause"):
        if hasattr(self, 'services'):
            self.services.start_interactive_mode()
        import IPython
        IPython.embed()
        if hasattr(self, 'services'):
            self.services.stop_interactive_mode()

    def on_success(self):
        if self.settings.get("overwrite"):
            self.new_story.save()

    def tear_down(self):
        try:
            self.shutdown_connection()
        except:
            pass
        if hasattr(self, 'services'):
            self.services.shutdown()


@expected(strictyaml.exceptions.YAMLValidationError)
@expected(exceptions.HitchStoryException)
def tdd(*words):
    """
    Run test with words.
    """
    print(
        StoryCollection(
            pathq(DIR.key.joinpath("story")).ext("story"), Engine(DIR, {})
        ).shortcut(*words).play().report()
    )


def regression():
    """
    Run regression testing - lint and then run all tests.
    """
    lint()
    print(
        StoryCollection(
            pathq(DIR.key).ext("story"), Engine(DIR, {})
        ).ordered_by_name().play().report()
    )


def lint():
    """
    Lint all code.
    """
    python("-m", "flake8")(
        DIR.project.joinpath("pathquery"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    python("-m", "flake8")(
        DIR.key.joinpath("key.py"),
        "--max-line-length=100",
        "--exclude=__init__.py",
    ).run()
    print("Lint success!")


def hitch(*args):
    """
    Use 'h hitch --help' to get help on these commands.
    """
    hitch_maintenance(*args)


def deploy(version):
    """
    Deploy to pypi as specified version.
    """
    NAME = "pathquery"
    git = Command("git").in_dir(DIR.project)
    version_file = DIR.project.joinpath("VERSION")
    old_version = version_file.bytes().decode('utf8')
    if version_file.bytes().decode("utf8") != version:
        DIR.project.joinpath("VERSION").write_text(version)
        git("add", "VERSION").run()
        git("commit", "-m", "RELEASE: Version {0} -> {1}".format(
            old_version,
            version
        )).run()
        git("push").run()
        git("tag", "-a", version, "-m", "Version {0}".format(version)).run()
        git("push", "origin", version).run()
    else:
        git("push").run()

    # Set __version__ variable in __init__.py, build sdist and put it back
    initpy = DIR.project.joinpath(NAME, "__init__.py")
    original_initpy_contents = initpy.bytes().decode('utf8')
    initpy.write_text(
        original_initpy_contents.replace("DEVELOPMENT_VERSION", version)
    )
    python("setup.py", "sdist").in_dir(DIR.project).run()
    initpy.write_text(original_initpy_contents)

    # Upload to pypi
    python(
        "-m", "twine", "upload", "dist/{0}-{1}.tar.gz".format(NAME, version)
    ).in_dir(DIR.project).run()


def docgen():
    """
    Generate documentation.
    """
    docpath = DIR.project.joinpath("docs")

    if not docpath.exists():
        docpath.mkdir()

    documentation = hitchdoc.Documentation(
        DIR.gen.joinpath('storydb.sqlite'),
        'doctemplates.yml'
    )

    for story in documentation.stories:
        story.write(
            "rst",
            docpath.joinpath("{0}.rst".format(story.slug))
        )


@ignore_ctrlc
def ipy():
    """
    Run IPython in environment."
    """
    Command(DIR.gen.joinpath("py3.5.0", "bin", "ipython")).run()

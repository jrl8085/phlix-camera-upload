#!/usr/bin/env python3
"""Check that the documents still agree with the program.

Run it from the root of the repository:

    python3 scripts/check-docs.py           check, and change nothing
    python3 scripts/check-docs.py --sync    first make the two copies again

It needs Python and nothing else. It prints one line for each thing that is
wrong and ends with status 1, or prints one line and ends with status 0.

Two files hold a copy of another file, so that each works on its own:
install.sh holds docker-compose.yml, and the skill holds the instructions of
SETUP-WITH-AI.md. After a change to docker-compose.yml or to
SETUP-WITH-AI.md, run this script with --sync. It copies the text again.

What it compares:

  * the settings table in README.md with phlix_upload/config.py;
  * the file types in README.md with phlix_upload/storage.py;
  * the settings in docker-compose.yml and in the Unraid template with what
    the program accepts;
  * the Compose text in install.sh and in SETUP-WITH-AI.md with
    docker-compose.yml;
  * the skill with SETUP-WITH-AI.md, and with the rules for a skill;
  * the two plugin files with each other and with the program's version;
  * every link between the files of this repository;
  * every command, address and program message that a document quotes with
    the program itself, and the limits that the documents name with the
    numbers in the program;
  * the wording rules: the two trademark lines, plain ASCII, and no word
    that the product must not use.

When this check fails after a change to the program, change the documents.
"""

from __future__ import annotations

import inspect
import json
import os
import re
import sys
import xml.etree.ElementTree as ElementTree

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from phlix_upload import DEFAULT_PORT, __version__, config, pairing, storage  # noqa: E402
from phlix_upload import server as server_module  # noqa: E402

IMAGE = "ghcr.io/jrl8085/phlix-camera-upload:1"
PLACEHOLDER = "/CHANGE/THIS/Photos/Camera Uploads"
GUIDE_PLACEHOLDER = "HOST_PATH_OF_UPLOAD_FOLDER"
SKILL_NAME = "phlix-camera-upload-setup"
SKILL = f"skills/{SKILL_NAME}/SKILL.md"
REPOSITORY = "jrl8085/phlix-camera-upload"
TRADEMARK_LINES = [
    "Phlix is an independent application and is not affiliated with, endorsed, or sponsored by Plex, Inc.",
    "Plex, the Plex Play logo, and Plex Media Server are trademarks of Plex GmbH and used under a license.",
]
#: Documents for people. They end with the two trademark lines.
DOCUMENTS = ["README.md", "SETUP-WITH-AI.md", "NETWORKING.md", "SECURITY.md", SKILL]
#: Every file around the program. The wording rules apply to all of them.
PACKAGING = DOCUMENTS + [
    "docker-compose.yml", "install.sh", "Dockerfile", "LICENSE", ".dockerignore", ".gitignore",
    "unraid/phlix-camera-upload.xml", "scripts/smoke-test.sh", "scripts/check-docs.py", "scripts/test-install.sh",
    "scripts/build-skill-zip.sh", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    ".github/workflows/ci.yml", ".github/workflows/release.yml", ".github/dependabot.yml",
]
#: Messages of the program that the documents quote, by the file that says
#: them. When a document holds one of these, that file must still say it.
PROGRAM_TEXT = {
    # the status page
    "phlix_upload/statuspage.py": [
        "Upload folder", "Ready", "Free space", "Plex Media Server", "Paired devices", "Files stored",
        "Running, version", "The helper cannot write here", "too little: uploads are paused",
        "lets this helper in without signing in",
    ],
    # the doctor command, and the log at start
    "phlix_upload/__main__.py": [
        "Nothing needs fixing.", "The helper is running on port", "can be written to.",
        "free on the upload disk.", "Plex Media Server found: its owner can pair from Phlix without a code.",
        "files stored", "Pairing code: run `python -m phlix_upload code` the same way to see it.",
        "Nothing is mounted at", "Running as root, so uploaded files will belong to root", "Running as user",
        "Pairing code:", "Phlix Camera Upload cannot start:",
        "The owner of the Plex server can pair from Phlix without the code.",
        "inside a container this is the container's own address",
        "The helper runs as root",
    ],
    "phlix_upload/server.py": ["Wrong pairing code from", "was already paired and has paired again from"],
    "phlix_upload/tlsutil.py": ["Made a new TLS certificate in"],
    # the last one is Plex's own name for a setting, as the program's comments give it
    "phlix_upload/plex.py": ["Found Plex Media Server",
                             "List of IP addresses and networks that are allowed without auth"],
}
#: Lines of docker-compose.yml that the documents tell the reader to find,
#: change or remove. When a document names one, the file must still hold it.
COMPOSE_LINES = [
    "ports:", '- "7459:7459"', "extra_hosts:", '- "host.docker.internal:host-gateway"',
    "restart: unless-stopped", "./config:/config", "create_host_path: false",
]
#: Messages that the documents used to quote and the program no longer says.
RETIRED_TEXT = ["Files received", "files received"]

problems: list[str] = []


def wrong(text: str) -> None:
    problems.append(text)


def read(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def prose(markdown: str) -> str:
    """A document without its code: no fenced blocks, no inline code."""
    without_blocks = re.sub(r"```.*?```", " ", markdown, flags=re.S)
    return re.sub(r"`[^`\n]*`", " ", without_blocks)


def without_comments(yaml_text: str) -> list[str]:
    return [line.rstrip() for line in yaml_text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def flat(source: str) -> str:
    """Program text on one line, so that a message split over lines is found."""
    joined = re.sub(r'"\s*\n\s*f?"', "", source)
    return re.sub(r"\s+", " ", re.sub(r"\n\s*#", " ", joined))


def check_settings_table(readme: str) -> list[str]:
    """README's table lists every setting of config.py, with its default."""
    settings = sorted(set(re.findall(r'get\("([A-Z_]+)"', read("phlix_upload/config.py"))))
    rows = dict(re.findall(r"^\| `([A-Z_]+)` \| (.*?) \| ", readme, re.M))
    for name in settings:
        if name not in rows:
            wrong(f"README.md: the settings table has no row for {name}")
    for name in rows:
        if name not in settings:
            wrong(f"README.md: the settings table has a row for {name}, which the program does not read")
    defaults = config.load({})
    expected = {
        "PORT": str(defaults.port), "BIND": defaults.bind, "UPLOAD_DIR": defaults.upload_dir,
        "CONFIG_DIR": defaults.config_dir, "NAME": defaults.name, "PAIRING": defaults.pairing,
        "PATH_TEMPLATE": defaults.path_template,
        "MIN_FREE_GB": f"{defaults.min_free_bytes / 1024 ** 3:g}",
        "MAX_UPLOAD_GB": f"{defaults.max_upload_bytes / 1024 ** 3:g}",
        "TLS": "on" if defaults.tls else "off", "UMASK": f"{defaults.umask:03o}", "LOG_LEVEL": defaults.log_level,
    }
    for name in settings:
        shown = rows.get(name, "").strip("`")
        want = expected.get(name, "empty")
        if name in rows and shown != want:
            wrong(f"README.md: the default of {name} is shown as {shown!r}; the program's default is {want!r}")
    return settings


def check_file_types(readme: str) -> None:
    lines = [line for line in readme.splitlines() if line.startswith(("- Photos:", "- Raw photos:", "- Videos:"))]
    listed = set(re.findall(r"`([a-z0-9]+)`", "\n".join(lines)))
    for extension in sorted(set(storage.MEDIA_EXTENSIONS) - listed):
        wrong(f"README.md: the file type {extension} is accepted by the program and not listed")
    for extension in sorted(listed - set(storage.MEDIA_EXTENSIONS)):
        wrong(f"README.md: the file type {extension} is listed and the program refuses it")


def check_compose(settings: list[str]) -> str:
    compose = read("docker-compose.yml")
    lines = without_comments(compose)
    for needed in (f"    image: {IMAGE}", "    container_name: phlix-camera-upload", "    restart: unless-stopped",
                   f'      - "{DEFAULT_PORT}:{DEFAULT_PORT}"', f"        source: {PLACEHOLDER}",
                   "        target: /photos", "          create_host_path: false", "      - ./config:/config",
                   '      - "host.docker.internal:host-gateway"', '      - "no-new-privileges:true"'):
        if needed not in lines:
            wrong(f"docker-compose.yml: this line is missing or changed: {needed.strip()}")
    if any(line.startswith("    environment:") for line in lines):
        wrong("docker-compose.yml: a setting is switched on; the file must work with none")

    examples = dict(re.findall(r'^    #   ([A-Z_]+): "(.*)"$', compose, re.M))
    for name in examples:
        if name not in settings:
            wrong(f"docker-compose.yml: {name} is listed and the program does not read it")
    try:
        loaded = config.load(dict(examples))
    except config.ConfigError as error:
        wrong(f"docker-compose.yml: the program refuses an example value: {error}")
    else:
        defaults = config.load({})
        for field in ("path_template", "umask", "tls", "pairing", "pairing_code", "name", "min_free_bytes",
                      "max_upload_bytes", "log_level"):
            if getattr(loaded, field) != getattr(defaults, field):
                wrong(f"docker-compose.yml: the example for {field} is not the program's default")
    for name in settings:
        if name not in examples and name not in compose:
            wrong(f"docker-compose.yml: the setting {name} is not mentioned")
    return compose


def check_copies(compose: str, guide: str, readme: str) -> None:
    """The Compose text exists in three places. They must not drift apart."""
    installer = read("install.sh")
    embedded = re.search(r"cat <<'PHLIX_COMPOSE_FILE'\n(.*?)^PHLIX_COMPOSE_FILE$", installer, re.S | re.M)
    if not embedded:
        wrong("install.sh: the Compose file inside it was not found")
    elif embedded.group(1) != compose:
        wrong("install.sh: the Compose file inside it differs from docker-compose.yml; "
              "run: python3 scripts/check-docs.py --sync")
    for line in ("    image: " + IMAGE, f'      - "{DEFAULT_PORT}:{DEFAULT_PORT}"', "        source: " + PLACEHOLDER,
                 "    # environment:", '    #   PLEX_URL: "http://192.168.1.10:32400"', '    #   PUID: "1000"',
                 '    #   PGID: "1000"'):
        if f"'{line}')" not in installer:
            wrong(f"install.sh: it no longer looks for this line of docker-compose.yml: {line.strip()}")

    block = re.search(r"```yaml\n(# Phlix Camera Upload\..*?)```", guide, re.S)
    if not block:
        wrong("SETUP-WITH-AI.md: the Compose text in Step 6 was not found")
    elif without_comments(block.group(1).replace(GUIDE_PLACEHOLDER, PLACEHOLDER)) != without_comments(compose):
        wrong("SETUP-WITH-AI.md: the Compose text in Step 6 differs from docker-compose.yml")

    run = re.search(r"^docker run (?:[^\n]*\\\n)*[^\n]*", readme, re.M)
    if not run:
        wrong("README.md: the docker run command was not found")
    else:
        for needed in ("--name phlix-camera-upload", "--restart unless-stopped", f"-p {DEFAULT_PORT}:{DEFAULT_PORT}",
                       "--add-host=host.docker.internal:host-gateway", "--security-opt no-new-privileges:true",
                       "target=/photos", ":/config", IMAGE):
            if needed not in run.group(0):
                wrong(f"README.md: the docker run command lacks {needed}")

    marker = "\n## Goal\n"
    skill = read(SKILL)
    if marker not in guide or marker not in skill:
        wrong(f"SETUP-WITH-AI.md and {SKILL}: the heading '## Goal' was not found in both")
    elif guide.split(marker, 1)[1] != skill.split(marker, 1)[1]:
        wrong(f"{SKILL}: its instructions differ from SETUP-WITH-AI.md; run: python3 scripts/check-docs.py --sync")
    check_skill(skill)


def check_skill(skill: str) -> None:
    """The rules that a skill must keep, in Claude Code and in the Claude apps."""
    front = re.match(r"---\nname: (\S+)\ndescription: (.+)\n---\n", skill)
    if not front:
        wrong(f"{SKILL}: it must start with a front matter that holds name and description, in that order")
        return
    name, description = front.group(1), front.group(2)
    if name != SKILL_NAME or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        wrong(f"{SKILL}: the name must be {SKILL_NAME}, the same as its folder")
    if len(description) > 1024:
        wrong(f"{SKILL}: the description has {len(description)} characters; 1024 is the most")
    for word in ("install", "check", "update", "troubleshoot", "remove"):
        if word not in description:
            wrong(f"{SKILL}: the description must say when to use the skill; it lacks the word {word!r}")
    body_lines = len(skill[front.end():].splitlines())
    if body_lines >= 500:
        wrong(f"{SKILL}: the body has {body_lines} lines; it must stay under 500")


def check_plugin() -> None:
    """The repository is a Claude Code plugin and a marketplace of one."""
    files = {}
    for path in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        try:
            files[path] = json.loads(read(path))
        except ValueError as error:
            wrong(f"{path}: it is not valid JSON: {error}")
            return
    plugin, market = files[".claude-plugin/plugin.json"], files[".claude-plugin/marketplace.json"]
    if plugin.get("version") != __version__:
        wrong(f".claude-plugin/plugin.json: the version is {plugin.get('version')!r}; "
              f"phlix_upload/__init__.py says {__version__!r}")
    listed = market.get("plugins") or [{}]
    if len(listed) != 1 or listed[0].get("name") != plugin.get("name") or listed[0].get("source") != "./":
        wrong(".claude-plugin/marketplace.json: it must list the one plugin of plugin.json, with the source ./")
    elif listed[0].get("description") != plugin.get("description"):
        wrong(".claude-plugin: the two files describe the plugin in different words")
    for document in ("README.md",):
        text = read(document)
        for needed in (f"/plugin marketplace add {REPOSITORY}", f"/plugin install {plugin.get('name')}@{market.get('name')}",
                       f"/{plugin.get('name')}:{SKILL_NAME}"):
            if needed not in text:
                wrong(f"{document}: it must show {needed}")


def slug(heading: str) -> str:
    """The anchor GitHub gives a heading."""
    return re.sub(r"[^a-z0-9 _-]", "", heading.strip().lower().replace("`", "")).replace(" ", "-")


def check_links() -> None:
    """Links between the files of this repository lead somewhere."""
    anchors = {}
    for path in DOCUMENTS:
        headings = re.findall(r"^#{1,6} (.+)$", re.sub(r"```.*?```", "", read(path), flags=re.S), re.M)
        anchors[path] = {slug(heading) for heading in headings}
    for path in PACKAGING:
        text = read(path)
        if path in DOCUMENTS:
            for target in re.findall(r"\]\(([^)\s]+)\)", text):
                if target.startswith("http"):
                    continue
                file, _, anchor = target.partition("#")
                goal = os.path.normpath(os.path.join(os.path.dirname(path), file)) if file else path
                if not os.path.exists(goal):
                    wrong(f"{path}: the link {target} leads to a file that does not exist")
                elif anchor and goal in anchors and anchor not in anchors[goal]:
                    wrong(f"{path}: the link {target} leads to a heading that does not exist")
        for file in re.findall(rf"raw\.githubusercontent\.com/{REPOSITORY}/main/([^\s)`>\"'<]+)", text):
            if not os.path.exists(file):
                wrong(f"{path}: it gives an address for {file}, which is not in this repository")
        for file, anchor in re.findall(rf"github\.com/{REPOSITORY}(?:/blob/main/([^\s)`>\"'<#]+))?(?:#([a-z0-9-]+))?", text):
            if file and not os.path.exists(file):
                wrong(f"{path}: it links to {file}, which is not in this repository")
            if not file and anchor and anchor not in anchors["README.md"]:
                wrong(f"{path}: it links to the heading #{anchor} of the README, which does not exist")


def check_compose_lines(compose: str) -> None:
    """A document that says "remove the line X" must name a line that exists."""
    held = [line.strip() for line in without_comments(compose)]
    for path in DOCUMENTS:
        text = read(path)
        for line in COMPOSE_LINES:
            if f"`{line}`" in text and not any(line == entry or entry.endswith(line) for entry in held):
                wrong(f"{path}: it names the line `{line}`, and docker-compose.yml has no such line")
        for word in ("source:", "ports:", "environment:", "CHANGE THE NEXT LINE"):
            if f"`{word}`" in text and word not in compose:
                wrong(f"{path}: it points at `{word}`, and docker-compose.yml does not hold that")


def check_quotes() -> None:
    """Commands, addresses and messages in the documents exist in the program."""
    said = {source: flat(read(source)) for source in PROGRAM_TEXT}
    commands = set(re.findall(r'command == "([a-z-]+)"', read("phlix_upload/__main__.py"))) | {"version", "help"}
    routes = set(re.findall(r'"(/api/v1/[a-z/]+|/healthz)"', read("phlix_upload/server.py")))
    for path in PACKAGING:
        if path == "scripts/check-docs.py":
            continue
        text = read(path)
        for command in sorted(set(re.findall(r"python3? -m phlix_upload ([a-z-]+)", text)) - commands):
            wrong(f"{path}: the program has no command named {command}")
        for route in sorted(set(re.findall(r"(/api/v1/[a-z]+(?:/[a-z]+)?|/healthz)", text))):
            if not any(known == route or known.startswith(route + "/") for known in routes):
                wrong(f"{path}: the program has no address {route}")
        if path in DOCUMENTS:
            for source, messages in PROGRAM_TEXT.items():
                for message in messages:
                    if message in text and message not in said[source]:
                        wrong(f"{path}: it quotes {message!r}, and {source} no longer says that")
            for message in RETIRED_TEXT:
                if message in text:
                    wrong(f"{path}: it quotes {message!r}, which the program stopped saying")


def check_limits() -> None:
    """The numbers in the documents are the numbers in the program."""
    limiter = inspect.signature(pairing.AttemptLimiter.__init__).parameters
    if (limiter["per_address"].default, limiter["address_window"].default, limiter["overall_window"].default) != (5, 60.0, 600.0):
        wrong("pairing.py: the limit for one address is no longer five wrong tries a minute, or the pause for "
              "everyone no longer counts ten minutes; change the documents and this check")
    everyone = limiter["overall"].default
    one, all_ = server_module.MAX_CONNECTIONS_PER_ADDRESS, server_module.MAX_CONNECTIONS
    handshake, first, idle = (server_module._HANDSHAKE_SECONDS, server_module._FIRST_REQUEST_SECONDS,
                              server_module._IDLE_SECONDS)
    needed = {
        "README.md": [
            "five wrong tries within a minute", f"{everyone} wrong pairing codes within ten minutes",
            f"{one} connections at once from one address and {all_} in all",
            f"{handshake} seconds for the TLS handshake and {first} seconds to send its first request",
            f"silent for {idle} seconds",
        ],
        "SECURITY.md": [
            "five wrong tries a minute", f"{everyone} wrong codes in ten minutes",
            f"{one} connections at once from one address, and {all_} in all",
            f"{handshake} seconds for the TLS handshake and {first} seconds to send its first request",
            f"silent for {idle} seconds", f"still hold {one} connections",
        ],
        "NETWORKING.md": [f"{one} connections at once from one address"],
        "SETUP-WITH-AI.md": ["five wrong tries within a minute", f"{everyone} wrong codes within ten minutes"],
    }
    for path, phrases in needed.items():
        text = read(path)
        for phrase in phrases:
            if phrase not in text:
                wrong(f"{path}: it must say \"{phrase}\", which is what the program does now")


def check_dockerfile() -> None:
    dockerfile = read("Dockerfile")
    for needed in ("PYTHONUNBUFFERED=1", "PYTHONDONTWRITEBYTECODE=1", "PHLIX_CONTAINER=1", f"EXPOSE {DEFAULT_PORT}",
                   'ENTRYPOINT ["python", "-m", "phlix_upload"]', "HEALTHCHECK", "/healthz", "openssl",
                   'org.opencontainers.image.source="https://github.com/jrl8085/phlix-camera-upload"',
                   'org.opencontainers.image.licenses="LicenseRef-Proprietary"'):
        if needed not in dockerfile:
            wrong(f"Dockerfile: it lacks {needed}")
    if re.search(r"^\s*(VOLUME|USER)\b", dockerfile, re.M):
        wrong("Dockerfile: it must have no VOLUME line and no USER line (see its comments)")
    if len(re.findall(r"^(COPY|ADD) ", dockerfile, re.M)) != 1 or "COPY phlix_upload/ " not in dockerfile:
        wrong("Dockerfile: it must copy the folder phlix_upload and nothing else")
    description = re.search(r'image\.description="([^"]+)"', dockerfile)
    release = read(".github/workflows/release.yml")
    if description and release.count("org.opencontainers.image.description=" + description.group(1)) != 2:
        wrong("release.yml: the image description must be the Dockerfile's, once as a label and once as an annotation")


def check_unraid() -> None:
    path = "unraid/phlix-camera-upload.xml"
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as error:
        wrong(f"{path}: it is not well-formed XML: {error}")
        return
    if root.findtext("Repository") != IMAGE or root.findtext("Name") != "phlix-camera-upload":
        wrong(f"{path}: the name or the repository changed")
    if "--add-host=host.docker.internal:host-gateway" not in (root.findtext("ExtraParams") or ""):
        wrong(f"{path}: ExtraParams lacks the add-host flag")
    passed = {}
    for entry in root.findall("Config"):
        if entry.get("Type") == "Variable":
            # Unraid passes the value, or the default when the value is empty.
            passed[entry.get("Target")] = (entry.text or "") or (entry.get("Default") or "")
    try:
        config.load(passed)
    except config.ConfigError as error:
        wrong(f"{path}: the program refuses what Unraid passes when nothing is edited: {error}")


def check_wording() -> None:
    forbidden = "ca" + "st"
    for path in PACKAGING:
        text = read(path)
        if re.search(forbidden, text, re.I):
            wrong(f"{path}: it holds the letters '{forbidden}' in a row, which the product's rules forbid")
        if any(ord(character) > 127 for character in text):
            wrong(f"{path}: it holds a character that is not plain ASCII")
    for path in DOCUMENTS:
        text = read(path)
        if [line for line in text.rstrip("\n").split("\n") if line.strip()][-2:] != TRADEMARK_LINES:
            wrong(f"{path}: it must end with the two trademark lines, exactly")
        if "!" in prose(text):
            wrong(f"{path}: it has an exclamation mark outside code")
    if "Phlix (phlixapp.com)" not in read("LICENSE"):
        wrong("LICENSE: the copyright holder must be Phlix (phlixapp.com)")


def sync() -> None:
    """Make the two copies again: the Compose file in install.sh, and the
    instructions in the skill."""
    compose = read("docker-compose.yml")
    installer = read("install.sh")
    copied = re.sub(r"(cat <<'PHLIX_COMPOSE_FILE'\n).*?(^PHLIX_COMPOSE_FILE$)",
                    lambda match: match.group(1) + compose + match.group(2), installer, flags=re.S | re.M)
    if copied != installer:
        with open("install.sh", "w", encoding="utf-8") as handle:
            handle.write(copied)
        print("install.sh: copied docker-compose.yml into it")

    marker = "\n## Goal\n"
    guide, skill = read("SETUP-WITH-AI.md"), read(SKILL)
    if marker in guide and marker in skill:
        copied = skill.split(marker, 1)[0] + marker + guide.split(marker, 1)[1]
        if copied != skill:
            with open(SKILL, "w", encoding="utf-8") as handle:
                handle.write(copied)
            print(f"{SKILL}: copied the instructions of SETUP-WITH-AI.md into it")


def main() -> int:
    if sys.argv[1:] == ["--sync"]:
        sync()
    elif sys.argv[1:]:
        print("Usage: python3 scripts/check-docs.py [--sync]", file=sys.stderr)
        return 2
    readme, guide = read("README.md"), read("SETUP-WITH-AI.md")
    settings = check_settings_table(readme)
    check_file_types(readme)
    compose = check_compose(settings)
    check_copies(compose, guide, readme)
    check_compose_lines(compose)
    check_quotes()
    check_limits()
    check_dockerfile()
    check_unraid()
    check_plugin()
    check_links()
    check_wording()
    if problems:
        for problem in problems:
            print(f"WRONG  {problem}")
        print(f"{len(problems)} to fix. The documents and the program must agree.")
        return 1
    print("The documents agree with the program.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

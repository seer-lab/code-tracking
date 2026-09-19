# Continue (JetBrains Plugin) — Patched Build for KOALA Study

This directory contains a modified copy of the open-source [Continue](https://github.com/continuedev/continue)
AI coding assistant, licensed under Apache 2.0. It is vendored here (source copied in, not a git submodule) so
the study's plugin build stays fixed and self-contained.

## Why this copy exists

Continue's officially released JetBrains plugin (up to v1.0.67 at the time of writing) crashes with:

```
NoClassDefFoundError: com/intellij/ui/jcef/JBCefApp
```

on IntelliJ Platform 2026.2.1 and later (this affects any JetBrains IDE on that platform version, e.g. PyCharm
2026.2, IntelliJ IDEA 2026.2.1+ — not just IntelliJ IDEA specifically). This is a platform-wide regression:
starting with 2026.2.1, plugins that use JCEF (the embedded Chromium browser component) must explicitly declare
that dependency, or the class fails to load at runtime even though it's present.

### The fix

One line added to `extensions/intellij/src/main/resources/META-INF/plugin.xml`:

```xml
<depends>com.intellij.modules.jcef</depends>
```

added inside the `<idea-plugin>` tag. No other source changes were made.

## Building the plugin

The plugin is built from source rather than downloading a prebuilt release, so the fix above is baked in. This
produces a single `.zip` that works on **any JetBrains IDE, on any OS** (Windows, macOS, Linux) — the plugin
bundles native binaries for all supported platforms, so you only need to build it once.

### Prerequisites

- **Node.js v20.20.1** (use [nvm](https://github.com/nvm-sh/nvm) to install/switch: `nvm install 20.20.1 && nvm use 20.20.1`).
  Newer Node versions (tested: v24.21.0) break the native binary build — the `node:sqlite` built-in module isn't
  compatible with the `pkg` bundler this project uses to produce standalone binaries.
- **JDK 17** (the Gradle build requires this specific version; if you have another JDK installed, set `JAVA_HOME`
  to a JDK 17 install for the build step below).
- **Git**, **npm**, standard build tools (`zip`/`unzip` on Linux/macOS).

### Steps

```bash
# 1. From the repo root, enter the plugin directory
cd continue

# 2. Make sure you're on the correct Node version
nvm use 20.20.1

# 3. Install dependencies, build shared packages, and compile the native
#    continue-binary for all platforms (Windows/macOS/Linux, x64/arm64).
#    This step takes several minutes.
./scripts/install-dependencies.sh

# 4. Build the JetBrains plugin itself
cd extensions/intellij
JAVA_HOME=/path/to/jdk-17 ./gradlew buildPlugin
```

The built plugin zip will be at:

```
extensions/intellij/build/distributions/continue-intellij-extension-<version>.zip
```

That's the file to distribute to students.

## Distributing to students

Students install the built zip via:

**Settings → Plugins → gear icon (⚙) → Install Plugin from Disk...** → select the `.zip` from the build step above.

If a student previously installed a broken version of Continue (the one that crashes with the JCEF error), it
needs to be fully removed first — a stale cached copy or leftover settings can cause the new install to silently
reuse broken state. See the Troubleshooting section below.

## Troubleshooting

### Old/broken Continue install won't go away after uninstalling from the Plugins UI

JetBrains IDEs sometimes leave cached plugin data behind. On Linux, for example (paths follow the same pattern
on macOS/Windows, just under different base directories):

- Installed plugin files: `~/.local/share/JetBrains/<Product><Version>/continue-intellij-extension/`
- Cached download: `~/.cache/JetBrains/<Product><Version>/plugins/continue-intellij-extension.zip`
- Plugin settings: `~/.config/JetBrains/<Product><Version>/options/ContinueExtensionSettings.xml`

Fully quit the IDE, delete those three paths, then reinstall the fixed zip and restart the IDE completely
(not just reload). A `ClassCastException` involving `PluginClassLoader` after installing a new build is a sign
the IDE wasn't fully restarted between uninstall and reinstall — quitting and relaunching clears it.

### Model loading hangs / takes a very long time after adding an API key

This was traced to the native `continue-binary` process crash-looping due to a `node:sqlite` incompatibility
present on Continue's unreleased `main` branch. Building from the `v1.0.67-jetbrains` release tag (as opposed to
`main`) resolves this — check `~/.continue/logs/core.log` and the IDE's own log
(`~/.cache/JetBrains/<Product><Version>/log/idea.log`) for a repeating start/crash pattern if this recurs.

## License

Continue is licensed under the Apache License 2.0. This directory is a modified copy of the original project;
per the license terms, the original copyright and license notices are retained, and the modification made here
(the `plugin.xml` JCEF dependency fix, above) is documented in this README. See [`LICENSE`](LICENSE) for the
full license text.

Original project: https://github.com/continuedev/continue

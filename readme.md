# HEOS 

`Heos` is a small Python library + client for Denon's HEOS-powered multi-room speakers systems. The package aims to provide a straight-forward interface for issuing commands to HEOS-powered speakers.

## Getting started

You can install the package from source using:

```
pip install git+https://github.com/jrderuiter/heos.git
```

Should there be sufficient interest, we'll consider providing a package in PyPI once development has stabilised.

## Examples

### Controlling individual speakers

You can issue commands directly to individual players (= speakers) using the `Player` class. 

First, you need to obtain a reference to the corresponding player from the `Registry`, which effectively tracks all the speakers available on your local network. You can retrieve a specific player using it's name:

```
from heos.registry import Registry

registry = Registry()

player = registry.players["Living Room"]
```

Once you have a reference to a player, you can issue commands to it using it's properties and methods.

For example, to set the player volume, simply assign a new value to the volume property: 

```
player.volume = 10
```

Note that you can use the same property to check the current volume of the player.

Similarly, you can mute a player using it's mute property:
```
player.mute = True
```

You can also control playback using the `start`/`pause`/`stop` methods:

```
player.pause() # Pause playback
player.play()  # Resume playback
player.stop()  # Stop playback
```

### Controlling speaker groups

If you have multiple speakers combined into a group, you can also issue commands to the group using the `Group` class. 

Player groups can also be retrieved using the player registry:

```
from heos.registry import Registry

registry = Registry()
group = registry.groups["Downstairs"]
```

Groups have the same interface as players (where possible), meaning you can also control player groups in a similar fashion:

```
group.volume = 10 # Set the group volume
group.mute = True # Mute the group
```

### (Re-)discovering speakers

By default, the player registry caches players found on the network in a file called `.heos`. This allows us to avoid having to go through the (relatively slow) process of discovering speakers on your network for every new session. Sometimes you may want to force re-discovery however, for example when you've added new speakers or changed speaker/group names. 

You can force re-discovery using the registry's `discover` method:

```
from heos.registry import Registry

registry = Registry()
registry.discover()
```

Alternatively, you can also delete the `.heos` file to start clean.

# Command line interface 

The `heos` library also provides a command line interface (CLI) that you can use to send commands to players or player groups from the terminal.

For example, you can set the volume for a given player using:

```
heos player --name "Living Room" set-volume 10
```

Similarly, you can mute a player using:

```
heos player --name "Living Room" mute
```
 
Equivalent commands are provided for player groups using the `heos group` comand.

# Contributing 

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Report Bugs

Report bugs at https://github.com/jrderuiter/heos/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

## Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

## Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

## Write Documentation

We  could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

## Submit Feedback

The best way to send feedback is to file an issue at https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

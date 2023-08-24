# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added additional tests for the REST API
- Added support for using dotenv for loading credentials for testing
- Added CI workflow for creating releases both in Gitlab and Github
- Added Changelog to mkdocs

## [1.1.2] - 2023-08-16

### Changed
- Added License shield to README
- Added GPL-3.0 License headers to all files

## [1.1.1] - 2023-08-15

### Changed

- Updated pyproject file with relevant information

## [1.1.0] - 2023-08-15

### Added

- Added argument to log to file
- Added docstring for `InterceptHandler`

## [1.0.0] - 2023-08-15

### Added

- Added `get_player_games` to `OGSClient`. Gets list of games from a player
- Added `loguru` as a logging backend
- Added plenty of debug, info, success, and error logs to make troubleshooting hopefully easier

### Changed

- Updated documentation to reflect logging changes

## [0.9.1] - 2023-08-15

### Changed

- Refactored the `OGSGame` class to put the game and clock data into their own dataclasses respectively.

## [0.9.0] - 2023-08-02

### Changed

- All realtime socket events are now being sent to two different event handlers, instead of one for each event. One for the realtime API in general, and one for each game you are connected to. See the Usage documentation for more details

### Added

- Added methods to `OGSClient` to manually connect and disconnect to the realtime API

## [0.8.0] - 2023-08-01

### Changed

- The client no longer connects to the Realtime API by default, you must now manually call the socket_connect method to connect. This will make working with just the REST API easier, not having to deal with the Websocket
- Updated documentation to reflect that when using the Websocket, you are responsible for disconnecting from the server via socket_disconnect, otherwise a Keyboard Inturrupt will be required to close out

### Removed

- Removed the redundant destructor on `OGSClient` that disconnected from the websocket, it wasnt working correctly, and now it will be the users responsibility anyway

## [0.7.3] - 2023-07-14

### Added

- Added methods for getting games as a PNG or SGF
- Added methods for getting list of game reviews for a game

### Changed

- Create `OGSRestAPI` class for handling direct calls to API
- Create `OGSCredentials` class for handling the user credentials
- Move Socket token grabbing to `OGSRestAPI`

## [0.7.2] - 2023-07-06

### Fixed

- OGSSClient now properly disconnects the OGSSocket from the realtime API to be able to close out without a KeyboardInturrupt

## [0.7.0] - 2023-07-06

### Fixed

- Fixed issues causing errors during import
  - Removed circular dependency
  - Moved class imports to local imports vs absolute

## [0.6.1] - 2023-06-29

### Added

- New socket functions for the following events
  - pause/resume
  - cancel game
  - cancel / accept undo
  - sending chat

### Changed

- Refactored code to make the library more readable, with the large classes being broken into seperate files.
- Renamed primary file to client.py from api.py, chaning the import string to ogsapi.client

## [0.5.0] - 2023-05-02

### Added

- Added socket level callbacks for `error` and `notification` events
- Added Game Phase change handler and callback
- Implemented proper challenge creation, You can now define the challenge settings, and send it out as an open challenge, or to a specific player.

### Changed

- Fixed undo cancelled to be the British canceled. Thank you, @aureop!

## [0.4.1] - 2023-04-26

### Changed

- Documentation improvements

## [0.4.0] - 2023-04-26

### Added

- Added relevant game data to the OGSGame class
- Implemented clock handling
- Implemented handling of undo actions
- Added asdict() method to OGSGame to get game data as a dict
- Added mkdocs documentation

### Removed

- Remove printing of bearer token on connecting to API


## [0.3.0] - 2023-04-18

### Added

- Implemented ability to update user settings
- Added on move handling via callback functions
- Connecting to a game now returns the object, allowing for direct assignment

### Changed

- Privated functions used only internally
- Updated docs

## [0.2.1] - 2023-04-04

### Changed

- Set socketio to not log by default

## [0.2.0] - 2023-04-04

### Added

- Initial release

[unreleased]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v1.1.2...HEAD
[1.1.2]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v1.1.1...v1.1.2
[1.1.1]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v1.1.0...v1.1.1
[1.1.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v1.0.0...v1.1.0
[1.0.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.9.1...v1.0.0
[0.9.1]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.9.0...v0.9.1
[0.9.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.8.0...v0.9.0
[0.8.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.7.3...v0.8.0
[0.7.3]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.7.2...v0.7.3
[0.7.2]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/v0.7.0...v0.7.2
[0.7.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.6.1...v0.7.0
[0.6.1]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.5.0...0.6.1
[0.5.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.4.1...0.5.0
[0.4.1]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.4.0...0.4.1
[0.4.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.3.0...0.4.0
[0.3.0]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.2.1...0.3.0
[0.2.1]: https://gitlab.com/dakota.marshall/ogs-python/-/compare/0.2.0...0.2.1
[0.2.0]: https://gitlab.com/dakota.marshall/ogs-python/-/tags/0.2.0
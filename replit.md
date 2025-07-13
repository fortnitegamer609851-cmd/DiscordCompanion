# Pennsylvania State Roleplay Discord Bot

## Overview

This is a Discord bot built with Python and discord.py for the Pennsylvania State Roleplay server. The bot provides essential server management features including welcome messages, member count display, moderation tools, and messaging utilities. The architecture follows a modular cog-based design for maintainability and extensibility.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes

**July 13, 2025:**
- Fixed command synchronization issue - all slash commands now properly sync to Discord
- Updated welcome message to include non-clickable button displaying member count with custom emoji
- Eliminated duplicate welcome messages by removing redundant bot instance
- Confirmed 24/7 hosting functionality with proper Discord token and privileged intents
- Implemented comprehensive command logging system to track all command usage
- Updated DM command to send plain messages without embeds for natural appearance
- Removed /help command per user request
- Replaced session commands with /infract system for staff infractions
- Added infraction command with custom embed, PA logo, and automatic appeal thread creation

## System Architecture

The bot follows a modular architecture using Discord.py's cog system:

- **Main Application**: `main.py` serves as the entry point and bot initialization
- **Keep Alive Service**: `keep_alive.py` provides a Flask-based health monitoring service
- **Modular Cogs**: Feature-specific modules in `bot/cogs/` directory
- **Utility Layer**: Common functionality in `bot/utils/` directory
- **Data Storage**: JSON-based file storage for case tracking

## Key Components

### Core Bot Structure
- **Discord Bot Instance**: Built with discord.py using slash commands and traditional commands
- **Cog System**: Modular feature organization for maintainability
- **Event Handling**: Member join events, guild join/leave events
- **Command Synchronization**: Automatic slash command syncing on startup

### Cog Modules

#### Welcome System (`bot/cogs/welcome.py`)
- Automatically welcomes new members in designated channel
- Uses custom emoji with fallback to standard Unicode
- Configurable welcome channel ID

#### Member Count (`bot/cogs/member_count.py`)
- Displays current server member count via slash command
- Interactive button UI with custom emoji support
- Real-time member count display

#### Moderation Tools (`bot/cogs/moderation.py`)
- Kick command with case tracking
- DM notification system for moderated users
- Permission checking and role hierarchy validation
- Case number generation and tracking

#### Messaging Utilities (`bot/cogs/messaging.py`)
- Bot message sending (`/say` command)
- Direct message functionality (`/dm` command)
- Permission-based access control

### Utility Layer

#### Permission System (`bot/utils/permissions.py`)
- Role-based permission checking
- Moderator role validation
- Administrator and guild owner detection
- Hierarchical permission system

#### Case Tracking (`bot/utils/case_tracker.py`)
- JSON-based case storage
- Sequential case number generation
- Persistent data management
- Error handling and recovery

## Data Flow

1. **Bot Initialization**: Main bot loads environment variables, sets up intents, and loads cogs
2. **Command Processing**: Slash commands are processed through respective cogs
3. **Permission Validation**: Commands check user permissions before execution
4. **Data Persistence**: Moderation actions are logged with case numbers
5. **Event Handling**: Member join events trigger welcome messages

## External Dependencies

### Discord API
- **discord.py**: Primary bot framework
- **Slash Commands**: Modern Discord interaction system
- **Intents**: Message content, members, and guilds access

### Infrastructure
- **Flask**: Health monitoring and keep-alive service
- **Threading**: Concurrent Flask server operation
- **Environment Variables**: Token and configuration management

### Data Storage
- **JSON Files**: Local file-based data persistence
- **File System**: Case data stored in `data/cases.json`

## Deployment Strategy

### Environment Setup
- Discord bot token via environment variables
- Dotenv for local development configuration
- Logging configuration for monitoring

### Service Architecture
- **Primary Service**: Discord bot with event loop
- **Health Service**: Flask server on port 5000 for uptime monitoring
- **Threaded Execution**: Concurrent operation of both services

### Configuration Management
- Hard-coded channel and role IDs for specific server
- Custom emoji IDs with fallback mechanisms
- Modular configuration through constants

### Error Handling
- Comprehensive logging throughout all modules
- Graceful degradation for custom emoji failures
- Permission error handling with user feedback
- Data persistence error recovery
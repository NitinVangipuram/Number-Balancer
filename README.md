# Number-Balancer Game Project

A math-based educational game where players solve arithmetic problems by balancing target numbers using available numbers and operations.

## Project Overview

The Balance Game is an interactive educational tool designed to help users improve their arithmetic skills through gameplay. Players are presented with a target number and must use available numbers and operations to reach that target within a time limit.

## Features

- **Multiple difficulty levels**: From very easy to very hard
- **Time-based challenges**: Solve problems within time limits
- **Customizable game settings**: Adjust timers and animations
- **Admin panel**: Create and manage game levels
- **User progression tracking**: Monitor improvement over time
- **Authentication**: Secure user accounts and data

## Tech Stack

- **Frontend**: Vue.js 3 with Composition API
- **Backend**: FastAPI (Python)
- **Authentication**: Firebase Authentication
- **Styling**: Tailwind CSS
- **State Management**: Pinia

## Architecture

The project follows a client-server architecture:

1. **Frontend**: Vue.js SPA that handles game UI, user interactions, and admin panel
2. **Backend**: FastAPI application that manages game configurations, user progress, and data persistence
3. **Authentication**: Firebase handles user authentication and authorization

## Getting Started

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- Firebase account
- npm or yarn

### Installation

#### Backend Setup

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/balance-game.git
   cd balance-game
   ```

2. Set up a Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. Run the FastAPI server
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup

1. Navigate to the frontend directory
   ```bash
   cd frontend
   ```

2. Install dependencies
   ```bash
   npm install
   # or
   yarn install
   ```

3. Configure Firebase
   - Create a new Firebase project
   - Enable Authentication (Email/Password)
   - Create a web app in your Firebase project
   - Copy the Firebase configuration to `src/firebase/config.js`

4. Run the development server
   ```bash
   npm run dev
   # or
   yarn dev
   ```

### API Endpoints

#### Game Configurations

- `GET /game-configurations/`: Retrieve all game configurations
- `GET /game-configurations/{id}`: Retrieve a specific game configuration
- `POST /game-configurations/`: Create a new game configuration
- `PUT /game-configurations/{id}`: Update a game configuration
- `DELETE /game-configurations/{id}`: Delete a game configuration


## Admin Panel

The admin panel allows privileged users to:

- Create and modify game levels
- Set difficulty parameters (target ranges, available numbers, time limits)
- Enable/disable levels
- Apply predefined difficulty presets
- Export and import game configurations

## User Authentication

Firebase Authentication is used to handle:
- User registration and login
- Role-based access control (admin vs regular users)
- Secure access to user data and progress

## Challenges and Solutions

During the development of the Balance Game, we encountered several challenges:

### Data Structure Mismatches

**Challenge**: Significant differences between the frontend data structure and the backend API expectations caused issues with saving and retrieving game configurations.

**Solution**: We implemented transformation functions to convert between the frontend and backend data models and added validation to ensure data integrity.

### Authentication Integration

**Challenge**: Integrating Firebase Authentication with FastAPI backend for secure API access proved complex.

**Solution**: We created a middleware in FastAPI to verify Firebase tokens and implemented a custom authentication store in Vue to manage user sessions and permissions.

### Cross-Browser Compatibility

**Challenge**: Ensuring consistent animation timing and gameplay experience across different browsers and devices.

**Solution**: We implemented a browser detection system and adjusted animation timings based on the platform. We also created a comprehensive testing suite to verify functionality across environments.

### Accessibility Requirements

**Challenge**: Making the game accessible to users with different abilities without compromising the core gameplay.

**Solution**: We implemented keyboard controls, screen reader support, and configurable difficulty levels to accommodate diverse user needs.

## Deployment

### Backend Deployment

1. Set up a server with Python support
2. Configure environment variables for production
3. Install dependencies and run with a production ASGI server like Uvicorn behind Nginx

### Frontend Deployment

1. Build the production version
   ```bash
   npm run build
   # or
   yarn build
   ```

2. Deploy the `dist` directory to a static hosting service or server



## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Vue.js](https://vuejs.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Firebase](https://firebase.google.com/)
- [Tailwind CSS](https://tailwindcss.com/)

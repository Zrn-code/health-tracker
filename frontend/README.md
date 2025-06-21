# Health Tracker Frontend

React + Vite Frontend Application

## Requirements

- Node.js 16+
- npm or yarn

## Installation & Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build project
npm run build

# Preview build result
npm run preview
```

## Project Structure

```text
frontend/
├── src/
│   ├── components/     # Reusable components
│   ├── pages/          # Page components
│   ├── hooks/          # Custom React hooks
│   ├── services/       # API services
│   ├── utils/          # Utility functions
│   └── App.jsx         # Main application component
├── public/             # Static assets
└── package.json
```

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router
- **HTTP Client**: Axios
- **Styling**: CSS Modules / Styled Components
- **Development**: Hot Module Replacement (HMR)

## Core Features

### User Interface

- **Modern React**: Latest React 18 with hooks and functional components
- **Responsive Design**: Mobile-first responsive layout
- **Interactive Forms**: User registration, login, and profile management
- **Real-time Updates**: Live data synchronization with backend

### Health Tracking Interface

- **Daily Entry Forms**: Intuitive forms for health data input
- **Data Visualization**: Charts and graphs for progress tracking
- **History View**: Browse and manage historical health records
- **AI Suggestions Display**: View personalized health recommendations

### User Experience

- **Fast Loading**: Vite's lightning-fast development and build process
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Loading States**: Smooth loading indicators and skeleton screens
- **Accessibility**: WCAG compliant interface design

## API Integration

The frontend communicates with the Flask backend API:

- Authentication endpoints for login/register
- Profile management for user data
- Health data CRUD operations
- AI suggestion retrieval

## Development Commands

```bash
# Development server with hot reload
npm run dev

# Type checking (if using TypeScript)
npm run type-check

# Linting
npm run lint

# Production build
npm run build

# Preview production build locally
npm run preview
```

## Environment Configuration

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:8080/api
VITE_APP_TITLE=Health Tracker
```

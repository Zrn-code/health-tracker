import React, { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";
import UserProfile from "./components/UserProfile";
import HistoryView from "./components/HistoryView";
import HealthSuggestions from "./components/HealthSuggestions";

function App() {
  const [currentPage, setCurrentPage] = useState("login");

  const renderPage = () => {
    switch (currentPage) {
      case "login":
        return (
          <Login
            onSwitchToRegister={() => setCurrentPage("register")}
            onLoginSuccess={() => setCurrentPage("profile")}
          />
        );
      case "register":
        return <Register onSwitchToLogin={() => setCurrentPage("login")} />;
      case "profile":
        return (
          <UserProfile
            onLogout={() => setCurrentPage("login")}
            onBack={() => setCurrentPage("login")}
            onViewHistory={() => setCurrentPage("history")}
            onGetSuggestions={() => setCurrentPage("suggestions")}
          />
        );
      case "history":
        return (
          <HistoryView
            onBack={() => setCurrentPage("profile")}
            onLogout={() => setCurrentPage("login")}
          />
        );
      case "suggestions":
        return (
          <HealthSuggestions
            onBack={() => setCurrentPage("profile")}
            onLogout={() => setCurrentPage("login")}
          />
        );
      default:
        return (
          <Login
            onSwitchToRegister={() => setCurrentPage("register")}
            onLoginSuccess={() => setCurrentPage("profile")}
          />
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary">
      {renderPage()}
    </div>
  );
}

export default App;

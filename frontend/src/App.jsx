import React, { useState } from "react";
import Login from "./components/Login";
import Register from "./components/Register";

function App() {
  const [currentPage, setCurrentPage] = useState("login");

  const renderPage = () => {
    switch (currentPage) {
      case "login":
        return <Login onSwitchToRegister={() => setCurrentPage("register")} />;
      case "register":
        return <Register onSwitchToLogin={() => setCurrentPage("login")} />;
      default:
        return <Login onSwitchToRegister={() => setCurrentPage("register")} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary">
      {renderPage()}
    </div>
  );
}

export default App;

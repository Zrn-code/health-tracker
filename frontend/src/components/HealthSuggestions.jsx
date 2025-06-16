import React, { useState } from "react";

const HealthSuggestions = ({ onBack, onLogout }) => {
  const [suggestion, setSuggestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [alreadyReceived, setAlreadyReceived] = useState(false);

  const getSuggestion = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        onLogout();
        return;
      }

      const response = await fetch(
        "http://localhost:5000/api/health/suggestion",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSuggestion(data.suggestion);
        setAlreadyReceived(data.already_received);
      } else if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        onLogout();
      } else if (response.status === 503) {
        setError(
          "Health suggestions are currently unavailable. Please try again later."
        );
      } else {
        const data = await response.json();
        setError(data.error || "Failed to get suggestion");
      }
    } catch (error) {
      console.error("Error getting suggestion:", error);
      setError("Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 transition duration-200 flex items-center"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                Back to Dashboard
              </button>
              <h1 className="text-3xl font-bold text-gray-800">
                Health Suggestions
              </h1>
            </div>
            <button
              onClick={onLogout}
              className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="mb-8">
              <svg
                className="w-20 h-20 mx-auto mb-4 text-purple-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                Personalized Health Suggestion
              </h2>
              <p className="text-gray-600">
                Get AI-powered health recommendations based on your daily data
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
                {error}
              </div>
            )}

            {!suggestion && !loading && (
              <button
                onClick={getSuggestion}
                className="bg-purple-500 hover:bg-purple-600 text-white font-medium py-3 px-8 rounded-lg transition duration-200 flex items-center mx-auto"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                Get Today's Suggestion
              </button>
            )}

            {loading && (
              <div className="flex items-center justify-center">
                <svg
                  className="animate-spin -ml-1 mr-3 h-8 w-8 text-purple-500"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span className="text-purple-600 font-medium">
                  Generating your personalized suggestion...
                </span>
              </div>
            )}

            {suggestion && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 mt-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <svg
                      className="w-8 h-8 text-purple-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                  </div>
                  <div className="ml-4 text-left">
                    <h3 className="text-lg font-semibold text-purple-800 mb-2">
                      {alreadyReceived
                        ? "Today's Suggestion (Already Received)"
                        : "Today's Suggestion"}
                    </h3>
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {suggestion}
                    </p>
                    {alreadyReceived && (
                      <p className="text-purple-600 text-sm mt-3 font-medium">
                        You've already received today's suggestion. Come back
                        tomorrow for a new one!
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {suggestion && !alreadyReceived && (
              <div className="mt-6">
                <button
                  onClick={() => {
                    setSuggestion("");
                    setAlreadyReceived(false);
                  }}
                  className="bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-6 rounded-lg transition duration-200"
                >
                  Get Another Suggestion
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <div className="flex items-center">
            <svg
              className="w-6 h-6 text-blue-500 mr-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div>
              <h4 className="font-semibold text-blue-800">How it works</h4>
              <p className="text-blue-700 text-sm mt-1">
                Our AI analyzes your recent health data including weight,
                height, and meal patterns to provide personalized
                recommendations. You can receive one suggestion per day to help
                improve your health journey.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HealthSuggestions;

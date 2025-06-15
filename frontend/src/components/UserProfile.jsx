import React, { useState, useEffect } from "react";

const UserProfile = ({ onLogout, onBack }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        onLogout();
        return;
      }

      const response = await fetch("http://localhost:5000/api/profile", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        onLogout();
      } else {
        setError("Failed to load profile");
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userId");
    onLogout();
  };

  const formatDate = (dateObj) => {
    if (!dateObj) return "N/A";
    if (dateObj._seconds) {
      return new Date(dateObj._seconds * 1000).toLocaleDateString();
    }
    return new Date(dateObj).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <div className="text-red-600 text-center mb-4">{error}</div>
          <button
            onClick={onBack}
            className="w-full bg-primary text-white py-2 px-4 rounded hover:bg-primary-dark transition duration-200"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">User Profile</h1>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Basic Information */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Basic Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <label className="block text-sm font-medium text-gray-600">
                Username
              </label>
              <p className="text-lg text-gray-800">
                {profile?.username || "N/A"}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <label className="block text-sm font-medium text-gray-600">
                Email
              </label>
              <p className="text-lg text-gray-800">{profile?.email || "N/A"}</p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <label className="block text-sm font-medium text-gray-600">
                Account Created
              </label>
              <p className="text-lg text-gray-800">
                {formatDate(profile?.created_at)}
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded">
              <label className="block text-sm font-medium text-gray-600">
                Profile Status
              </label>
              <p
                className={`text-lg font-semibold ${
                  profile?.profile_completed
                    ? "text-green-600"
                    : "text-orange-600"
                }`}
              >
                {profile?.profile_completed ? "Completed" : "Incomplete"}
              </p>
            </div>
          </div>
        </div>

        {/* Health Information */}
        {profile?.profile_completed ? (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Health Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded">
                <label className="block text-sm font-medium text-blue-600">
                  Birth Date
                </label>
                <p className="text-lg text-gray-800">
                  {formatDate(profile?.birth_date)}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded">
                <label className="block text-sm font-medium text-green-600">
                  Initial Height
                </label>
                <p className="text-lg text-gray-800">
                  {profile?.initial_height
                    ? `${profile.initial_height} cm`
                    : "N/A"}
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded">
                <label className="block text-sm font-medium text-purple-600">
                  Initial Weight
                </label>
                <p className="text-lg text-gray-800">
                  {profile?.initial_weight
                    ? `${profile.initial_weight} kg`
                    : "N/A"}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-orange-50 border-l-4 border-orange-400 rounded-lg p-6 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-orange-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-lg font-medium text-orange-800">
                  Complete Your Profile
                </h3>
                <p className="text-orange-700 mt-1">
                  Please complete your health profile to get personalized
                  suggestions and track your progress.
                </p>
                <button className="mt-3 bg-orange-500 text-white py-2 px-4 rounded hover:bg-orange-600 transition duration-200">
                  Complete Profile
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-blue-500 text-white py-3 px-6 rounded-lg hover:bg-blue-600 transition duration-200 flex items-center justify-center">
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              View Daily Data
            </button>
            {profile?.profile_completed && (
              <button className="bg-green-500 text-white py-3 px-6 rounded-lg hover:bg-green-600 transition duration-200 flex items-center justify-center">
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
                    d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                  />
                </svg>
                Add Daily Entry
              </button>
            )}
            <button className="bg-purple-500 text-white py-3 px-6 rounded-lg hover:bg-purple-600 transition duration-200 flex items-center justify-center">
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
                  d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                />
              </svg>
              Health Suggestions
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;

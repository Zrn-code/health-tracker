import React, { useState, useEffect } from "react";

const UserProfile = ({ onLogout, onBack }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split("T")[0],
    height: "",
    weight: "",
    breakfast: "",
    lunch: "",
    dinner: "",
  });
  const [profileData, setProfileData] = useState({
    birth_date: "",
    initial_height: "",
    initial_weight: "",
  });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [submitMessage, setSubmitMessage] = useState("");
  const [profileSubmitLoading, setProfileSubmitLoading] = useState(false);
  const [profileSubmitMessage, setProfileSubmitMessage] = useState("");

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleProfileInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmitDailyData = async (e) => {
    e.preventDefault();
    setSubmitLoading(true);
    setSubmitMessage("");

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:5000/submit_daily_data", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setSubmitMessage("Daily data submitted successfully!");
        setFormData({
          date: new Date().toISOString().split("T")[0],
          height: "",
          weight: "",
          breakfast: "",
          lunch: "",
          dinner: "",
        });
      } else {
        setSubmitMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error("Error submitting daily data:", error);
      setSubmitMessage("Network error occurred");
    } finally {
      setSubmitLoading(false);
    }
  };

  const handleSubmitProfile = async (e) => {
    e.preventDefault();
    setProfileSubmitLoading(true);
    setProfileSubmitMessage("");

    try {
      const token = localStorage.getItem("token");
      const response = await fetch("http://localhost:5000/api/profile", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (response.ok) {
        setProfileSubmitMessage("Profile completed successfully!");
        // Refresh profile data
        await fetchProfile();
        // Reset form
        setProfileData({
          birth_date: "",
          initial_height: "",
          initial_weight: "",
        });
      } else {
        setProfileSubmitMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error("Error submitting profile:", error);
      setProfileSubmitMessage("Network error occurred");
    } finally {
      setProfileSubmitLoading(false);
    }
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
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-800">
              Health Tracker Dashboard
            </h1>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition duration-200"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Main Content - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Profile Information */}
          <div className="lg:col-span-1">
            {/* Basic Information */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                Profile Information
              </h2>
              <div className="space-y-4">
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
                  <p className="text-lg text-gray-800">
                    {profile?.email || "N/A"}
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
                <div className="space-y-4">
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
                      Please complete your health profile to access all
                      features.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                Quick Actions
              </h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition duration-200 flex items-center justify-center">
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
                  View History
                </button>
                <button className="w-full bg-purple-500 text-white py-3 px-4 rounded-lg hover:bg-purple-600 transition duration-200 flex items-center justify-center">
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
                  Get Suggestions
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Profile Form or Daily Data Input Form */}
          <div className="lg:col-span-2">
            {!profile?.profile_completed ? (
              // Profile Completion Form
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                  Complete Your Health Profile
                </h2>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-center">
                    <svg
                      className="h-5 w-5 text-blue-400 mr-2"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <p className="text-blue-700">
                      Please complete your profile to unlock daily data tracking
                      and health suggestions.
                    </p>
                  </div>
                </div>

                {profileSubmitMessage && (
                  <div
                    className={`p-4 rounded-lg mb-6 ${
                      profileSubmitMessage.includes("Error") ||
                      profileSubmitMessage.includes("error")
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-green-50 text-green-700 border border-green-200"
                    }`}
                  >
                    {profileSubmitMessage}
                  </div>
                )}

                <form onSubmit={handleSubmitProfile} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Birth Date *
                      </label>
                      <input
                        type="date"
                        name="birth_date"
                        value={profileData.birth_date}
                        onChange={handleProfileInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Initial Height (cm) *
                      </label>
                      <input
                        type="number"
                        name="initial_height"
                        value={profileData.initial_height}
                        onChange={handleProfileInputChange}
                        placeholder="Enter your height"
                        step="0.1"
                        min="50"
                        max="300"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Initial Weight (kg) *
                      </label>
                      <input
                        type="number"
                        name="initial_weight"
                        value={profileData.initial_weight}
                        onChange={handleProfileInputChange}
                        placeholder="Enter your weight"
                        step="0.1"
                        min="20"
                        max="500"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-medium text-gray-800 mb-2">
                      Why do we need this information?
                    </h3>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>
                        • <strong>Birth Date:</strong> To calculate your age and
                        provide age-appropriate health suggestions
                      </li>
                      <li>
                        • <strong>Height & Weight:</strong> To track your health
                        progress and calculate BMI trends
                      </li>
                      <li>
                        • <strong>Privacy:</strong> This information is stored
                        securely and used only for your health tracking
                      </li>
                    </ul>
                  </div>

                  <div className="pt-4">
                    <button
                      type="submit"
                      disabled={profileSubmitLoading}
                      className={`w-full py-3 px-4 rounded-lg text-white font-medium transition duration-200 ${
                        profileSubmitLoading
                          ? "bg-gray-400 cursor-not-allowed"
                          : "bg-blue-500 hover:bg-blue-600"
                      }`}
                    >
                      {profileSubmitLoading
                        ? "Completing Profile..."
                        : "Complete Profile"}
                    </button>
                  </div>
                </form>
              </div>
            ) : (
              // Daily Data Input Form (existing form)
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                  Daily Health Data Entry
                </h2>

                {submitMessage && (
                  <div
                    className={`p-4 rounded-lg mb-6 ${
                      submitMessage.includes("Error") ||
                      submitMessage.includes("error")
                        ? "bg-red-50 text-red-700 border border-red-200"
                        : "bg-green-50 text-green-700 border border-green-200"
                    }`}
                  >
                    {submitMessage}
                  </div>
                )}

                <form onSubmit={handleSubmitDailyData} className="space-y-6">
                  {/* Date and Physical Measurements */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date
                      </label>
                      <input
                        type="date"
                        name="date"
                        value={formData.date}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Height (cm)
                      </label>
                      <input
                        type="number"
                        name="height"
                        value={formData.height}
                        onChange={handleInputChange}
                        placeholder="Enter height"
                        step="0.1"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Weight (kg)
                      </label>
                      <input
                        type="number"
                        name="weight"
                        value={formData.weight}
                        onChange={handleInputChange}
                        placeholder="Enter weight"
                        step="0.1"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        required
                      />
                    </div>
                  </div>

                  {/* Meals Section */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-800 border-b pb-2">
                      Daily Meals
                    </h3>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Breakfast
                      </label>
                      <textarea
                        name="breakfast"
                        value={formData.breakfast}
                        onChange={handleInputChange}
                        placeholder="Describe your breakfast..."
                        rows="3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Lunch
                      </label>
                      <textarea
                        name="lunch"
                        value={formData.lunch}
                        onChange={handleInputChange}
                        placeholder="Describe your lunch..."
                        rows="3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Dinner
                      </label>
                      <textarea
                        name="dinner"
                        value={formData.dinner}
                        onChange={handleInputChange}
                        placeholder="Describe your dinner..."
                        rows="3"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-black"
                        required
                      />
                    </div>
                  </div>

                  {/* Submit Button */}
                  <div className="pt-4">
                    <button
                      type="submit"
                      disabled={submitLoading}
                      className={`w-full py-3 px-4 rounded-lg text-white font-medium transition duration-200 ${
                        submitLoading
                          ? "bg-gray-400 cursor-not-allowed"
                          : "bg-green-500 hover:bg-green-600"
                      }`}
                    >
                      {submitLoading ? "Submitting..." : "Submit Daily Data"}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;

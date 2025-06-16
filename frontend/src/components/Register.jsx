import React, { useState } from "react";

const Register = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (formData.password !== formData.confirmPassword) {
      setError("Password confirmation does not match");
      return false;
    }
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long");
      return false;
    }
    if (!formData.email.includes("@")) {
      setError("Please enter a valid email address");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Show success toast
        const toast = document.createElement("div");
        toast.className = "toast toast-top toast-center z-50";
        toast.innerHTML = `
          <div class="alert alert-success shadow-lg">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>Registration successful! Please sign in</span>
            </div>
          </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => {
          if (document.body.contains(toast)) {
            document.body.removeChild(toast);
          }
        }, 3000);

        onSwitchToLogin();
      } else {
        setError(data.error || "Registration failed");
      }
    } catch (err) {
      setError("Network error, please try again later");
      console.error("Register error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center p-4 transition-all duration-500">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full mb-4 transform transition-all duration-300 hover:scale-110 hover:shadow-lg">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-8 w-8 text-white transition-transform duration-300"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 transition-all duration-300">
            Health Tracker
          </h1>
          <p className="text-gray-600 transition-all duration-300">
            Start your health journey
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 transform transition-all duration-500 hover:shadow-2xl animate-fade-in-up">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2 transition-all duration-300">
              Create new account
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="transition-all duration-300">
              <label className="block text-sm font-medium text-gray-700 mb-2 transition-colors duration-200">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="your@email.com"
                required
                disabled={loading}
              />
            </div>

            <div className="transition-all duration-300">
              <label className="block text-sm font-medium text-gray-700 mb-2 transition-colors duration-200">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="Enter username"
                required
                disabled={loading}
              />
            </div>

            <div className="transition-all duration-300">
              <label className="block text-sm font-medium text-gray-700 mb-2 transition-colors duration-200">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="At least 6 characters"
                required
                disabled={loading}
                minLength={6}
              />
            </div>

            <div className="transition-all duration-300">
              <label className="block text-sm font-medium text-gray-700 mb-2 transition-colors duration-200">
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="Re-enter password"
                required
                disabled={loading}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg animate-shake transition-all duration-300">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 px-4 rounded-lg hover:from-purple-600 hover:to-pink-600 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] hover:shadow-lg active:scale-[0.98]"
            >
              <span
                className={`transition-all duration-200 ${
                  loading ? "opacity-0" : "opacity-100"
                }`}
              >
                {loading ? "Creating..." : "Create Account"}
              </span>
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent border-solid rounded-full animate-spin"></div>
                  <span className="ml-2">Creating...</span>
                </div>
              )}
            </button>
          </form>

          <div className="mt-8 text-center transition-all duration-300">
            <p className="text-gray-600 transition-colors duration-200">
              Already have an account?{" "}
              <button
                type="button"
                onClick={onSwitchToLogin}
                className="text-purple-600 hover:text-purple-700 font-medium transition-all duration-200 hover:underline transform hover:scale-105"
                disabled={loading}
              >
                Sign in now
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;

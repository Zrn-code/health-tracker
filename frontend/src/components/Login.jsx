import React, { useState } from "react";

const Login = ({ onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem("access_token", data.access_token);
        localStorage.setItem("user_id", data.user_id);

        // Show success toast
        const toast = document.createElement("div");
        toast.className = "toast toast-top toast-center";
        toast.innerHTML = `
          <div class="alert alert-success">
            <span>Login successful!</span>
          </div>
        `;
        document.body.appendChild(toast);
        setTimeout(() => document.body.removeChild(toast), 3000);

        console.log("Login successful:", data);
      } else {
        setError(data.error || "Login failed");
      }
    } catch (err) {
      setError("Network error, please try again later");
      console.error("Login error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 transition-all duration-500">
      <div className="w-full max-w-md">
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full mb-4 transform transition-all duration-300 hover:scale-110 hover:shadow-lg">
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
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2 transition-all duration-300">
            Health Tracker
          </h1>
          <p className="text-gray-600 transition-all duration-300">
            Welcome back
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 transform transition-all duration-500 hover:shadow-2xl animate-fade-in-up">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2 transition-all duration-300">
              Sign in to your account
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="transition-all duration-300">
              <label className="block text-sm font-medium text-gray-700 mb-2 transition-colors duration-200">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="Enter your username"
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 transform focus:scale-[1.02] hover:shadow-md text-black"
                placeholder="Enter your password"
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
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] hover:shadow-lg active:scale-[0.98] relative"
            >
              <span
                className={`transition-all duration-200 ${
                  loading ? "opacity-0" : "opacity-100"
                }`}
              >
                {loading ? "Signing in..." : "Sign In"}
              </span>
              {loading && (
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent border-solid rounded-full animate-spin"></div>
                  <span className="ml-2">Signing in...</span>
                </div>
              )}
            </button>
          </form>

          <div className="mt-8 text-center transition-all duration-300">
            <p className="text-gray-600 transition-colors duration-200">
              Don't have an account?{" "}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-blue-600 hover:text-blue-700 font-medium transition-all duration-200 hover:underline transform hover:scale-105"
                disabled={loading}
              >
                Sign up now
              </button>
            </p>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes shake {
          0%,
          100% {
            transform: translateX(0);
          }
          25% {
            transform: translateX(-5px);
          }
          75% {
            transform: translateX(5px);
          }
        }

        .animate-fade-in-up {
          animation: fade-in-up 0.6s ease-out;
        }

        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
};

export default Login;

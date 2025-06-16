import React, { useState, useEffect } from "react";

const HistoryView = ({ onBack, onLogout }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [entriesPerPage] = useState(10);
  const [sortBy, setSortBy] = useState("date");
  const [sortOrder, setSortOrder] = useState("desc");
  const [dateFilter, setDateFilter] = useState("");

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        onLogout();
        return;
      }

      const response = await fetch(
        "http://localhost:5000/api/health/daily-entries",
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEntries(data.data || []);
      } else if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("userId");
        onLogout();
      } else {
        setError("Failed to load history");
      }
    } catch (error) {
      console.error("Error fetching history:", error);
      setError("Network error");
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("asc");
    }
  };

  const filteredAndSortedEntries = entries
    .filter((entry) => {
      if (!dateFilter) return true;
      return entry.date && entry.date.includes(dateFilter);
    })
    .sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];

      if (sortBy === "date") {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }

      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  const indexOfLastEntry = currentPage * entriesPerPage;
  const indexOfFirstEntry = indexOfLastEntry - entriesPerPage;
  const currentEntries = filteredAndSortedEntries.slice(
    indexOfFirstEntry,
    indexOfLastEntry
  );
  const totalPages = Math.ceil(
    filteredAndSortedEntries.length / entriesPerPage
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
        <div className="text-white text-xl">Loading history...</div>
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
            Back to Dashboard
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
                Health History
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

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Date
              </label>
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort by
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
              >
                <option value="date">Date</option>
                <option value="weight">Weight</option>
                <option value="height">Height</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setDateFilter("")}
                className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition duration-200"
              >
                Clear Filter
              </button>
            </div>
          </div>
          <div className="mt-4 text-sm text-gray-600">
            Showing {currentEntries.length} of {filteredAndSortedEntries.length}{" "}
            entries
          </div>
        </div>

        {/* History Table */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {currentEntries.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No entries found
              </h3>
              <p className="text-gray-500">
                Start tracking your daily health data to see your history here.
              </p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort("date")}
                      >
                        <div className="flex items-center">
                          Date
                          {sortBy === "date" && (
                            <svg
                              className={`w-4 h-4 ml-1 ${
                                sortOrder === "asc"
                                  ? "transform rotate-180"
                                  : ""
                              }`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          )}
                        </div>
                      </th>
                      <th
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort("height")}
                      >
                        <div className="flex items-center">
                          Height (cm)
                          {sortBy === "height" && (
                            <svg
                              className={`w-4 h-4 ml-1 ${
                                sortOrder === "asc"
                                  ? "transform rotate-180"
                                  : ""
                              }`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          )}
                        </div>
                      </th>
                      <th
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                        onClick={() => handleSort("weight")}
                      >
                        <div className="flex items-center">
                          Weight (kg)
                          {sortBy === "weight" && (
                            <svg
                              className={`w-4 h-4 ml-1 ${
                                sortOrder === "asc"
                                  ? "transform rotate-180"
                                  : ""
                              }`}
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth="2"
                                d="M19 9l-7 7-7-7"
                              />
                            </svg>
                          )}
                        </div>
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Meals
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {currentEntries.map((entry, index) => (
                      <tr key={entry.id || index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {entry.date
                            ? new Date(entry.date).toLocaleDateString()
                            : "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.height || "N/A"}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {entry.weight || "N/A"}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <div className="space-y-1">
                            <div className="truncate max-w-xs">
                              <span className="font-medium text-orange-600">
                                Breakfast:
                              </span>{" "}
                              {entry.breakfast || "N/A"}
                            </div>
                            <div className="truncate max-w-xs">
                              <span className="font-medium text-green-600">
                                Lunch:
                              </span>{" "}
                              {entry.lunch || "N/A"}
                            </div>
                            <div className="truncate max-w-xs">
                              <span className="font-medium text-purple-600">
                                Dinner:
                              </span>{" "}
                              {entry.dinner || "N/A"}
                            </div>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
                  <div className="flex-1 flex justify-between sm:hidden">
                    <button
                      onClick={() =>
                        setCurrentPage(Math.max(1, currentPage - 1))
                      }
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <button
                      onClick={() =>
                        setCurrentPage(Math.min(totalPages, currentPage + 1))
                      }
                      disabled={currentPage === totalPages}
                      className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        Showing{" "}
                        <span className="font-medium">
                          {indexOfFirstEntry + 1}
                        </span>{" "}
                        to{" "}
                        <span className="font-medium">
                          {Math.min(
                            indexOfLastEntry,
                            filteredAndSortedEntries.length
                          )}
                        </span>{" "}
                        of{" "}
                        <span className="font-medium">
                          {filteredAndSortedEntries.length}
                        </span>{" "}
                        results
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                        <button
                          onClick={() =>
                            setCurrentPage(Math.max(1, currentPage - 1))
                          }
                          disabled={currentPage === 1}
                          className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <svg
                            className="h-5 w-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>

                        {Array.from(
                          { length: Math.min(5, totalPages) },
                          (_, i) => {
                            const pageNumber = i + 1;
                            return (
                              <button
                                key={pageNumber}
                                onClick={() => setCurrentPage(pageNumber)}
                                className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                                  currentPage === pageNumber
                                    ? "z-10 bg-blue-50 border-blue-500 text-blue-600"
                                    : "bg-white border-gray-300 text-gray-500 hover:bg-gray-50"
                                }`}
                              >
                                {pageNumber}
                              </button>
                            );
                          }
                        )}

                        <button
                          onClick={() =>
                            setCurrentPage(
                              Math.min(totalPages, currentPage + 1)
                            )
                          }
                          disabled={currentPage === totalPages}
                          className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <svg
                            className="h-5 w-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </button>
                      </nav>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryView;

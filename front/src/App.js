import React, { useEffect, useState } from "react";
import { Search, Star } from "lucide-react";

const Dashboard = () => {
   const [subscriptions, setSubscriptions] = useState([]);
   const [user, setUser] = useState(null);
   useEffect(() => {
    fetch("/api/subscriptions", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => setSubscriptions(data))
      .catch((err) => {
        console.error(err);
      });

    fetch("/api/user", {
      method: "GET",
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then((data) => setUser(data))
      .catch((err) => {
        console.error(err);
      });
  }, []);


  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      {/* Top Bar */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Search className="text-white" />
          <input
            type="text"
            placeholder="Search subscriptions..."
            className="bg-gray-800 border-none text-white p-2 rounded"
          />
        </div>
        {user && (
            <div className="flex items-center space-x-2">
              <span className="text-sm">{user.name}</span>
              <img
                src={user.image || "/static/images/default-avatar.png"}
                alt="User Avatar"
                className="rounded-full w-10 h-10"
              />
            </div>
          )}
      </div>

      {/* Subscriptions Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {subscriptions.map((sub) => (
          <div key={sub.id} className="bg-gray-800 rounded shadow-md">
            <div className="p-4 flex space-x-4">
              <img
                src={sub.image}
                alt={sub.title}
                className="w-24 h-36 object-cover rounded"
              />
              <div className="flex-1">
                <h2 className="text-lg font-semibold mb-1">{sub.title}</h2>
                <p className="text-sm text-gray-400 mb-2">{sub.type}</p>
                <p className="text-sm mb-2">{sub.progress}</p>
                <div className="flex justify-between items-center">
                  <button className="text-sm bg-gray-600 px-2 py-1 rounded hover:bg-gray-500">
                    Update
                  </button>
                  <Star className="text-yellow-400 cursor-pointer" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;

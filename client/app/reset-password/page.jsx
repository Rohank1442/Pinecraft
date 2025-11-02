"use client";
import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const { error } = await supabase.auth.updateUser({ password });
    if (error) return setError(error.message);

    setSuccess(true);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <form className="bg-white p-8 rounded-xl shadow-md w-96 border border-gray-300" onSubmit={handleSubmit}>
        <h2 className="text-2xl font-semibold mb-6 text-center text-black">Reset Password</h2>

        {success ? (
          <p className="text-green-600 text-center">✅ Password updated successfully! You can now log in.</p>
        ) : (
          <>
            <label className="block mb-2 text-sm font-medium text-black">New Password</label>
            <input
              type="password"
              placeholder="Enter new password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full mb-4 p-2 border border-gray-300 rounded text-black"
            />
            {error && <p className="text-red-600 text-center mb-2">{error}</p>}
            <button type="submit" className="w-full py-2 rounded font-medium text-white bg-blue-600 hover:bg-blue-700">
              Update Password
            </button>
          </>
        )}
      </form>
    </div>
  );
}

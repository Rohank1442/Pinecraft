"use client";
import { useState } from "react";
import Link from "next/link";

export default function AuthForm({ type, onSubmit }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  // Password must be alphanumeric and at least 8 characters
  const validatePassword = (pwd) => {
    const regex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
    return regex.test(pwd);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (type === "register") {
      if (password !== confirm) {
        setError("Passwords do not match");
        return;
      }
      if (!validatePassword(password)) {
        setError(
          "Password must be at least 8 characters long and contain both letters and numbers."
        );
        return;
      }
    }

    onSubmit(email, password);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-md w-96 border border-gray-300"
      >
        <h2 className="text-3xl font-semibold mb-6 text-center text-black">
          {type === "login" ? "Login" : "Create Account"}
        </h2>

        {error && (
          <p className="text-red-600 text-sm text-center mb-4">{error}</p>
        )}

        {/* Email */}
        <label className="block mb-2 text-sm font-medium text-black">
          Email
        </label>
        <input
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full mb-4 p-2 border border-gray-300 rounded text-black placeholder-gray-500"
        />

        {/* Password */}
        <label className="block mb-2 text-sm font-medium text-black">
          Password
        </label>
        <input
          type="password"
          placeholder="********"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full mb-4 p-2 border border-gray-300 rounded text-black placeholder-gray-500"
        />

        {/* Confirm Password (only for register) */}
        {type === "register" && (
          <>
            <label className="block mb-2 text-sm font-medium text-black">
              Confirm Password
            </label>
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              className="w-full mb-4 p-2 border border-gray-300 rounded text-black placeholder-gray-500"
            />
          </>
        )}

        {/* Submit button */}
        <button
          type="submit"
          className={`w-full py-2 rounded font-medium text-white transition-colors duration-200 ${
            type === "login"
              ? "bg-blue-600 hover:bg-blue-700"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {type === "login" ? "Login" : "Register"}
        </button>

        {/* Forgot password (only on login) */}
        {type === "login" && (
          <div className="mt-4 text-center">
            <Link
              href="/forgot-password"
              className="text-blue-600 hover:underline text-sm font-medium"
            >
              Forgot Password?
            </Link>
          </div>
        )}

        {/* Toggle link between login/register */}
        <div className="mt-6 text-center">
          {type === "login" ? (
            <p className="text-black text-sm">
              Don’t have an account?{" "}
              <Link href="/register" className="text-blue-600 hover:underline">
                Sign up
              </Link>
            </p>
          ) : (
            <p className="text-black text-sm">
              Already have an account?{" "}
              <Link href="/login" className="text-blue-600 hover:underline">
                Login
              </Link>
            </p>
          )}
        </div>
      </form>
    </div>
  );
}

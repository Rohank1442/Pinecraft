"use client";
import { useState } from "react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("http://localhost:5000/forgot-password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
  
    if (res.ok) setSent(true);
  };
  

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-md w-96 border border-gray-300"
      >
        <h2 className="text-2xl font-semibold mb-6 text-center text-black">
          Forgot Password
        </h2>

        {sent ? (
          <p className="text-green-600 text-center">
            If an account exists, a reset link will be sent to {email}.
          </p>
        ) : (
          <>
            <label className="block mb-2 text-sm font-medium text-black">
              Enter your email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full mb-4 p-2 border border-gray-300 rounded text-black"
            />

            <button
              type="submit"
              className="w-full py-2 rounded font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Send Reset Link
            </button>
          </>
        )}
      </form>
    </div>
  );
}

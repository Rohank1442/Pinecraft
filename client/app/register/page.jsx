"use client";
import { registerUser } from "@/lib/api";
import AuthForm from "@/components/AuthForm";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const router = useRouter();

  const handleRegister = async (email, password) => {
    const res = await registerUser(email, password);
    if (res.success) {
      alert("Registration successful!");
      router.push("/login"); // ✅ consistent redirect
    }
    return res;
  };

  return <AuthForm type="register" onSubmit={handleRegister} />;
}

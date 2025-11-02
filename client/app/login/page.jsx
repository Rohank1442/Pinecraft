"use client";
import { loginUser } from "@/lib/api";
import AuthForm from "@/components/AuthForm";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = async (email, password) => {
    const res = await loginUser(email, password);
    if (res.token) {
      localStorage.setItem("token", res.token);
      router.push("/dashboard");
    }
    return res;
  };

  return <AuthForm type="login" onSubmit={handleLogin} />;
}

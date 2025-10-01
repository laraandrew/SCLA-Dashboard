"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const router = useRouter();

  const submit = async (e: any) => {
    e.preventDefault();
    setErr("");
    const r = await fetch("/api/login", { method: "POST", body: JSON.stringify({ password }) });
    if (r.ok) router.push("/");
    else setErr("Incorrect password");
  };

  return (
    <main style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <form onSubmit={submit} style={{ border: "1px solid #ddd", borderRadius: 12, padding: 24, width: 320 }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, marginBottom: 12 }}>SportsCarLA Hub</h1>
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password"
          style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid #ccc" }} />
        <button type="submit" style={{ marginTop: 12, width: "100%", padding: 10, borderRadius: 8, background: "black", color: "white" }}>Enter</button>
        {err && <div style={{ color: "crimson", marginTop: 8 }}>{err}</div>}
      </form>
    </main>
  );
}

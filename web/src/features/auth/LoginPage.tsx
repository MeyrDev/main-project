import { useState } from "react";
import type { FormEvent } from "react";
import { getCurrentUser } from "./api";
import { clearAuthCredentials, setAuthCredentials } from "./authStorage";
import type { CurrentUser } from "./types";
import "./auth.css";

type Props = {
  onLogin: (user: CurrentUser) => void;
};

export function LoginPage({ onLogin }: Props) {
  const [email, setEmail] = useState("admin@risk-crm.local");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    const credentials = {
      email: email.trim(),
      password,
    };

    setAuthCredentials(credentials);

    try {
      const user = await getCurrentUser();
      onLogin(user);
    } catch {
      clearAuthCredentials();
      setError("Invalid email or password");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-panel" onSubmit={handleSubmit}>
        <img src="/favicon.svg" alt="EntityRIsk Analytics logo" />
        <h1>EntityRIsk Analytics</h1>

        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>

        {error && <div className="login-error">{error}</div>}

        <button type="submit" disabled={isLoading}>
          {isLoading ? "Ожидание..." : "Вход"}
        </button>
      </form>
    </main>
  );
}

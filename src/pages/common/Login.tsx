import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Phone, Mail } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { ApiError } from "../../lib/apiClient";
import { Card, PageHeader, Field, Button, inputClass } from "../../components/ui";

type LoginMode = "phone" | "email";

export default function Login() {
  const navigate = useNavigate();
  const { loginWithIdentifier, user } = useAuth();
  const [mode, setMode] = React.useState<LoginMode>("phone");
  const [identifier, setIdentifier] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (user) navigate(user.role === "buyer" ? "/buyer" : "/farmer");
  }, [user, navigate]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await loginWithIdentifier(identifier.trim(), password);
      // navigation happens via the effect above once `user` updates
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not log in. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <PageHeader title="Log in" description="Access your Fasal account." />
      <Card className="p-5">
        <div className="flex gap-1 mb-5 bg-stone-100 rounded-lg p-1">
          <button
            type="button"
            onClick={() => {
              setMode("phone");
              setIdentifier("");
              setError(null);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === "phone" ? "bg-white shadow-sm text-stone-900" : "text-stone-500"
            }`}
          >
            <Phone size={14} /> Phone Number
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("email");
              setIdentifier("");
              setError(null);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === "email" ? "bg-white shadow-sm text-stone-900" : "text-stone-500"
            }`}
          >
            <Mail size={14} /> Email / Username
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "phone" ? (
            <Field label="Phone Number" required>
              <input
                type="tel"
                inputMode="tel"
                className={inputClass}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="e.g. 9876543210"
                autoComplete="tel"
              />
            </Field>
          ) : (
            <Field label="Email or Username" required>
              <input
                type="text"
                className={inputClass}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                placeholder="you@example.com"
                autoComplete="username"
              />
            </Field>
          )}

          <Field label="Password" required>
            <input
              type="password"
              className={inputClass}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </Field>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Logging in..." : "Log in"}
          </Button>
        </form>

        <p className="text-sm text-stone-500 text-center mt-5">
          New here?{" "}
          <Link to="/register" className="text-green-700 font-medium hover:underline">
            Create an account
          </Link>
        </p>
      </Card>
    </div>
  );
}

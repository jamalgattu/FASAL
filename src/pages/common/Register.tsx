import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sprout, ShoppingCart } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { ApiError } from "../../lib/apiClient";
import { Card, PageHeader, Field, Button, inputClass } from "../../components/ui";

type Role = "farmer" | "buyer";

const BUYER_TYPES = [
  { value: "retail_chain", label: "Retail Chain" },
  { value: "institutional", label: "Institutional" },
  { value: "wholesaler", label: "Wholesaler" },
  { value: "processor", label: "Processor" },
] as const;

export default function Register() {
  const navigate = useNavigate();
  const { registerFarmer, registerBuyer, user } = useAuth();
  const [role, setRole] = React.useState<Role>("farmer");
  const [error, setError] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  const [form, setForm] = React.useState({
    email: "",
    password: "",
    fullName: "",
    phone: "",
    district: "",
    state: "Uttar Pradesh",
    lat: "26.85",
    lng: "80.95",
    // farmer-only
    isFpo: false,
    orgName: "",
    village: "",
    // buyer-only
    buyerType: "retail_chain" as (typeof BUYER_TYPES)[number]["value"],
  });

  React.useEffect(() => {
    if (user) navigate(user.role === "buyer" ? "/buyer" : "/farmer");
  }, [user, navigate]);

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const common = {
        email: form.email.trim(),
        password: form.password,
        fullName: form.fullName.trim(),
        phone: form.phone.trim() || undefined,
        district: form.district.trim(),
        state: form.state.trim(),
        lat: Number(form.lat),
        lng: Number(form.lng),
      };
      if (role === "farmer") {
        await registerFarmer({
          ...common,
          isFpo: form.isFpo,
          orgName: form.orgName.trim() || undefined,
          village: form.village.trim() || undefined,
        });
      } else {
        await registerBuyer({
          ...common,
          buyerType: form.buyerType,
          orgName: form.orgName.trim() || form.fullName.trim(),
        });
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create your account. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <PageHeader title="Create an account" description="Join as a Farmer/FPO or as a Buyer." />
      <Card className="p-5">
        <div className="flex gap-1 mb-5 bg-stone-100 rounded-lg p-1">
          <button
            type="button"
            onClick={() => setRole("farmer")}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
              role === "farmer" ? "bg-white shadow-sm text-stone-900" : "text-stone-500"
            }`}
          >
            <Sprout size={14} /> Farmer / FPO
          </button>
          <button
            type="button"
            onClick={() => setRole("buyer")}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-md text-sm font-medium transition-colors ${
              role === "buyer" ? "bg-white shadow-sm text-stone-900" : "text-stone-500"
            }`}
          >
            <ShoppingCart size={14} /> Buyer
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Field label="Full Name" required>
            <input className={inputClass} value={form.fullName} onChange={(e) => update("fullName", e.target.value)} />
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Email" required>
              <input
                type="email"
                className={inputClass}
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
              />
            </Field>
            <Field label="Phone" hint="For phone login">
              <input
                type="tel"
                className={inputClass}
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
              />
            </Field>
          </div>

          <Field label="Password" required hint="At least 8 characters">
            <input
              type="password"
              className={inputClass}
              value={form.password}
              onChange={(e) => update("password", e.target.value)}
              minLength={8}
            />
          </Field>

          {role === "farmer" ? (
            <>
              <Field label="Account Type" required>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => update("isFpo", false)}
                    className={`flex-1 py-2 rounded-lg border text-sm font-medium ${
                      !form.isFpo ? "border-green-700 bg-green-50 text-green-800" : "border-stone-300 text-stone-500"
                    }`}
                  >
                    Individual Farmer
                  </button>
                  <button
                    type="button"
                    onClick={() => update("isFpo", true)}
                    className={`flex-1 py-2 rounded-lg border text-sm font-medium ${
                      form.isFpo ? "border-green-700 bg-green-50 text-green-800" : "border-stone-300 text-stone-500"
                    }`}
                  >
                    FPO
                  </button>
                </div>
              </Field>
              {form.isFpo && (
                <Field label="FPO / Organization Name">
                  <input className={inputClass} value={form.orgName} onChange={(e) => update("orgName", e.target.value)} />
                </Field>
              )}
              <Field label="Village">
                <input className={inputClass} value={form.village} onChange={(e) => update("village", e.target.value)} />
              </Field>
            </>
          ) : (
            <>
              <Field label="Organization Name" required>
                <input className={inputClass} value={form.orgName} onChange={(e) => update("orgName", e.target.value)} />
              </Field>
              <Field label="Buyer Type" required>
                <select className={inputClass} value={form.buyerType} onChange={(e) => update("buyerType", e.target.value as any)}>
                  {BUYER_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </Field>
            </>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Field label="District" required>
              <input className={inputClass} value={form.district} onChange={(e) => update("district", e.target.value)} />
            </Field>
            <Field label="State" required>
              <input className={inputClass} value={form.state} onChange={(e) => update("state", e.target.value)} />
            </Field>
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Creating account..." : "Create account"}
          </Button>
        </form>

        <p className="text-sm text-stone-500 text-center mt-5">
          Already have an account?{" "}
          <Link to="/login" className="text-green-700 font-medium hover:underline">
            Log in
          </Link>
        </p>
      </Card>
    </div>
  );
}

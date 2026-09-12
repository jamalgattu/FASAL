import React from "react";
import { useNavigate } from "react-router-dom";
import { farmerService } from "../../services/farmerService";
import { QualityGrade, Unit } from "../../types";
import { Card, Field, PageHeader, Button, inputClass } from "../../components/ui";

const CROPS = ["Potato", "Wheat", "Onion", "Tomato", "Maize", "Rice", "Sugarcane", "Mustard"];

export default function AddProduce() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = React.useState(false);
  const [form, setForm] = React.useState({
    crop: CROPS[0],
    variety: "",
    quantity: "",
    unit: "kg" as Unit,
    expectedPrice: "",
    harvestDate: "",
    availableDate: "",
    village: "",
    district: "",
    state: "Uttar Pradesh",
    qualityGrade: "A" as QualityGrade,
    notes: "",
  });

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    await farmerService.createListing({
      crop: form.crop,
      variety: form.variety || "Local",
      quantity: Number(form.quantity) || 0,
      unit: form.unit,
      expectedPrice: Number(form.expectedPrice) || 0,
      harvestDate: form.harvestDate,
      availableDate: form.availableDate,
      location: {
        village: form.village || undefined,
        district: form.district || "Sitapur",
        state: form.state,
        lat: 27.71,
        lng: 80.78,
      },
      qualityGrade: form.qualityGrade,
      notes: form.notes || undefined,
    });
    setSubmitting(false);
    navigate("/farmer/listings");
  }

  return (
    <div className="max-w-2xl">
      <PageHeader title="Add Produce" description="Fill in the details of your crop. This will be visible to verified buyers." />
      <Card className="p-5">
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Crop" required>
              <select className={inputClass} value={form.crop} onChange={(e) => update("crop", e.target.value)}>
                {CROPS.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Variety" hint="e.g. Kufri Jyoti, HD-2967">
              <input
                className={inputClass}
                value={form.variety}
                onChange={(e) => update("variety", e.target.value)}
                placeholder="Enter variety"
              />
            </Field>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Quantity" required>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.quantity}
                onChange={(e) => update("quantity", e.target.value)}
                placeholder="e.g. 5000"
              />
            </Field>
            <Field label="Unit" required>
              <select className={inputClass} value={form.unit} onChange={(e) => update("unit", e.target.value as Unit)}>
                <option value="kg">kg</option>
                <option value="quintal">quintal</option>
                <option value="tonne">tonne</option>
              </select>
            </Field>
            <Field label="Expected Price (₹/unit)" required>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.expectedPrice}
                onChange={(e) => update("expectedPrice", e.target.value)}
                placeholder="e.g. 14"
              />
            </Field>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Harvest Date" required>
              <input
                type="date"
                className={inputClass}
                value={form.harvestDate}
                onChange={(e) => update("harvestDate", e.target.value)}
              />
            </Field>
            <Field label="Available From" required hint="When it will be ready for pickup">
              <input
                type="date"
                className={inputClass}
                value={form.availableDate}
                onChange={(e) => update("availableDate", e.target.value)}
              />
            </Field>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Village">
              <input className={inputClass} value={form.village} onChange={(e) => update("village", e.target.value)} />
            </Field>
            <Field label="District" required>
              <input className={inputClass} value={form.district} onChange={(e) => update("district", e.target.value)} />
            </Field>
            <Field label="State" required>
              <input className={inputClass} value={form.state} onChange={(e) => update("state", e.target.value)} />
            </Field>
          </div>

          <Field label="Quality Grade" required hint="Grade A = best quality, C = lower quality">
            <div className="flex gap-2">
              {(["A", "B", "C"] as QualityGrade[]).map((g) => (
                <button
                  type="button"
                  key={g}
                  onClick={() => update("qualityGrade", g)}
                  className={`w-12 h-12 rounded-lg border-2 font-semibold transition-colors ${
                    form.qualityGrade === g
                      ? "border-green-700 bg-green-50 text-green-800"
                      : "border-stone-300 text-stone-500 hover:border-stone-400"
                  }`}
                  aria-pressed={form.qualityGrade === g}
                >
                  {g}
                </button>
              ))}
            </div>
          </Field>

          <Field label="Notes (optional)">
            <textarea
              className={inputClass}
              rows={3}
              value={form.notes}
              onChange={(e) => update("notes", e.target.value)}
              placeholder="Any extra information for buyers"
            />
          </Field>

          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Saving..." : "List My Produce"}
            </Button>
            <Button type="button" variant="secondary" onClick={() => navigate(-1)}>
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}

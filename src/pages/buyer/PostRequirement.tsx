import React from "react";
import { useNavigate } from "react-router-dom";
import { buyerService } from "../../services/buyerService";
import { QualityGrade, Unit } from "../../types";
import { Card, Field, PageHeader, Button, inputClass } from "../../components/ui";

const CROPS = ["Potato", "Wheat", "Onion", "Tomato", "Maize", "Rice", "Sugarcane", "Mustard"];
const BUYER_TYPES = ["Institutional", "Wholesaler", "Retail Chain", "Processor"] as const;

export default function PostRequirement() {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = React.useState(false);
  const [form, setForm] = React.useState({
    crop: CROPS[0],
    variety: "",
    requiredQuantity: "",
    unit: "kg" as Unit,
    acceptablePrice: "",
    requiredQuality: "A" as QualityGrade,
    deliveryDistrict: "",
    deliveryState: "Uttar Pradesh",
    requiredDeliveryDate: "",
    buyerType: "Retail Chain" as (typeof BUYER_TYPES)[number],
  });

  function update<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    await buyerService.createRequirement({
      crop: form.crop,
      variety: form.variety || "Any",
      requiredQuantity: Number(form.requiredQuantity) || 0,
      unit: form.unit,
      acceptablePrice: Number(form.acceptablePrice) || 0,
      requiredQuality: form.requiredQuality,
      deliveryLocation: {
        district: form.deliveryDistrict || "Lucknow",
        state: form.deliveryState,
        lat: 26.85,
        lng: 80.95,
      },
      requiredDeliveryDate: form.requiredDeliveryDate,
      buyerType: form.buyerType,
    });
    setSubmitting(false);
    navigate("/buyer/requirements");
  }

  return (
    <div className="max-w-2xl">
      <PageHeader title="Post Requirement" description="Tell farmers and FPOs what you need. Verified matches will be shown to you automatically." />
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
            <Field label="Preferred Variety" hint="Leave blank if flexible">
              <input className={inputClass} value={form.variety} onChange={(e) => update("variety", e.target.value)} />
            </Field>
          </div>

          <div className="grid sm:grid-cols-3 gap-4">
            <Field label="Required Quantity" required>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.requiredQuantity}
                onChange={(e) => update("requiredQuantity", e.target.value)}
              />
            </Field>
            <Field label="Unit" required>
              <select className={inputClass} value={form.unit} onChange={(e) => update("unit", e.target.value as Unit)}>
                <option value="kg">kg</option>
                <option value="quintal">quintal</option>
                <option value="tonne">tonne</option>
              </select>
            </Field>
            <Field label="Acceptable Price (₹/unit)" required>
              <input
                type="number"
                min={0}
                className={inputClass}
                value={form.acceptablePrice}
                onChange={(e) => update("acceptablePrice", e.target.value)}
              />
            </Field>
          </div>

          <Field label="Required Quality Grade" required>
            <div className="flex gap-2">
              {(["A", "B", "C"] as QualityGrade[]).map((g) => (
                <button
                  type="button"
                  key={g}
                  onClick={() => update("requiredQuality", g)}
                  className={`w-12 h-12 rounded-lg border-2 font-semibold transition-colors ${
                    form.requiredQuality === g
                      ? "border-green-700 bg-green-50 text-green-800"
                      : "border-stone-300 text-stone-500 hover:border-stone-400"
                  }`}
                  aria-pressed={form.requiredQuality === g}
                >
                  {g}
                </button>
              ))}
            </div>
          </Field>

          <div className="grid sm:grid-cols-2 gap-4">
            <Field label="Delivery District" required>
              <input
                className={inputClass}
                value={form.deliveryDistrict}
                onChange={(e) => update("deliveryDistrict", e.target.value)}
              />
            </Field>
            <Field label="Delivery State" required>
              <input className={inputClass} value={form.deliveryState} onChange={(e) => update("deliveryState", e.target.value)} />
            </Field>
          </div>

          <Field label="Required Delivery Date" required>
            <input
              type="date"
              className={inputClass}
              value={form.requiredDeliveryDate}
              onChange={(e) => update("requiredDeliveryDate", e.target.value)}
            />
          </Field>

          <Field label="Buyer Type" required>
            <select className={inputClass} value={form.buyerType} onChange={(e) => update("buyerType", e.target.value as any)}>
              {BUYER_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </Field>

          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={submitting}>
              {submitting ? "Posting..." : "Post Requirement"}
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

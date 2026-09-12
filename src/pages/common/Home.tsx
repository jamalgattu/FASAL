import React from "react";
import { Sprout, ShoppingCart, Truck, BarChart3, ArrowRight } from "lucide-react";
import { LinkButton, Card } from "../../components/ui";

const CARDS = [
  {
    to: "/farmer",
    icon: <Sprout size={22} className="text-green-700" />,
    title: "Farmer / FPO",
    description: "List your produce and find matched buyers near you.",
  },
  {
    to: "/buyer",
    icon: <ShoppingCart size={22} className="text-blue-700" />,
    title: "Buyer",
    description: "Post requirements and source directly from verified FPOs.",
  },
  {
    to: "/logistics",
    icon: <Truck size={22} className="text-amber-700" />,
    title: "Logistics",
    description: "View pickup/delivery routes and vehicle utilization.",
  },
  {
    to: "/impact",
    icon: <BarChart3 size={22} className="text-stone-700" />,
    title: "Impact Analytics",
    description: "Track outcomes across the supply chain.",
  },
];

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto text-center py-6">
      <h1 className="text-2xl sm:text-3xl font-semibold text-stone-900">AgriSetu</h1>
      <p className="text-stone-500 mt-2 max-w-xl mx-auto">
        A coordination platform connecting Farmers/FPOs, verified bulk buyers, and logistics
        providers — with supply-demand matching and route planning. Built as an SIH prototype;
        this is not a replacement for e-NAM and does not claim to remove all intermediaries.
      </p>

      <div className="grid sm:grid-cols-2 gap-4 mt-8 text-left">
        {CARDS.map((c) => (
          <Card key={c.to} className="p-5">
            <div className="flex items-center gap-3 mb-2">
              {c.icon}
              <h2 className="font-semibold text-stone-900">{c.title}</h2>
            </div>
            <p className="text-sm text-stone-500 mb-4">{c.description}</p>
            <LinkButton to={c.to} variant="secondary" className="w-full">
              Continue as {c.title} <ArrowRight size={15} />
            </LinkButton>
          </Card>
        ))}
      </div>
    </div>
  );
}

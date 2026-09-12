import React from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import { Sprout, ShoppingCart, Truck, BarChart3, Menu, X } from "lucide-react";

type RoleKey = "farmer" | "buyer" | "logistics" | "impact";

const ROLE_TABS: { key: RoleKey; label: string; to: string; icon: React.ReactNode }[] = [
  { key: "farmer", label: "Farmer / FPO", to: "/farmer", icon: <Sprout size={16} /> },
  { key: "buyer", label: "Buyer", to: "/buyer", icon: <ShoppingCart size={16} /> },
  { key: "logistics", label: "Logistics", to: "/logistics", icon: <Truck size={16} /> },
  { key: "impact", label: "Impact", to: "/impact", icon: <BarChart3 size={16} /> },
];

const SUB_NAV: Record<RoleKey, { label: string; to: string }[]> = {
  farmer: [
    { label: "Dashboard", to: "/farmer" },
    { label: "Add Produce", to: "/farmer/add-produce" },
    { label: "My Listings", to: "/farmer/listings" },
    { label: "Buyer Matches", to: "/farmer/matches" },
    { label: "Orders", to: "/farmer/orders" },
  ],
  buyer: [
    { label: "Dashboard", to: "/buyer" },
    { label: "Post Requirement", to: "/buyer/post-requirement" },
    { label: "My Requirements", to: "/buyer/requirements" },
    { label: "Available Supply", to: "/buyer/supply" },
    { label: "Recommended Matches", to: "/buyer/matches" },
    { label: "Orders", to: "/buyer/orders" },
  ],
  logistics: [{ label: "Routes", to: "/logistics" }],
  impact: [{ label: "Impact Dashboard", to: "/impact" }],
};

function activeRole(pathname: string): RoleKey | null {
  if (pathname.startsWith("/farmer")) return "farmer";
  if (pathname.startsWith("/buyer")) return "buyer";
  if (pathname.startsWith("/logistics")) return "logistics";
  if (pathname.startsWith("/impact")) return "impact";
  return null;
}

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const role = activeRole(location.pathname);
  const [mobileNavOpen, setMobileNavOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-stone-50 flex flex-col">
      {/* Brand + role bar */}
      <header className="bg-green-900 text-white sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-semibold tracking-tight">
            <Sprout size={20} className="text-green-300" />
            <span>AgriSetu</span>
            <span className="hidden sm:inline text-green-300 font-normal text-xs ml-1">
              Supply-Chain Coordination
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-1" aria-label="Primary">
            {ROLE_TABS.map((t) => (
              <NavLink
                key={t.key}
                to={t.to}
                className={({ isActive }) =>
                  `flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive || role === t.key
                      ? "bg-green-800 text-white"
                      : "text-green-100 hover:bg-green-800/60"
                  }`
                }
              >
                {t.icon}
                {t.label}
              </NavLink>
            ))}
          </nav>
          <button
            className="md:hidden p-2 rounded-md hover:bg-green-800"
            aria-label={mobileNavOpen ? "Close menu" : "Open menu"}
            onClick={() => setMobileNavOpen((o) => !o)}
          >
            {mobileNavOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {mobileNavOpen && (
          <nav className="md:hidden border-t border-green-800 px-4 py-2 flex flex-col gap-1" aria-label="Primary mobile">
            {ROLE_TABS.map((t) => (
              <NavLink
                key={t.key}
                to={t.to}
                onClick={() => setMobileNavOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2.5 rounded-md text-sm font-medium ${
                    isActive || role === t.key ? "bg-green-800 text-white" : "text-green-100"
                  }`
                }
              >
                {t.icon}
                {t.label}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      {/* Sub navigation for the active role */}
      {role && SUB_NAV[role].length > 1 && (
        <div className="bg-white border-b border-stone-200 sticky top-14 z-20">
          <div className="max-w-6xl mx-auto px-2 sm:px-4">
            <nav className="flex gap-1 overflow-x-auto no-scrollbar py-2" aria-label="Section">
              {SUB_NAV[role].map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === `/${role}`}
                  className={({ isActive }) =>
                    `whitespace-nowrap px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-green-100 text-green-800"
                        : "text-stone-500 hover:bg-stone-100 hover:text-stone-700"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>
      )}

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-5">{children}</main>

      <footer className="text-center text-xs text-stone-400 py-4 border-t border-stone-200 bg-white">
        AgriSetu — SIH Prototype (Problem 26033). Not affiliated with e-NAM. Demo data shown throughout.
      </footer>
    </div>
  );
}

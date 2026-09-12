import React from "react";
import { HashRouter, Routes, Route } from "react-router-dom";
import { Layout } from "./components/Layout";

import Home from "./pages/common/Home";

import FarmerDashboard from "./pages/farmer/Dashboard";
import AddProduce from "./pages/farmer/AddProduce";
import MyListings from "./pages/farmer/MyListings";
import BuyerMatches from "./pages/farmer/BuyerMatches";
import FarmerOrders from "./pages/farmer/Orders";
import FarmerOrderDetails from "./pages/farmer/OrderDetails";

import BuyerDashboard from "./pages/buyer/Dashboard";
import PostRequirement from "./pages/buyer/PostRequirement";
import MyRequirements from "./pages/buyer/MyRequirements";
import AvailableSupply from "./pages/buyer/AvailableSupply";
import RecommendedMatches from "./pages/buyer/RecommendedMatches";
import BuyerOrders from "./pages/buyer/Orders";
import BuyerOrderDetails from "./pages/buyer/OrderDetails";

import LogisticsRoutePage from "./pages/logistics/RoutePage";
import ImpactDashboard from "./pages/analytics/ImpactDashboard";

export default function App() {
  return (
    <HashRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />

          <Route path="/farmer" element={<FarmerDashboard />} />
          <Route path="/farmer/add-produce" element={<AddProduce />} />
          <Route path="/farmer/listings" element={<MyListings />} />
          <Route path="/farmer/matches" element={<BuyerMatches />} />
          <Route path="/farmer/orders" element={<FarmerOrders />} />
          <Route path="/farmer/orders/:id" element={<FarmerOrderDetails />} />

          <Route path="/buyer" element={<BuyerDashboard />} />
          <Route path="/buyer/post-requirement" element={<PostRequirement />} />
          <Route path="/buyer/requirements" element={<MyRequirements />} />
          <Route path="/buyer/supply" element={<AvailableSupply />} />
          <Route path="/buyer/matches" element={<RecommendedMatches />} />
          <Route path="/buyer/orders" element={<BuyerOrders />} />
          <Route path="/buyer/orders/:id" element={<BuyerOrderDetails />} />

          <Route path="/logistics" element={<LogisticsRoutePage />} />
          <Route path="/impact" element={<ImpactDashboard />} />
        </Routes>
      </Layout>
    </HashRouter>
  );
}

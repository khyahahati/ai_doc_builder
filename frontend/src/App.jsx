import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/home.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import CreateProject from "./pages/CreateProject.jsx";
import Workspace from "./pages/Workspace.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateProject />} />
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/workspace/:projectId" element={<Workspace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

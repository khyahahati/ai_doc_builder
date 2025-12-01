import Navbar from "./Navbar.jsx";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen w-full bg-[#0e0f14] text-white">
      <Navbar />
      {children}
    </div>
  );
}

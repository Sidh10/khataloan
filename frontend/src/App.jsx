import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Upload from "./pages/Upload";
import Report from "./pages/Report";

export default function App() {
  return (
    <Router>
      <div style={{ fontFamily: "Inter, Calibri, sans-serif", minHeight: "100vh", background: "#FDF6EC" }}>
        <Routes>
          <Route path="/"           element={<Home />} />
          <Route path="/upload"     element={<Upload />} />
          <Route path="/report/:id" element={<Report />} />
        </Routes>
      </div>
    </Router>
  );
}

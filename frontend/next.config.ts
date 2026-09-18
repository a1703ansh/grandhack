import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Client-only app: static export lets FastAPI serve the built site on a
  // single port for the demo (frontend/out). Dev (`next dev`) is unaffected.
  output: "export",
};

export default nextConfig;

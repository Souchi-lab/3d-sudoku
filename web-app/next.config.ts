import type { NextConfig } from "next";

// GitHub Pages deploys to /3d-sudoku sub-path.
// Vercel / local dev use no basePath.
const isPages = !!process.env.NEXT_PUBLIC_BASE_PATH;

const nextConfig: NextConfig = {
  // Static export — required for GitHub Pages
  ...(isPages && { output: "export" }),
  basePath: process.env.NEXT_PUBLIC_BASE_PATH ?? "",
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH ?? "",
};

export default nextConfig;

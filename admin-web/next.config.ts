import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  trailingSlash: fontConfigTrailingSlash(),
};

function fontConfigTrailingSlash() {
  return true;
}

export default nextConfig;

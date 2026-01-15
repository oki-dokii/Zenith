
/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export', // Required for Electron (static export)
    images: {
        unoptimized: true, // Required for static export
    },
};


export default nextConfig;

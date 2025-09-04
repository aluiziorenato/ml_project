import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteMockServe } from "vite-plugin-mock";

export default defineConfig({
	plugins: [
		react(),
		viteMockServe({
			mockPath: "mock",
		}),
	],
	server: {
		port: 3002,
		proxy: {
			"/api": "http://backend:8000",
			"/detector-tendencias": "http://localhost:8000",
		},
	},
	resolve: {
		alias: {
			"@": "/src",
		},
	},
});

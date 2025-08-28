/// <reference types="vite/client" />

declare interface ImportMetaEnv {
  readonly VITE_BACKEND_URL?: string;
  // outras variáveis de ambiente personalizadas
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv;
}

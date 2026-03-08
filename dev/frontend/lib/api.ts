import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // Mathlib semantic search
  searchMathlib: async (query: string, topK = 5, filterModule?: string) => {
    const { data } = await apiClient.post("/search/mathlib", {
      query,
      top_k: topK,
      filter_module: filterModule,
    });
    return data;
  },

  // Proof generation
  generateProof: async (
    description: string,
    context?: string,
    style: "tactic" | "term" = "tactic",
    autoCompile = true
  ) => {
    const { data } = await apiClient.post("/generate/proof", {
      description,
      context,
      style,
      auto_compile: autoCompile,
    });
    return data;
  },

  // Error diagnosis
  diagnoseError: async (code: string, errorMessage?: string) => {
    const { data } = await apiClient.post("/diagnose/error", {
      code,
      error_message: errorMessage,
    });
    return data;
  },

  // LaTeX to Lean conversion
  latexToLean: async (latex: string, includeImports = false) => {
    const { data } = await apiClient.post("/convert/latex-to-lean", {
      latex,
      include_imports: includeImports,
    });
    return data;
  },

  // Lean to LaTeX conversion
  leanToLatex: async (leanCode: string, format: "inline" | "display" = "display") => {
    const { data } = await apiClient.post("/convert/lean-to-latex", {
      lean_code: leanCode,
      format,
    });
    return data;
  },

  // Compile check
  compileCheck: async (code: string, timeoutSeconds = 60) => {
    const { data } = await apiClient.post("/compile/check", {
      code,
      timeout_seconds: timeoutSeconds,
    });
    return data;
  },

  // Explain tactics
  explainTactics: async (code: string, language: "zh" | "en" = "en") => {
    const { data } = await apiClient.post("/explain/tactics", {
      code,
      language,
    });
    return data;
  },

  // User usage
  getUserUsage: async (period = "current_month") => {
    const { data } = await apiClient.get(`/user/usage?period=${period}`);
    return data;
  },

  // Auth
  login: async (email: string, password: string) => {
    const { data } = await apiClient.post("/auth/login", { email, password });
    return data;
  },

  register: async (email: string, password: string, displayName: string) => {
    const { data } = await apiClient.post("/auth/register", {
      email,
      password,
      display_name: displayName,
    });
    return data;
  },

  // Proof sessions
  getProofSessions: async (page = 1, perPage = 20) => {
    const { data } = await apiClient.get(
      `/proof/sessions?page=${page}&per_page=${perPage}`
    );
    return data;
  },

  createProofSession: async (title: string, description?: string) => {
    const { data } = await apiClient.post("/proof/sessions", {
      title,
      description,
    });
    return data;
  },

  updateProofSession: async (
    sessionId: string,
    updates: { title?: string; current_code?: string }
  ) => {
    const { data } = await apiClient.patch(`/proof/sessions/${sessionId}`, updates);
    return data;
  },

  // Billing
  getSubscription: async () => {
    const { data } = await apiClient.get("/billing/subscription");
    return data;
  },

  createCheckout: async (plan: string, billingCycle: string = "monthly") => {
    const { data } = await apiClient.post(
      `/billing/create-checkout?plan=${plan}&billing_cycle=${billingCycle}`
    );
    return data;
  },

  cancelSubscription: async () => {
    const { data } = await apiClient.post("/billing/cancel");
    return data;
  },
};

export default api;

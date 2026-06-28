const API_BASE = "/api/projects";

export async function createProject(githubUrl, apiKey) {
  const payload = { github_url: githubUrl };
  if (apiKey) payload.gemini_api_key = apiKey;

  const res = await fetch(API_BASE, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

export async function getProjects() {
  const res = await fetch(API_BASE);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function getProject(id) {
  const res = await fetch(`${API_BASE}/${id}`);
  if (!res.ok) throw new Error("Failed to fetch project");
  return res.json();
}

export async function getProjectAnalysis(id) {
  const res = await fetch(`${API_BASE}/${id}/analysis`);
  if (!res.ok) throw new Error("Failed to fetch analysis");
  return res.json();
}

export async function getProjectPrompt(id) {
  const res = await fetch(`${API_BASE}/${id}/prompt`);
  if (!res.ok) throw new Error("Failed to fetch prompt");
  return res.json();
}

export async function regeneratePrompt(id) {
  const res = await fetch(`${API_BASE}/${id}/regenerate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to regenerate prompt");
  return res.json();
}

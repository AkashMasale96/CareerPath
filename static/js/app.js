const STUDENT_KEY = "careerpath_student_id";

let authCache = null;

function getStudentId() {
  return localStorage.getItem(STUDENT_KEY);
}

function setStudentId(id) {
  if (id) localStorage.setItem(STUDENT_KEY, String(id));
  else localStorage.removeItem(STUDENT_KEY);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = data.error || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

async function refreshAuth() {
  try {
    authCache = await api("/api/auth/me");
    setStudentId(authCache.student_id);
    return authCache;
  } catch {
    authCache = null;
    setStudentId(null);
    return null;
  }
}

function syncAuthNav(loggedIn) {
  document.querySelectorAll("[data-nav-guest]").forEach((el) => {
    el.hidden = loggedIn;
  });
  document.querySelectorAll("[data-nav-auth]").forEach((el) => {
    el.hidden = !loggedIn;
  });
}

function redirectLogin() {
  window.location.href = "/login";
}

function redirectUpload() {
  window.location.href = "/upload";
}

async function needLogin() {
  const auth = authCache || (await refreshAuth());
  if (!auth) {
    redirectLogin();
    return null;
  }
  return auth.student_id;
}

async function needScannedProfile() {
  const id = await needLogin();
  if (!id) return null;
  const auth = authCache || (await refreshAuth());
  if (!auth?.resume_scanned) {
    redirectUpload();
    return null;
  }
  return id;
}

function fill(el, html) {
  if (el) el.innerHTML = html;
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function submitLogin(event) {
  event.preventDefault();
  const form = event.target;
  const error = document.getElementById("login-error");
  error.hidden = true;
  try {
    const data = await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: form.email.value,
        password: form.password.value,
      }),
    });
    setStudentId(data.student_id);
    authCache = data;
    window.location.href = data.resume_scanned ? "/dashboard" : "/upload";
  } catch (err) {
    error.hidden = false;
    error.textContent = err.message;
  }
}

async function submitSignup(event) {
  event.preventDefault();
  const form = event.target;
  const error = document.getElementById("signup-error");
  error.hidden = true;
  try {
    const data = await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: form.name.value,
        email: form.email.value,
        password: form.password.value,
      }),
    });
    setStudentId(data.student_id);
    authCache = data;
    window.location.href = "/upload";
  } catch (err) {
    error.hidden = false;
    error.textContent = err.message;
  }
}

async function logout() {
  try {
    await api("/api/auth/logout", { method: "POST" });
  } catch {
    /* ignore */
  }
  authCache = null;
  setStudentId(null);
  window.location.href = "/";
}

function initScanUpload() {
  const form = document.getElementById("scan-upload-form");
  if (!form || form.dataset.bound) return;
  form.dataset.bound = "1";

  const dropZone = document.getElementById("scan-drop-zone");
  const fileInput = document.getElementById("scan-file-input");
  const fileLabel = document.getElementById("scan-file-label");
  const errorEl = document.getElementById("scan-upload-error");
  const results = document.getElementById("scan-results");
  const parsedBox = document.getElementById("scan-parsed");
  const topCareer = document.getElementById("scan-top-career");

  const showFile = (file) => {
    fileLabel.hidden = false;
    fileLabel.textContent = `${file.name} (${formatBytes(file.size)})`;
  };

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) showFile(fileInput.files[0]);
  });

  ["dragenter", "dragover"].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
  });
  ["dragleave", "drop"].forEach((ev) => {
    dropZone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
    });
  });
  dropZone.addEventListener("drop", (e) => {
    const file = e.dataTransfer.files[0];
    if (file) {
      fileInput.files = e.dataTransfer.files;
      showFile(file);
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.hidden = true;
    const id = await needLogin();
    if (!id) return;
    const file = fileInput.files[0];
    if (!file) {
      errorEl.hidden = false;
      errorEl.textContent = "Choose a resume file first.";
      return;
    }
    const btn = document.getElementById("scan-upload-btn");
    btn.disabled = true;
    btn.textContent = "Scanning…";
    const body = new FormData();
    body.append("file", file);
    try {
      const res = await fetch(`/api/students/${id}/resume/upload`, {
        method: "POST",
        credentials: "include",
        body,
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Upload failed");
      authCache = { ...(authCache || {}), resume_scanned: 1, student_id: id };
      const p = data.parsed;
      fill(
        parsedBox,
        `
        <div><dt>Education</dt><dd>${p.education_level}</dd></div>
        <div><dt>Field</dt><dd>${p.field_of_study}</dd></div>
        <div><dt>Skills found</dt><dd>${(p.skills || []).join(", ") || "—"}</dd></div>
        <div><dt>Experience</dt><dd>${p.experience_level}</dd></div>
        <div><dt>Work style</dt><dd>${p.work_style}</dd></div>`
      );
      topCareer.textContent = data.top_career
        ? `Top career match: ${data.top_career}`
        : "Career matches are ready in your dashboard.";
      results.hidden = false;
      form.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      errorEl.hidden = false;
      errorEl.textContent = err.message;
    } finally {
      btn.disabled = false;
      btn.textContent = "Scan resume & build my plan";
    }
  });
}

async function loadResults() {
  if (!document.getElementById("career-list")) return;
  const id = await needScannedProfile();
  if (!id) return;
  const recs = await api(`/api/students/${id}/recommendations`);
  document.getElementById("results-intro").textContent =
    recs.length ? "Ranked from your resume scan. Top match drives your roadmap and interview set." : "Upload your resume to generate matches.";
  fill(
    document.getElementById("career-list"),
    recs
      .map(
        (c) => `
      <article class="card career-card">
        <p class="score">${c.match_score}%</p>
        <h2>${c.title}</h2>
        <p class="muted">${c.category} · ${c.avg_salary} · ${c.outlook}</p>
        <p>${c.description}</p>
        <p><strong>Education fit:</strong> ${c.education_fit}</p>
        <ul>${(c.reasons || []).map((r) => `<li>${r}</li>`).join("")}</ul>
      </article>`
      )
      .join("")
  );

  const gap = await api(`/api/students/${id}/skill-gap`);
  document.getElementById("gap-career").textContent = `Compared with ${gap.career.title}`;
  document.getElementById("gap-bar").style.width = `${gap.match_percent}%`;
  document.getElementById("gap-meta").textContent = `${gap.match_percent}% of listed role skills already on your profile`;
  fill(
    document.getElementById("gap-have"),
    gap.matched.map((s) => `<li class="${s.importance}">${s.name} · ${s.importance}</li>`).join("") || "<li>None of the role skills detected yet</li>"
  );
  fill(
    document.getElementById("gap-missing"),
    gap.missing.map((s) => `<li class="${s.importance}">${s.name} · ${s.importance}</li>`).join("") || "<li>No gaps on this list</li>"
  );

  const projects = await api(`/api/students/${id}/projects`);
  fill(
    document.getElementById("project-list"),
    projects.projects
      .map(
        (p) => `
      <article class="card">
        <p class="eyebrow">${p.difficulty}</p>
        <h3>${p.title}</h3>
        <p>${p.description}</p>
        <p class="muted">${p.skills_used}</p>
        <p><strong>Why it helps:</strong> ${p.outcome}</p>
      </article>`
      )
      .join("")
  );
}

async function loadDashboard() {
  if (!document.getElementById("dash-stats")) return;
  const id = await needScannedProfile();
  if (!id) return;
  const data = await api(`/api/students/${id}/dashboard`);
  const s = data.student;
  document.getElementById("dash-title").textContent = `Welcome back, ${s.name.split(" ")[0]}`;
  document.getElementById("dash-sub").textContent = `${s.education_level} · ${s.field_of_study}`;
  const top = data.recommendations[0];
  fill(
    document.getElementById("dash-stats"),
    `
    <article class="card"><h2>Top match</h2><p class="big">${top ? top.title : "—"}</p><p class="muted">${top ? top.match_score + "% fit" : ""}</p></article>
    <article class="card"><h2>Roadmap</h2><p class="big">${data.roadmap.percent}%</p><p class="muted">${data.roadmap.completed}/${data.roadmap.total} months done</p></article>
    <article class="card"><h2>Resume</h2><p class="big">${data.resume.percent}%</p><p class="muted">${data.resume.completed}/${data.resume.total} checks done</p></article>
    `
  );
  fill(
    document.getElementById("dash-careers"),
    data.recommendations
      .map(
        (c) => `
      <article class="card career-card">
        <h2>${c.title}</h2>
        <p class="muted">${c.category} · ${c.match_score}% match</p>
      </article>`
      )
      .join("")
  );
  fill(
    document.getElementById("dash-profile"),
    `
    <div><dt>Interests</dt><dd>${s.interests}</dd></div>
    <div><dt>Skills</dt><dd>${s.skills}</dd></div>
    <div><dt>Goals</dt><dd>${s.career_goals}</dd></div>
    <div><dt>Work style</dt><dd>${s.work_style}</dd></div>
    `
  );
}

async function loadRoadmap() {
  if (!document.getElementById("road-steps")) return;
  const id = await needScannedProfile();
  if (!id) return;
  const data = await api(`/api/students/${id}/roadmap`);
  document.getElementById("road-title").textContent = `6-month plan: ${data.career.title}`;
  document.getElementById("road-bar").style.width = `${data.percent}%`;
  document.getElementById("road-meta").textContent = `${data.completed} of ${data.total} steps complete`;
  fill(
    document.getElementById("road-steps"),
    data.steps
      .map(
        (step) => `
      <li>
        <span class="month">Month ${step.month_number}</span>
        <div>
          <h2>${step.title}</h2>
          <p>${step.description}</p>
          <p class="muted">Resources: ${step.resources}</p>
          <label class="check-row" style="margin-top:0.6rem">
            <input type="checkbox" data-progress="${step.progress_id}" ${step.completed ? "checked" : ""}>
            <span>Mark this month complete</span>
          </label>
        </div>
      </li>`
      )
      .join("")
  );
  document.getElementById("road-steps").addEventListener("change", async (e) => {
    const box = e.target.closest("input[data-progress]");
    if (!box) return;
    await api(`/api/progress/${box.dataset.progress}`, {
      method: "PATCH",
      body: JSON.stringify({ completed: box.checked }),
    });
    const refreshed = await api(`/api/students/${id}/roadmap`);
    document.getElementById("road-bar").style.width = `${refreshed.percent}%`;
    document.getElementById("road-meta").textContent = `${refreshed.completed} of ${refreshed.total} steps complete`;
  });
}

async function loadResume() {
  if (!document.getElementById("resume-list")) return;
  const id = await needScannedProfile();
  if (!id) return;
  const data = await api(`/api/students/${id}/resume`);
  document.getElementById("resume-bar").style.width = `${data.percent}%`;
  document.getElementById("resume-meta").textContent = `${data.completed} of ${data.total} items complete`;
  fill(
    document.getElementById("resume-list"),
    data.items
      .map(
        (item) => `
      <li>
        <input type="checkbox" data-resume="${item.progress_id}" ${item.completed ? "checked" : ""}>
        <div>
          <strong>${item.title}</strong>
          <p class="muted">${item.section} · ${item.description}</p>
        </div>
      </li>`
      )
      .join("")
  );
  document.getElementById("resume-list").addEventListener("change", async (e) => {
    const box = e.target.closest("input[data-resume]");
    if (!box) return;
    await api(`/api/resume-progress/${box.dataset.resume}`, {
      method: "PATCH",
      body: JSON.stringify({ completed: box.checked }),
    });
    const refreshed = await api(`/api/students/${id}/resume`);
    document.getElementById("resume-bar").style.width = `${refreshed.percent}%`;
    document.getElementById("resume-meta").textContent = `${refreshed.completed} of ${refreshed.total} items complete`;
  });
}

async function loadInterview() {
  if (!document.getElementById("int-list")) return;
  const id = await needScannedProfile();
  if (!id) return;
  const data = await api(`/api/students/${id}/interview`);
  document.getElementById("int-title").textContent = `Interview prep: ${data.career.title}`;
  fill(
    document.getElementById("int-list"),
    data.questions
      .map(
        (q) => `
      <article class="card">
        <span class="q-cat">${q.category}</span>
        <h2>${q.question}</h2>
        <p><strong>How to answer:</strong> ${q.tip}</p>
      </article>`
      )
      .join("")
  );
}

async function initUploadPage() {
  if (!document.getElementById("scan-upload-form")) return;
  await needLogin();
  initScanUpload();
}

document.addEventListener("DOMContentLoaded", async () => {
  const auth = await refreshAuth();
  syncAuthNav(!!auth);

  document.getElementById("nav-logout")?.addEventListener("click", logout);

  const loginForm = document.getElementById("login-form");
  if (loginForm) loginForm.addEventListener("submit", submitLogin);

  const signupForm = document.getElementById("signup-form");
  if (signupForm) signupForm.addEventListener("submit", submitSignup);

  initUploadPage().catch((err) => console.error(err));
  loadResults().catch((err) => console.error(err));
  loadDashboard().catch((err) => console.error(err));
  loadRoadmap().catch((err) => console.error(err));
  loadInterview().catch((err) => console.error(err));
  loadResume().catch((err) => console.error(err));
});

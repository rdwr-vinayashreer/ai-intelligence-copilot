const API_BASE = "";

const profileNames = {};
const profileData = {};

const form = document.getElementById("preferences-form");
const topicsContainer = document.getElementById("topics-container");

const userIdInput = document.getElementById("user-id");
const emailInput = document.getElementById("email");
const timezoneInput = document.getElementById("timezone");
const timeInput = document.getElementById("briefing-time");

const topicCount = document.getElementById("topic-count");
const previewProfile = document.getElementById("preview-profile");
const previewTopics = document.getElementById("preview-topics");
const previewDelivery = document.getElementById("preview-delivery");
const previewEmail = document.getElementById("preview-email");

const successMessage = document.getElementById("success-message");


async function loadProfiles() {
  const response = await fetch(`${API_BASE}/api/v1/profiles`);

  if (!response.ok) {
    throw new Error("Unable to load intelligence profiles.");
  }

  const profiles = await response.json();

  profiles.forEach((profile) => {
    profileNames[profile.id] = profile.name;
    profileData[profile.id] = profile;
  });
}


function getSelectedProfile() {
  return document.querySelector(
    'input[name="profile"]:checked'
  )?.value || "";
}


function formatTime(time) {
  if (!time) return "--:--";

  const [hour, minute] = time.split(":").map(Number);
  const suffix = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;

  return `${displayHour}:${String(minute).padStart(2, "0")} ${suffix}`;
}


function renderTopics(profile) {
  topicsContainer.innerHTML = "";

  const categories = profileData[profile]?.categories || [];

  const topicLabels = {
    models: "Models",
    agentic_ai: "Agentic AI",
    ai_research: "AI Research",
    ai_engineering: "AI Engineering",
    developer_ecosystem: "Developer Ecosystem",
    enterprise_ai: "Enterprise AI",
    ai_security: "AI Security",
    ai_infrastructure: "AI Infrastructure",
    robotics_multimodal: "Robotics & Multimodal"
  };

  categories.forEach((topic) => {
    const wrapper = document.createElement("div");
    wrapper.className = "topic-option";

    const inputId = `topic-${topic}`;

    wrapper.innerHTML = `
      <input
        type="checkbox"
        id="${inputId}"
        name="topics"
        value="${topic}"
      />
      <label for="${inputId}">
        ${topicLabels[topic] || topic}
      </label>
    `;

    topicsContainer.appendChild(wrapper);
  });

  topicsContainer
    .querySelectorAll('input[name="topics"]')
    .forEach((input) => {
      input.addEventListener("change", updatePreview);
    });

  updatePreview();
}


function getSelectedTopics() {
  return Array.from(
    document.querySelectorAll('input[name="topics"]:checked')
  ).map((input) => input.value);
}


function getTopicLabel(value) {
  const labels = {
    models: "Models",
    agentic_ai: "Agentic AI",
    ai_research: "AI Research",
    ai_engineering: "AI Engineering",
    developer_ecosystem: "Developer Ecosystem",
    enterprise_ai: "Enterprise AI",
    ai_security: "AI Security",
    ai_infrastructure: "AI Infrastructure",
    robotics_multimodal: "Robotics & Multimodal"
  };

  return labels[value] || value;
}


function updatePreview() {
  const profile = getSelectedProfile();
  const topics = getSelectedTopics();

  previewProfile.textContent =
    profile ? profileNames[profile] : "Select a profile";

  topicCount.textContent = topics.length;

  previewTopics.innerHTML = "";

  if (topics.length === 0) {
    previewTopics.innerHTML = `
      <span class="empty-tag">No topics selected</span>
    `;
  } else {
    topics.forEach((topic) => {
      const tag = document.createElement("span");
      tag.className = "preview-tag";
      tag.textContent = getTopicLabel(topic);
      previewTopics.appendChild(tag);
    });
  }

  const timezone =
    timezoneInput.options[timezoneInput.selectedIndex]?.text || "IST";

  previewDelivery.textContent =
    `${formatTime(timeInput.value)} · ${timezone.replace(/\s*\(.+\)/, "")}`;

  previewEmail.textContent =
    emailInput.value.trim() || "you@company.com";
}


function clearErrors() {
  document.querySelectorAll(".field-error").forEach((element) => {
    element.textContent = "";
  });

  document.querySelectorAll(".input-error").forEach((element) => {
    element.classList.remove("input-error");
  });
}


function validate() {
  clearErrors();

  let valid = true;

  const userId = userIdInput.value.trim();
  const profile = getSelectedProfile();
  const topics = getSelectedTopics();
  const email = emailInput.value.trim();

  if (!/^[a-zA-Z0-9._-]+$/.test(userId)) {
    document.getElementById("user-id-error").textContent =
      "Enter a valid company user ID.";

    userIdInput.classList.add("input-error");
    valid = false;
  }

  if (!profile) {
    document.getElementById("profile-error").textContent =
      "Select an intelligence profile.";

    valid = false;
  }

  if (topics.length === 0) {
    document.getElementById("topics-error").textContent =
      "Select at least one topic.";

    valid = false;
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    document.getElementById("email-error").textContent =
      "Enter a valid email address.";

    emailInput.classList.add("input-error");
    valid = false;
  }

  return valid;
}


async function savePreferences() {
  const payload = {
    user_id: userIdInput.value.trim(),
    profile: getSelectedProfile(),
    topics: getSelectedTopics(),
    timezone: timezoneInput.value,
    time: timeInput.value,
    delivery: {
      channel: "email",
      destination: emailInput.value.trim()
    }
  };

  const response = await fetch(
    `${API_BASE}/api/v1/users/${encodeURIComponent(payload.user_id)}`,
    {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    }
  );

  const body = await response.json();

  if (!response.ok) {
    const message =
      typeof body.detail === "string"
        ? body.detail
        : body.detail?.message || "Unable to save preferences.";

    throw new Error(message);
  }

  return body;
}


document.querySelectorAll('input[name="profile"]').forEach((input) => {
  input.addEventListener("change", () => {
    renderTopics(input.value);
    successMessage.classList.remove("show");
  });
});


userIdInput.addEventListener("input", updatePreview);
emailInput.addEventListener("input", updatePreview);
timezoneInput.addEventListener("change", updatePreview);
timeInput.addEventListener("change", updatePreview);


form.addEventListener("submit", async (event) => {
  event.preventDefault();

  successMessage.classList.remove("show");

  if (!validate()) {
    return;
  }

  const button = form.querySelector(".primary-button");
  const originalText = button.innerHTML;

  button.disabled = true;
  button.innerHTML = "<span>Saving...</span>";

  try {
    await savePreferences();

    successMessage.querySelector("strong").textContent =
      "Preferences saved";

    successMessage.querySelector("span").textContent =
      "Your briefing configuration is now stored.";

    successMessage.classList.add("show");

  } catch (error) {
    document.getElementById("email-error").textContent =
      error.message;

  } finally {
    button.disabled = false;
    button.innerHTML = originalText;
  }
});


async function initialize() {
  try {
    await loadProfiles();
    updatePreview();
  } catch (error) {
    console.error(error);

    document.getElementById("profile-error").textContent =
      "Unable to load intelligence profiles.";
  }
}


initialize();

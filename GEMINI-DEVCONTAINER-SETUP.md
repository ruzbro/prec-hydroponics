# Gemini CLI Dev Container Setup: The Golden Path

This guide provides a standardized, robust template for configuring any devcontainer project to include the Gemini CLI correctly from the start. Following these steps will prevent the common build and runtime errors associated with this setup.

## Core Principle

The setup is divided between the two main configuration files, with each file responsible for what it does best:

- **`devcontainer.json`:** Manages dev container *features* (like adding Node.js) and commands that must run *after* the container is built and those features are available.
- **`Dockerfile`:** Manages the *base image* setup, such as installing operating system packages (`apt-get`) and language-specific dependencies (like Python's `requirements.txt`).

---

## Step 1: Configure `devcontainer.json`

This is the control center for your dev container's tools. Open `.devcontainer/devcontainer.json` and ensure it contains the following two components.

### 1. Add the Node.js Feature

The Gemini CLI is a Node.js application. We must add the official Node.js feature to install the `npm` command. Pinning to a stable version like `18` is highly recommended.

### 2. Add the `postCreateCommand`

This command runs **after** the container is built and the Node.js feature is installed. This is the correct place to globally install the Gemini CLI using `npm`.

It is also highly recommended to update `npm` itself before installing Gemini, as some base images may have an outdated version that can cause issues.

**Example `devcontainer.json` snippet:**

```json
{
	// ... other settings like "name", "build", etc.

	"features": {
		// ... other existing features (e.g., docker-in-docker)
		"ghcr.io/devcontainers/features/node:1": {
			"version": "18"
		}
	},

	"postCreateCommand": "npm install -g npm && npm install -g @google/gemini-cli",

	// ... other settings like "postStartCommand", "customizations", etc.
}
```

---

## Step 2: Clean Up the `Dockerfile`

Open your project's `Dockerfile` and ensure it is **only** responsible for OS and language setup. It should **not** contain any commands related to installing `nodejs`, `npm`, or the `gemini` CLI directly.

**Example of a clean `Dockerfile` section:**

```dockerfile
# Install OS packages and Python dependencies
RUN apt-get update && apt-get install -y libpq-dev python3-dev gcc
RUN python3 -m pip install --no-cache-dir --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# --- DO NOT add "npm install" or "gemini" commands here. ---
# --- DO NOT add "ENV PATH" commands for gemini here.      ---
```

---

## Step 3: Verify Project Dependencies (If Applicable)

For Python projects, ensure that your `requirements.txt` file contains the Python SDK for the Gemini API, but **not** the broken `[cli]` extra.

- **Correct:** `google-generativeai`
- **Incorrect:** `google-generativeai[cli]`

---

## Workflow for Upgrading a Project

1.  **Copy this file** (`GEMINI-DEVCONTAINER-SETUP.md`) into the root of the target project.
2.  **Open the project** in your IDE.
3.  **Edit `.devcontainer/devcontainer.json`** to add the `node` feature and the `postCreateCommand` as described in Step 1.
4.  **Edit the `Dockerfile`** to remove any incorrect `npm` or `gemini` installation attempts, as described in Step 2.
5.  **Check `requirements.txt`** (if it exists) as described in Step 3.
6.  **Rebuild the Container** using your IDE's command palette.

After the rebuild, the `gemini` command will be available in your IDE's terminal session.